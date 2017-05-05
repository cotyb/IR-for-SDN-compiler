# -*- coding: utf-8 -*-

import SA
import networkx as nx
from gurobipy import *
import copy
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time
import random
import numpy as np

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def construct_topo_from_snap_topo(topo_txt):
    topo = nx.Graph()
    for edge in topo_txt.readlines():
        # print edge
        start, end = edge.split(' ')[0], edge.split(' ')[1]
        # print start, end
        topo.add_edge(start, end, {'cc':100})
    return topo

def draw_3d(x, y, z):
    ax=plt.subplot(111,projection='3d') #创建一个三维的绘图工程

    #将数据点分成三部分画，在颜色上有区分度
    ax.scatter(x, y, z,c='b') #绘制数据点
    # ax.scatter(x[1000:4000],y[1000:4000],z[1000:4000],c='r')
    # ax.scatter(x[4000:],y[4000:],z[4000:],c='g')

    ax.set_zlabel('Time/s') #坐标轴
    ax.set_ylabel('Ingress switch')
    ax.set_xlabel('Egress switch')
    plt.show()
# construct topology and compute all simple path
# topo = nx.Graph()
# topo.add_edges_from([('i','a'),('i','c'),('i','b'),('a','d'),('a','z'),('c','z'),('b','z'),('b','f'),('z','d'),('z','j'),('z','f'),('d','g'),('j','g'),('f','g')])
# topo.add_edge('i','a',{'cc':100})
# topo.add_edge('i','c',{'cc':100})
# topo.add_edge('i','b',{'cc':100})
# topo.add_edge('a','d',{'cc':100})
# topo.add_edge('a','z',{'cc':100})
# topo.add_edge('c','z',{'cc':100})
# topo.add_edge('b','z',{'cc':100})
# topo.add_edge('b','f',{'cc':100})
# topo.add_edge('z','d',{'cc':100})
# topo.add_edge('z','j',{'cc':100})
# topo.add_edge('z','f',{'cc':100})
# topo.add_edge('d','g',{'cc':100})
# topo.add_edge('j','g',{'cc':100})
# topo.add_edge('f','g',{'cc':100})

def draw_topo(topo):
    pos = nx.spring_layout(topo)
    plt.figure()
    nx.draw(topo, pos,with_labels=True)
    plt.show()

def last_two_edge(sa, count_1, count_2):
    # sa.add_edge_indirect(SA.Node(1),SA.Node(count_2)," srcip='192.168.1.2' && dstip='192.168.1.3' ",'FWD(21)','')
    # sa.add_edge_indirect(SA.Node(count_1),SA.Node(4),"",'FWD(.) && dpi','')
    edge1 = SA.Edge(SA.Node(1),SA.Node(count_2)," srcip='192.168.1.2' && dstip='192.168.1.3' ",'FWD(21)','')
    sa.add_edge_direct(edge1)
    edge2 = SA.Edge(SA.Node(count_1),SA.Node(4),"",'FWD(.) && dpi','')
    sa.add_edge_direct(edge2)

    return sa, edge1, edge2

def construct_sa():
    sa = SA.SA(SA.Node(1),SA.Node(5))
    sa.add_edge_indirect(SA.Node(1),SA.Node(1),'','FWD(.)','')
    sa.add_edge_indirect(SA.Node(1),SA.Node(3)," srcip='192.168.1.1' && dstip='192.168.1.3' ",'FWD(19)','')
    sa.add_edge_indirect(SA.Node(1),SA.Node(3)," srcip='192.168.1.1' && dstip='192.168.1.3' ",'FWD(20)','')
    # sa.add_edge_indirect(SA.Node(1),SA.Node(2)," srcip='192.168.1.2' && dstip='192.168.1.3' ",'FWD(21)','')
    # sa.add_edge_indirect(SA.Node(3),SA.Node(4),"",'FWD(.) && dpi','')

    sa.add_edge_indirect(SA.Node(2),SA.Node(5),"",'FWD(e)','')
    sa.add_edge_indirect(SA.Node(2),SA.Node(2),"",'FWD(.)','')
    sa.add_edge_indirect(SA.Node(4),SA.Node(4),"h<3",'FWD(.)','h+=1')
    sa.add_edge_indirect(SA.Node(4),SA.Node(5),"h<3",'FWD(e)','')
    sa.add_state_configuration('h',0)
    sa.add_edge_indirect(SA.Node(3),SA.Node(7),"",'FWD(20)','')
    sa.add_edge_indirect(SA.Node(1000),SA.Node(2),"",'FWD(20)','')
    return sa

