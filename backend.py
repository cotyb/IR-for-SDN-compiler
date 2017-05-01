import networkx as nx
from gurobipy import *

def construct_topo():
    topo = nx.Graph()
    topo.add_edges_from([('i','a'),('i','c'),('i','b'),('a','d'),('a','z'),('c','z'),('b','z'),('b','f'),('z','d'),('z','e'),('z','f'),('d','g'),('e','g'),('f','g')])
    return topo

def mip(topo, start, end, global_constrain, all_sub_sa):
    all_path =nx.all_simple_paths(topo, start, end)
    sa_topo = {}
    for sa in all_sub_sa:
        sa_topo[sa] = []
        for path in all_path:
            if sa.accepts_with_state(path, sa.start, sa.state_configuration):
                sa_topo[sa].append(path)
