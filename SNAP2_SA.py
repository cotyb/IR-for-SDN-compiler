#coding=utf-8
import networkx as nx
import snap.policies as policies
import snap.stateful as stateful
import SA
import graphviz as gv
import sys

sys.path.append("E:\Program Files (x86)\Graphviz2.38\bin\dot")

class BinaryTree(object):
    def __init__(self, item):
        self.key = item
        self.left = None
        self.right = None

    def insertLeft(self, item):
        if self.left == None:
            self.left = BinaryTree(item)
        else:
            t = BinaryTree(item)
            t.left = self.left
            self.left = t

    def insertRight(self, item):
        if self.right == None:
            self.right = BinaryTree(item)
        else:
            t = BinaryTree(item)
            t.right = self.right
            self.right = t

def traverse_tree(root):
    '''
    breadth traversal
    :param root: the root of the binary tree
    :return:
    '''
    if root == None:
        return
    myqueue = []
    node = root
    myqueue.append(node)
    while myqueue:
        node = myqueue.pop(0)
        print node.key
        if node.left != None:
            myqueue.append(node.left)
        if node.right != None:
            myqueue.append(node.right)


def SNAP_policy2_xfdd():
    graph_demo = nx.DiGraph()
    traffic_req = {}
    ports = [1,2,3,4,5,6]
    policy = policies.get_dns_tunnel_policy(ports)
    # policy = policies.get_ftp_monitoring_policy(ports)
    assumption = policies.get_route_and_assump_policy(ports)[1]
    xfdd = stateful.compile_to_xfdd(policy, assumption, ports)
    return xfdd


def xfdd2_binarytree(xfdd):

    xfdd = xfdd.split("\n")
    if xfdd[0].__contains__(":"):
        xfdd_tree = BinaryTree(xfdd[0].split(":")[1].strip("( ) \t \n"))
        recursive_construct_tree(xfdd_tree, xfdd[1:], 0)
    return xfdd_tree


def recursive_construct_tree(root, statements, tab_count):
    left, right = -1, -1
    if len(statements) == 0:
        return None
    if len(statements) == 1 and statements[0].endswith("}"):
        return
    for i in range(len(statements)):
        if statements[i].count("\t") == tab_count + 1:
            if left == -1:
                left = i
            else:
                right = i
    root.left = BinaryTree(statements[left].split(":")[1].strip('\t \n')) if statements[left].__contains__(":") \
                else BinaryTree(statements[left].strip('\t \n'))
    root.right = BinaryTree(statements[right].split(":")[1].strip('\t \n')) if statements[right].__contains__(":") \
                else BinaryTree(statements[right].strip('\t \n'))
    recursive_construct_tree(root.left, statements[left+1:right], tab_count+1)
    recursive_construct_tree(root.right, statements[right:], tab_count+1)


def binary_tree_paths(root):
    result = []
    if root == None:
        return result
    path = ""
    Paths(root, result, path)
    return result

def Paths(root, result, path):
    if root == None:
        result
    if root.left == None and root.right == None:
        path += "|||" + root.key
        result.append(path)
        return
    path_left, path_right = path, path
    path_left += root.key + " && "
    path_right += root.key.replace("=","!=") + " && "
    Paths(root.left, result, path_left)
    Paths(root.right, result, path_right)


def xfdd_tree2_SA(xfdd_tree):
    start = SA.Node(1)
    end = SA.Node(2)
    sa = SA.SA(start, end)
    sa.add_edge(start, start, "", "FWD(.)", "")
    all_path = binary_tree_paths(xfdd_tree)
    action = "FWD(e)"
    for path in all_path:
        guard, update = path.split("&& |||")
        sa.add_edge(start, end, guard, action, update)
    return sa

def draw_dfa(sa, filename="xfdd_sa"):
    g = gv.Digraph(format="pdf")
    g.node(str(1), color="red")
    g.node(str(2), color="blue")

    for edge in sa.edges:
        g.edge(str(edge.start.id), str(edge.end.id), label=edge.guard + edge.action + edge.update)
    g.render(filename)

if __name__ == "__main__":
    xfdd = SNAP_policy2_xfdd()
    xfdd_tree = xfdd2_binarytree(xfdd)
    sa = xfdd_tree2_SA(xfdd_tree)
    sa.sa_str()
    draw_dfa(sa)