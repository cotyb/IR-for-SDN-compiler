import fsm_2_17
import SA
import pickle
import os

def fsm2SA(fsm):
    '''
    change mi's fsm to my SA
    :param fsm: a instance of fsm obj
    :return: the sa
    '''
    alphabet = fsm.alphabet
    states = fsm.states
    initial = fsm.initial
    finals = fsm.finals
    maps = fsm.map

    # to init a sa, we need get the start node, end node, edges.
    start = SA.Node(initial)
    end = SA.Node(finals.pop())

    # init sa
    sa = SA.SA(start, end)

    # get all edges from fsm.map, and add edge into sa with function add_edge_indirect
    for edge_start, value1 in maps.items():
        print value1
        for edge_action, value2 in value1.items():
            for edge_end, value3 in value2.items():
                # count denotes the number of (guard, update) tuple
                count = len(value3) / 2
                for dummy_i in range(count):
                    edge_guard, edge_update = value3[2*dummy_i], value3[2*dummy_i + 1]
                    sa.add_edge_indirect(SA.Node(int(edge_start)), SA.Node(int(edge_end)), edge_guard, edge_action, edge_update)
    return sa



Merlin_sa_path = "./Merlin_sa/"
SNAP_sa_path = "./SNAP_sa/"

def load_pickle(f):
    f = open(f, "r")
    res = pickle.loads(f.read())
    f.close()
    return res


if __name__ == "__main__":
    files = os.listdir(Merlin_sa_path)
    Merlin_all_sa = []
    for file in files:
        Merlin_all_sa.append(load_pickle(Merlin_sa_path + file))
    SNAP_sa = load_pickle(SNAP_sa_path + "SNAP_sa")
    alphabet, states, initial, finals, map = SNAP_sa.to_fsm()
    print alphabet, states, initial, finals, map
    SNAP_fsm = fsm_2_17.fsm(alphabet=alphabet, states=states, initial=initial, finals=finals, map=map)
    Merlin_fsm = []
    for sa in Merlin_all_sa:
        a, s, i, f, m = sa.to_fsm()
        # fsm = [a, s, i, f, m]
        # print a, s, i, f
        # print m
        Merlin_fsm.append(fsm_2_17.fsm(alphabet=a, states=s, initial=i, finals=f, map=m))
    Merlin_merged_fsm = Merlin_fsm[0]
    for fsm in Merlin_fsm[1:]:
        Merlin_merged_fsm.intersection(fsm)

    result = SNAP_fsm.union(Merlin_merged_fsm)
    # change fsm to SA
    sa = fsm2SA(result)
    sa.draw_sa("result")









