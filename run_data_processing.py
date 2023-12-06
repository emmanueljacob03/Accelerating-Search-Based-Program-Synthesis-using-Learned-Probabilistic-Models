# this is run_data_processing.py file:
    
import os
from sygus_parser import StrParser
from property_signatures import compute_property_sig, property_signatures_to_cluster_ids
from utils import PATH_TO_STR_BENCHMARKS
import pickle
import json
import numpy as np
import argparse

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='testlogs.txt',
    filemode='a',
)

def prop_sig_to_str(prop_sig):
    return ''.join(str(x) for x in prop_sig)

def str_to_prop_sig(str_in):
    return [int(s) for s in str_in]

def dict_to_jsonstr(dict_in):
    return json.dumps(dict_in)

def jsonstr_to_dict(jsonstr):
    return json.loads(jsonstr)

def inout_list_to_str(inout_list):
    return ','.join([dict_to_jsonstr(e) for e in inout_list])

def main(n_cluster):
    logging.info(f"number of cluster {n_cluster}")
    '''
    problem -> (inout_dicts, prop_sig, cluster_id)
    '''
    data_dict = {}
    property_sigs_X = []
    benchmark_list = []
    in_out_examples_list = []
    

    benchmark_file_list = os.listdir(PATH_TO_STR_BENCHMARKS)
    for benchmark in benchmark_file_list:
        print("benchmark: ", benchmark)
        specification_parser = StrParser(benchmark)
        specifications = specification_parser.parse()

        string_variables = specifications[0]
        string_literals = specifications[1]
        integer_variables = specifications[2]
        integer_literals = specifications[3]
        input_output_examples = specifications[4]

        print("string_variables", string_variables)
        print("string_literals", string_literals)
        print("integer_variables", integer_variables)
        print("integer_literals", integer_literals)

        print("input_output_examples", input_output_examples)

        ps = compute_property_sig(input_output_dicts_list=input_output_examples,
                             string_variables_list=string_variables,
                             integer_variables_list=integer_variables)
        print(ps)
        print(len(ps))


        property_sigs_X.append(ps)
        benchmark_list.append(os.path.splitext(benchmark)[0])
        in_out_examples_list.append(input_output_examples)

    ps_arr = np.array(property_sigs_X)
    cluster_ids = property_signatures_to_cluster_ids(ps_arr, n_components=0.99, n_clusters=n_cluster)

    for benchmark, in_out, ps, c_id in zip(benchmark_list, in_out_examples_list, property_sigs_X, cluster_ids):
        data_dict.update({benchmark: (in_out, ps, c_id)})


    # Specify the output folder
    output_folder="pickle_res"
    output_folder_path = os.path.join(os.getcwd(), output_folder)
    os.makedirs(output_folder_path, exist_ok=True)

    # Construct the file name with the specified number of clusters
    f_name = f"processed_data_cluster_{n_cluster}.pickle"
    f_path = os.path.join(output_folder_path, f_name)
    
    with open(f_path, 'wb') as file:
        pickle.dump(data_dict, file)
    
    print("Saved input out examples, property signatures and cluster_ids in", f_name)


    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_clusters',type=int,default=5)
    args = parser.parse_args()
    main(args.n_clusters)

