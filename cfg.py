
import heapq
class BustlePCFG:
    __instance = None

    @staticmethod
    def get_instance():
        if BustlePCFG.__instance is None:
            raise Exception("Need to initialize the grammar first")

        return BustlePCFG.__instance

    @staticmethod
    def initialize(operations, string_literals, integer_literals, boolean_literals, string_variables,
                   integer_variables):
        BustlePCFG(operations, string_literals, integer_literals,
                   boolean_literals, string_variables, integer_variables)

    def __init__(self, operations, string_literals, integer_literals, boolean_literals, string_variables,
                 integer_variables):
        self.uniform_grammar = {}
        self.grammar = {}
        self.number_rules = len(operations) + len(string_literals) + len(integer_literals) + len(
            boolean_literals) + len(string_variables) + len(integer_variables)
        self.program_id = 0
        BustlePCFG.__instance = self

    def get_cost(self, p):
        return 1

    def get_cost_by_name(self, name):
        return 1

    def get_program_id(self):
        self.program_id += 1
        return self.program_id


class SynthesisProblem:
    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state
        self.goal_state = goal_state

    def goal_test(self, state):
        return state == self.goal_state

    def get_neighbors(self, state):

        neighbors = []

        # Split the state into individual components based on grammar structure
        components = state.split()

        # Iterate over each component and generate neighbors
        for i in range(len(components)):
            neighbor = components.copy()

            if neighbor[i] == "ntString":
                neighbor[i] = '"ntInt "'
                neighbors.append(" ".join(neighbor))

        return neighbors

    def transition_cost(self, state, neighbor):
        return 1

    def heuristic(self, state):
        return 1


class Node:
    def __init__(self, state, parent=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        # Define comparison for priority queue based on total cost
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

def astar_search(problem):
    # Initialize start node
    start_node = Node(problem.initial_state)

    # Priority queue to store nodes to explore
    open_set = []
    heapq.heappush(open_set, start_node)

    # Set to store explored nodes
    closed_set = set()

    while open_set:
        current_node = heapq.heappop(open_set)

        if problem.goal_test(current_node.state):
            return current_node  # Goal reached

        closed_set.add(current_node.state)

        for neighbor in problem.get_neighbors(current_node.state):
            if neighbor not in closed_set:
                cost = current_node.cost + problem.transition_cost(current_node.state, neighbor)
                heuristic = problem.heuristic(neighbor)
                new_node = Node(neighbor, parent=current_node, cost=cost, heuristic=heuristic)

                heapq.heappush(open_set, new_node)

    return None  # No solution found
