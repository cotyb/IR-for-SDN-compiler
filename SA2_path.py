import networkx as nx
import matplotlib.pyplot as plt


SNAP_network_match_fields = ["srcip", "dstip", "srcport", "dstport"]
Merlin_network_match_fields = ["ip.src", "ip.dst", "tcp.dst", "tcp.src"]


def construct_graph(file):
    file = open(file, "r")
    node_name = {}
    tmp = []
    graph = nx.DiGraph()
    for line in file:
        line = line.strip()
        tmp.append(line)
    links_index = tmp.index('links')
    tmp_node = tmp[1:links_index]
    tmp_link = tmp[links_index+1:]
    for link in tmp_link:
        start, end, weight = link.split(' ')
        # print start, end, weight
        graph.add_edge(int(start), int(end), cap=int(weight))
    return graph

def construct_traffic_req(file):
    pass


def is_path_meet_sa(sa, path):
    '''
    given a path and a sa, verify whether the path meets the sa
    :param sa: sa, SA objetc
    :param path: a list, like [1,2,3]
    :return: false or true
    '''
    pass

if __name__ == "__main__":
    graph_file = r".\topo\synth\10\topo.txt"
    demands = r".\topo\synth\10\demands.txt"

    graph = construct_graph(graph_file)
    # traffic_req = construct_traffic_req(demands)
    print graph.nodes()
    print graph.edges()
    path = nx.all_simple_paths(graph, 1, 9)
    for p in path:
        print p
    for edge in graph.edges():
        print edge