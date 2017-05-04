#-*- coding: UTF-8 -*-
import time
import Merlin2_SA
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import random

function = ["dpi", "nat", "count", 'z']
header_field = ["dstip", "srcip", "srcport", "dstport"]
header_value = {'dstip':'10.0.0.1', 'srcip':'10.0.0.2', 'srcport':'20', 'dstport':'80'}
max_or_min = ["max", "min"]
bandwidth = ["100MB/s", "100MB/s"]


def construct_Merlin_policy(num):
    '''
    construct a Merlin policy contains num statements
    :param num:
    :return: a Merlin policy
    '''
    policy = ""
    constraint = []
    for dummy_i in range(num):
        id = chr(ord('a') + dummy_i/26 - 0) + chr(ord('a') + dummy_i%26 - 0)
        headers = random.sample(header_field, random.randint(1, 4))
        functions = random.sample(function, random.randint(1, 4))
        bandwidth_constrain = random.randint(0,2)
        if bandwidth_constrain != 2:
            constraint.append(max_or_min[bandwidth_constrain] + '(' + id + ',' + bandwidth[bandwidth_constrain] + ')')
        predict = " and ".join([x + "=" + '\'' + header_value[x] + '\'' for x in headers])
        action_list = ".*" + ".*".join(functions)
        statement = id + ":" + "(" + predict + ")" + " -> " + action_list + ".*" + ";"
        policy += statement

    policy = '[' + policy[:-1] + ']' + ',' + " and ".join(constraint)

    # policy ="[ x : (ip.src = '192.168.1.1' and ip.dst = '192.168.1.2' and tcp.dst = 20) -> .*dpi.*;\
    # y : (ip.src = '192.168.1.1' and ip.dst = '192.168.1.2' and tcp.dst = 21) -> .*z.*;\
    # z : (ip.src = '192.168.1.1' and ip.dst = '192.168.1.2' and tcp.dst = 80) -> .*dpi.*nat.*],\
    # max(x,50MB/s) and min(y,100MB/s)"
    return  policy

# for i in range(100):
#     policy = construct_Merlin_policy(i)
#     print policy


def test():
    x = np.linspace(1, 101)
    y = np.linspace(0, 0.1)
    plt.style.use('ggplot')
    plt.xlabel("Num of Merlin statements/#")
    plt.ylabel("Time/s")
    plt.title("Time and the num of Merlin statements")
    for i in range(1, 101):
        # policy = construct_Merlin_policy(100)
        policy = construct_Merlin_policy(i)
        t_s = time.time()
        statement, constraint = Merlin2_SA.parser_policy(policy)
        all_sa = Merlin2_SA.policy2_SA(statement, constraint)
        using_time = time.time() - t_s
        plt.scatter(i,using_time)
        # plt.plot(x, using_time)
        plt.ylim(-0.02, 0.1)
    plt.show()

test()