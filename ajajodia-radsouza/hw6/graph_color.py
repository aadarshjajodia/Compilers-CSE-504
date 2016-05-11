colors = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']

#states = ['t0', 't1', 't2', 't3', 't4']

#neighbors = {}
#neighbors['t1'] = ['t2']
#neighbors['t2'] = ['t1', 't3']
#neighbors['t3'] = ['t2']

colors_of_states = {}

def promising(state, color, neighbors):
    if neighbors.get(state) == None:
        return True
    for neighbor in neighbors.get(state): 
        color_of_neighbor = colors_of_states.get(neighbor)
        if color_of_neighbor == color:
            return False

    return True

def get_color_for_state(state, neighbors):
    for color in colors:
        if promising(state, color, neighbors):
            return color

def graph_color(states, neighbors):
    for state in states:
        colors_of_states[state] = get_color_for_state(state, neighbors)
        if colors_of_states[state] == None:
            return None
    return colors_of_states