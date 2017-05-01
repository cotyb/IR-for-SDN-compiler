import SA
import networkx
import copy
import matplotlib.pyplot as plt

# construct topology and compute all simple path
topo = networkx.Graph()
topo.add_edges_from([('i','a'),('i','c'),('i','b'),('a','d'),('a','z'),('c','z'),('b','z'),('b','f'),('z','d'),('z','j'),('z','f'),('d','g'),('j','g'),('f','g')])
# pos = networkx.spring_layout(topo, iterations=5000)
# plt.figure()
# networkx.draw(topo, pos,with_labels=True)
# plt.show()
all_path = networkx.all_simple_paths(topo, 'i','g')


# construct sa
sa = SA.SA(SA.Node(1),SA.Node(5))
sa.add_edge_indirect(SA.Node(1),SA.Node(1),'','FWD(.)','')
sa.add_edge_indirect(SA.Node(1),SA.Node(3)," srcip='192.168.1.1' && dstip='192.168.1.3' ",'FWD(a)','')
sa.add_edge_indirect(SA.Node(1),SA.Node(3)," srcip='192.168.1.1' && dstip='192.168.1.3' ",'FWD(b)','')
sa.add_edge_indirect(SA.Node(1),SA.Node(2)," srcip='192.168.1.2' && dstip='192.168.1.3' ",'FWD(z)','')
sa.add_edge_indirect(SA.Node(3),SA.Node(4),"",'FWD(.) && dpi','')
sa.add_edge_indirect(SA.Node(2),SA.Node(5),"",'FWD(e)','')
sa.add_edge_indirect(SA.Node(2),SA.Node(2),"",'FWD(.)','')
sa.add_edge_indirect(SA.Node(4),SA.Node(4),"h<2",'FWD(.)','h+=1')
sa.add_edge_indirect(SA.Node(4),SA.Node(5),"h<2",'FWD(e)','')
sa.add_state_configuration('h',0)


# sa.sa_str()
sub_sa = sa.divide_sa()
sub_sa_1 = sub_sa[sub_sa.keys()[0]]
sub_sa_2 = sub_sa[sub_sa.keys()[1]]
sub_sa_1.sa_str()
print "********"
sub_sa_2.sa_str()

count = 0
for path in all_path:
    if sub_sa_2.accepts_with_state(path, sub_sa_2.start, sub_sa_2.state_configuration):
        count += 1
        print path
print count