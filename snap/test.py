import policies
import networkx
import stateful
import pickle

def construct_graph(file):
    file = open(file, "r")
    node_name = {}
    tmp = []
    graph = networkx.DiGraph()
    for line in file:
        line = line.strip()
        tmp.append(line)
    links_index = tmp.index('links')
    tmp_node = tmp[1:links_index]
    tmp_link = tmp[links_index+1:]
    for node in tmp_node:
        num_name = node.split(' ')






def construct_traffic_req(file):
    pass




if __name__ == "__main__":
    graph_file = r"..\topo\synth\10\topo.txt"
    demands = r"..\topo\synth\10\demands.txt"

    graph_demo = construct_graph(graph_file)
    traffic_req = construct_traffic_req(demands)
    print "================policy======================="
    print policies.get_dns_tunnel_policy([1,2,3,4,5,6])
    print "================assumption==================="
    print policies.get_route_and_assump_policy([1,2,3,4,5,6])[1]
    print "================routing======================"
    print policies.get_route_and_assump_policy([1,2,3,4,5,6])[0]
    stateful.compile_to_req(policies.get_dns_amplification_policy([1,2,3,4,5,6]),policies.get_route_and_assump_policy([1,2,3,4,5,6])[1],
                   [1,2,3,4,5,6], graph_demo, traffic_req)