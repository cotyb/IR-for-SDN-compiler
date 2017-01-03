import policies
import networkx
import stateful

def construct_graph(graph, file):
    file = open(file)
    for line in file:
        print line

def construct_traffic_req(traffic_req, file):
    pass




if __name__ == "__main__":
    graph_demo = networkx.DiGraph()
    graph_demo.add_node()
    traffic_req = {}
    # graph_file = "\topo\synth\10\topo.txt"
    # demands = "\topo\synth\10\demands.txt"
    # construct_graph(graph_demo, graph_file)
    # construct_traffic_req()
    print "================policy======================="
    print policies.get_dns_tunnel_policy([1,2,3,4,5,6])
    print "================assumption==================="
    print policies.get_route_and_assump_policy([1,2,3,4,5,6])[1]
    print "================routing======================"
    print policies.get_route_and_assump_policy([1,2,3,4,5,6])[0]
    stateful.compile_to_req(policies.get_dns_amplification_policy([1,2,3,4,5,6]),policies.get_route_and_assump_policy([1,2,3,4,5,6])[1],
                   [1,2,3,4,5,6], graph_demo, traffic_req)