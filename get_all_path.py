import networkx
import matplotlib.pyplot as plt
topo = networkx.Graph()
topo.add_edges_from([('i','a'),('i','c'),('i','b'),('a','d'),('a','z'),('c','z'),('b','z'),('b','f'),('z','d'),('z','e'),('z','f'),('d','g'),('e','g'),('f','g')])

for path in networkx.all_simple_paths(topo, 'i','g'):
    print path

print topo.number_of_nodes()
print topo.number_of_edges()
print topo.edges()