# construct sa
def construct_sa_random(sa, num_of_edges, count_1, count_2):


    sa.add_edge_indirect(SA.Node(count_1-1),SA.Node(count_1),"",'FWD(20)','')
    sa.add_edge_indirect(SA.Node(count_2),SA.Node(count_2-1),"",'FWD(20)','')
    return sa

def path_match_sa(sa, all_path):
    sub_sa = sa.divide_sa()
    # print sub_sa
    sub_sa_1 = sub_sa[sub_sa.keys()[0]]
    sub_sa_2 = sub_sa[sub_sa.keys()[1]]

    sa_paths = {}
    sa_rescource = {sub_sa_1:70, sub_sa_2:50}
    old_path = copy.deepcopy(all_path)
    for key in sub_sa:
        # sub_sa[key].draw_sa("result1")
        sa_paths[sub_sa[key]] = []
        for path in all_path:
            if sub_sa[key].accepts_with_state(path, sub_sa[key].start, sub_sa[key].state_configuration):
                sa_paths[sub_sa[key]].append(path)
        all_path = copy.deepcopy(old_path)

    return sa_paths, sa_rescource


def mip(sa_path, topo, sa_resource):
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
                        c_obj.append(sa_resource[num_sa[tmp[0]]])
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
                        c.append(sa_resource[num_sa[tmp[0]]])
                    else:
                        break
        constr.addTerms(c, var1)
        m.addConstr(constr, GRB.LESS_EQUAL, topo.edge[i][j]['cc'])


    m.optimize()
    # for tmp in R:
    #     if R[tmp].X == 1:
    #         print var_path[tmp]
    return m, R

def test():
    # x = np.linspace(1, 101)
    # y = np.linspace(0, 0.1)
    plt.style.use('ggplot')
    plt.xlabel("SA中边的个数", fontsize='xx-large')
    plt.ylabel("时间/s", fontsize='xx-large')
    # plt.title("Time and the num of edges of SA")
    topo_file = open("topo.txt","r")
    topo = construct_topo_from_snap_topo(topo_file)
    count_1 = 7
    count_2 = 1000
    sa = construct_sa()
    X, Y = [], []
    for i in range(0, 100):
        count_1 += 1
        count_2 += 1
        sa = construct_sa_random(sa, i, count_1,count_2)
        sa, edge1, edge2 = last_two_edge(sa, count_1, count_2)
        # sa.draw_sa("result")
        # print "waiting...%s...%s" %(100.0 * count/17/16, count)
        c_s = time.time()
        all_path = nx.all_simple_paths(topo, '10', '8')
        all_path = [x for x in all_path]
        # 随机抽取部分路径
        all_path = random.sample(all_path, len(all_path)/100)
        sa_paths, sa_rescource = path_match_sa(sa, all_path)

        m, r = mip(sa_paths, topo, sa_rescource)
        using_time = time.time() - c_s

        plt.scatter(len(sa.edges),using_time)
        X.append(len(sa.edges))
        Y.append(using_time)
        # sa.del_edge(edge1)
        # sa.del_edge(edge2)
        # plt.plot(x, using_time)
        # plt.ylim(-0.02, 0.1)
    file = open("result.txt", "w")
    print >> file, X
    print >> file, Y

    plt.show()


test()


