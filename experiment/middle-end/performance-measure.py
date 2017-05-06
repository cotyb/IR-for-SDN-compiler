# -*- coding: utf-8 -*-

import fsm_2_17
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
        # print value1
        for edge_action, value2 in value1.items():
            for edge_end, value3 in value2.items():
                # count denotes the number of (guard, update) tuple
                count = len(value3) / 2
                for dummy_i in range(count):
                    edge_guard, edge_update = value3[2*dummy_i], value3[2*dummy_i + 1]
                    sa.add_edge_indirect(SA.Node(int(edge_start)), SA.Node(int(edge_end)), edge_guard, edge_action, edge_update)
    return sa

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

def test():
    # x = np.linspace(1, 101)
    # y = np.linspace(0, 0.1)

    ax1 = plt.subplot(121) #创建一个三维的绘图工程
    ax2 = plt.subplot(122)


    # plt.style.use('ggplot')
    # plt.xlabel("SA中边的个数", fontsize='xx-large')
    # plt.ylabel("时间/s", fontsize='xx-large')
    # plt.title("Time and the num of edges of SA")
    count_1 = 7
    count_2 = 1000
    sa = construct_sa()
    X, Y = [], []
    X1, Y1 = [], []
    for i in range(0, 150):
        print(i)
        count_1 += 1
        count_2 += 1
        sa = construct_sa_random(sa, i, count_1,count_2)
        sa, edge1, edge2 = last_two_edge(sa, count_1, count_2)
        # sa.draw_sa("result")
        # print "waiting...%s...%s" %(100.0 * count/17/16, count)
        c_s_1 = time.time()
        alphabet, states, initial, finals, map = sa.to_fsm()
        # print alphabet, states, initial, finals, map
        sa_fsm = fsm_2_17.fsm(alphabet=alphabet, states=states, initial=initial, finals=finals, map=map)
        result_1 = sa_fsm.union(sa_fsm)
        result_1 = fsm2SA(result_1)
        using_time_1 = time.time() - c_s_1


        ax1.set_ylabel('时间/s', fontsize='large')
        ax1.set_xlabel('并运算之后SA边的个数', fontsize='large')

        ax1.scatter(len(result_1.edges),using_time_1,s=0.5, c='b')
        X.append(len(result_1.edges))
        Y.append(using_time_1)

        # ax2.set_ylabel('时间/s', fontsize='x-large')
        ax2.set_xlabel('交运算之后SA边的个数', fontsize='large')

        c_s_2 = time.time()

        alphabet, states, initial, finals, map = sa.to_fsm()
        sa_fsm = fsm_2_17.fsm(alphabet=alphabet, states=states, initial=initial, finals=finals, map=map)
        result_2 = sa_fsm.intersection(sa_fsm)
        result_2 = fsm2SA(result_2)

        using_time_2 = time.time() - c_s_2
        X1.append(len(result_2.edges))
        Y1.append(using_time_2)

        ax2.scatter(len(result_2.edges),using_time_2, s=0.5, c='b')

        sa.del_edge(edge1)
        sa.del_edge(edge2)


        # plt.plot(x, using_time)
        # plt.ylim(-0.02, 0.1)
    file_1 = open("result_union.txt", "w")
    print >> file_1, X
    print >> file_1, Y

    file_2 = open("result_intersection.txt", "w")
    print >> file_2, X1
    print >> file_2, Y1
    plt.show()


test()







