
import subprocess
from pickle import load, dump
import logging
import time
import os
import argparse



parser = argparse.ArgumentParser()
parser.add_argument('--n_clusters',type=int)
args = parser.parse_args()
args_dict = vars(args)
file_extend = "_".join(["{}-{}".format(k,args_dict[k]) for k in args_dict])
LOG_FILE_NAME = f'result_time_{file_extend}.log'

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=LOG_FILE_NAME,
    filemode='a',
)


TRAIN_PATH = 'benchmarks/string/train/'
TEST_PATH = 'benchmarks/string/test/'


command = f'cd ..;python run_data_processing.py --n_clusters {args.n_clusters}'
logging.info('START CLUSTERING')
result = subprocess.run(command,capture_output=True, check=True,shell=True)
logging.info('FINSISH CLUSTERING')
print('finished clustering')
with open(f'../pickle_res/processed_data_cluster_{args.n_clusters}.pickle','rb') as f:
    d = load(f)

d_rev = {}
for k in d:
    key = d[k][-1]
    if key in d_rev:
        d_rev[key].append(k)
    else:
        d_rev[key] = [k]



db = {}
for k in d_rev:
    train,test =[],[]
    for file_name in d_rev[k]:
        if os.path.isfile(TRAIN_PATH+f'{file_name}.sl'):
            train.append(file_name)
        else:
            test.append(file_name)
    db[f'{k}-train'] = train
    db[f'{k}-test'] = test


phog_learner_command = "bin/run_phog_learner phog_str_{} {}"
for k in d_rev:
    files = " ".join(list(map(lambda x:f'{TRAIN_PATH}{x}.sl' ,db['{}-train'.format(k)])))
    command = phog_learner_command.format(f"{k}_n_clusters_{args.n_clusters}",files)
    ret = subprocess.run(command, capture_output=True, shell=True)
    number_of_training_data = len(db['{}-train'.format(k)])
    logging.info(f'cluster {k} is done with {number_of_training_data} training data')
logging.info('TRAINING DONE')

from timeit import timeit
from tqdm import tqdm
cluster_test_time = {}
cluster_output = {}
phog_guide_command = "time timeout 3m bin/run_with_new_phog {} {} {}" 

small_problems = ['exceljet1','exceljet4','exceljet3','stackoverflow4','stackoverflow1','stackoverflow3'
                  ,'stackoverflow8','stackoverflow5','stackoverflow9','phone-5','phone-5-long',
                  'phone-5-long-repeat','phone-5-short','phone-6','phone-6-long',
                  'phone-6-long-repeat','phone-6-short','phone-7','phone-7-long',
                  'phone-7-long-repeat','phone-7-short']
cluster_threshold = 10
logging.info('----------- Testing Start ----------------')
for k in d_rev:
    grammar_cluster = f"phog_str_{k}_n_clusters_{args.n_clusters}"
    grammar_all = "phog_str3all_train"

    test_files = list(map(lambda x:f'{TEST_PATH}{x}.sl' ,db['{}-test'.format(k)]))
    cluster_test_time[k] = []
    cluster_output[k] = []
    logging.info(f"Testing CLuster {k}")
    if len(db['{}-train'.format(k)])<cluster_threshold:
        logging.info(f'Skipping Cluster {k}')
    else:
        for t in tqdm(test_files):
            if t.split('/')[-1][:-3] not in small_problems:
                continue
            command = phog_guide_command.format(grammar_cluster,LOG_FILE_NAME,t)
            
            cluster_time = subprocess.run(command,capture_output=True, shell=True)
            command = phog_guide_command.format(grammar_all,LOG_FILE_NAME,t)
            all_phog_time = subprocess.run(command, capture_output=True, shell=True)
            cluster_test_time[k].append((t,cluster_time.stderr.decode(),all_phog_time.stderr.decode()))
            cluster_output[k].append((t,cluster_time.stdout.decode(),all_phog_time.stdout.decode()))

for k in cluster_test_time:
    all_time = []
    if cluster_test_time[k]!=[]:
        for p in cluster_test_time[k]:
            all_time.append(p[1])
            logging.info(p[0])
            logging.info(p[1])
            logging.info(p[2])
            logging.info('------------')

with open(f'cluster_{args.n_clusters}_time_info.pkl' ,'wb') as f:
    dump(cluster_test_time,f)

logging.info('---------- FINISHED TESTING-------------')

