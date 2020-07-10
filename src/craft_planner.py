import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].

        # Iterates through consumables and checks to see if inventory has enough
        if 'Consumes' in rule:
            for consumedItem in rule['Consumes']:
                if state[consumedItem] - rule['Consumes'][consumedItem] < 0:
                    return False # Need more items than currently have

        # Iterates through required items and checks to see if exists in inventory
        if 'Requires' in rule:
            for requiredItem in rule['Requires']:
                if not state[requiredItem]:
                    return False # Required item not found 

        # If nothing returned means passes consume and require check
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].

        next_state = state.copy()
        
        # Iterates through produces and adds the value to the current state
        if 'Produces' in rule:
            for produce in rule['Produces']:
                next_state[produce] = state[produce] + rule['Produces'][produce]

        # Iterates though consumes and subtracts the number of items needed from current state
        if 'Consumes' in rule:
            for consume in rule['Consumes']:
                next_state[consume] = state[consume] - rule['Consumes'][consume]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.

        # Goes through goals and if goal is not reached return false otherwise return true
        for singleGoal in goal:
            if state[singleGoal] < goal[singleGoal]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    tools = ['bench', 'wooden_pickaxe', 'wooden_axe', 'stone_axe', 'stone_pickaxe', 'iron_pickaxe', 'iron_axe', 'furnace']
    current_state = state.copy()

    for tool in tools:
        if state[tool] > 1:
            return inf
        return 0

    # for item in 


    return 0


def search(graph, state, is_goal, limit, heuristic):

    start_time = time()
    queue = [(0, state)]
    cost_so_far = {}
    came_from = {}
    actions = {}
    came_from[state] = None
    cost_so_far[state] = 0
    actions[state] = None
    path = []
    length = 0

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit:
        current_cost, current_state = heappop(queue)

        if is_goal(current_state):
            link = (current_state, actions[current_state])
            path.append(link)
            previous_state = current_state
            current_state = came_from[current_state]

            while (current_state is not None):
                length += 1
                link = (current_state, actions[current_state])
                path.append(link)
                current_state = came_from[current_state]
            # print('states visited: ' + str(len(visited_states)))
            print(time() - start_time, "seconds.")
            print("Length is " + str(length))
            print("Cost: " + str(cost_so_far[previous_state]))
            path.reverse()
            return path


        for adj_action, adj_state, adj_cost in graph(current_state):
            new_cost = cost_so_far[current_state] + adj_cost
            if adj_state not in cost_so_far or new_cost < cost_so_far[adj_state]:
                cost_so_far[adj_state] = new_cost
                priority = new_cost + heuristic(adj_state)
                actions[adj_state] = adj_action
                heappush(queue, (priority, adj_state))
                came_from[adj_state] = current_state


    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])
    #
    # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    #
    # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])
    #
    # Dict of crafting recipes (each is a dict):
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
