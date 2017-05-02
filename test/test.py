import SA
import networkx
from gurobipy import *
import copy
import matplotlib.pyplot as plt

# construct topology and compute all simple path
topo = networkx.Graph()
# topo.add_edges_from([('i','a'),('i','c'),('i','b'),('a','d'),('a','z'),('c','z'),('b','z'),('b','f'),('z','d'),('z','j'),('z','f'),('d','g'),('j','g'),('f','g')])
topo.add_edge('i','a',{'cc':100})
topo.add_edge('i','c',{'cc':100})
topo.add_edge('i','b',{'cc':100})
topo.add_edge('a','d',{'cc':100})
topo.add_edge('a','z',{'cc':100})
topo.add_edge('c','z',{'cc':100})
topo.add_edge('b','z',{'cc':100})
topo.add_edge('b','f',{'cc':100})
topo.add_edge('z','d',{'cc':100})
topo.add_edge('z','j',{'cc':100})
topo.add_edge('z','f',{'cc':100})
topo.add_edge('d','g',{'cc':100})
topo.add_edge('j','g',{'cc':100})
topo.add_edge('f','g',{'cc':100})
# pos = networkx.spring_layout(topo, iterations=5000)
# plt.figure()
# networkx.draw(topo, pos,with_labels=True)
# plt.show()
all_path = networkx.all_simple_paths(topo, 'i','g')

print topo.edge['z']['f']['cc']

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
# print sub_sa
sub_sa_1 = sub_sa[sub_sa.keys()[0]]
sub_sa_2 = sub_sa[sub_sa.keys()[1]]

sub_sa_1.sa_str()

# sub_sa_2.sa_str()
all_path = [x for x in all_path]
sa_paths = {}
sa_rescource = {sub_sa_1:70, sub_sa_2:50}
old_path = copy.deepcopy(all_path)
for key in sub_sa:
    sa_paths[sub_sa[key]] = []
    for path in all_path:
        if sub_sa[key].accepts_with_state(path, sub_sa[key].start, sub_sa[key].state_configuration):
            sa_paths[sub_sa[key]].append(path)
    all_path = copy.deepcopy(old_path)

print sa_paths



def mip(sa_path, topo, sa_resources):
    m = Model('path selection')

    R = {}
    sa_count = 0
    var_path = {}
    sa_num = {}
    num_sa = {}
    for sa in sa_path:
        path_count = 0
        sa_num[sa] = sa_count
        num_sa[sa_count] = sa
        for path in sa_path[sa]:
            R[sa_count, path_count] = m.addVar(vtype=GRB.BINARY, name='X_%s_%s' %(sa_count, path_count))
            var_path[sa_count, path_count] = path
            path_count += 1
        sa_count += 1

    m.update()



    # constraints

    # one sa can only select one path
    for sa in sa_path:
        vs = [R[sa_count, path_count] for (sa_count, path_count) in R if sa_count == sa_num[sa]]
        m.addConstr(quicksum(vs), GRB.EQUAL, 1)

    # objective
    object = LinExpr()
    var_obj = []
    c_obj = []

    for (i, j) in tuplelist(topo.edges()):
        for tmp in var_path:
            path = var_path[tmp]
            for dummy_i in range(len(path)-1):
                if path[dummy_i] == i:
                    if path[dummy_i+1] == j:
                        var_obj.append(R[tmp[0], tmp[1]])
                        c_obj.append(sa_rescource[num_sa[tmp[0]]])
                    else:
                        break
    object.addTerms(c_obj, var_obj)
    m.setObjective(object, GRB.MINIMIZE)

    for (i, j) in tuplelist(topo.edges()):
        constr = LinExpr()
        var1 = []
        c = []
        for tmp in var_path:
            path = var_path[tmp]
            for dummy_i in range(len(path)-1):
                if path[dummy_i] == i:
                    if path[dummy_i+1] == j:
                        var1.append(R[tmp[0], tmp[1]])
                        c.append(sa_rescource[num_sa[tmp[0]]])
                    else:
                        break
        constr.addTerms(c, var1)
        m.addConstr(constr, GRB.LESS_EQUAL, topo.edge[i][j]['cc'])


    m.optimize()
    for tmp in R:
        if R[tmp].X == 1:
            print var_path[tmp]




    return m, R


m, r = mip(sa_paths, topo, sa_rescource)




