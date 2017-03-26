#coding = utf-8
from collections import defaultdict

class SA(object):
    '''
    define the structure of SA
    SA is composed of edges
    edge is composed of two nodes, guard, action, update
    for all SA, node 1 is the start, node 2 is the end
    '''
    def __init__(self, start, end):
        assert type(start) == Node
        assert type(end) == Node
        self.start = start
        self.end = end
        self.edges = []
        self.nodes = [start, end]

    def accepts(self, path):
        '''
        Test whether the SA accepts the given path
        :param path: a list, like [a, b, c]
        :return: True or False
        '''
        state = self.start.id
        for sw in path:
            pass



    def to_fsm(self):
        alphabet = set()
        states = set()
        initial = 0
        finals = set()
        map = {}

        initial = self.start.id
        finals.add(self.end.id)
        for node in self.nodes:
            states.add(node.id)
        for edge in self.edges:
            alphabet.add(edge.action)
            key = edge.start.id
            if key not in map:
                value = {edge.action:{edge.end.id:[edge.guard, edge.update]}}
                map[key] = value
            else:
                tmp = map[key]
                if edge.action not in tmp:
                    tmp[edge.action] = {edge.end.id:[edge.guard, edge.update]}
                    map[key] = tmp
                else:
                    tmp = map[edge.start.id][edge.action]
                    if edge.end.id not in tmp:
                        tmp[edge.end.id] = [edge.guard, edge.update]
                        map[edge.start.id][edge.action] = tmp
                    else:
                        tmp = map[edge.start.id][edge.action][edge.end.id]
                        tmp.append(edge.guard)
                        tmp.append(edge.update)
                        map[edge.start.id][edge.action][edge.end.id] = tmp

        return alphabet, states, initial, finals, map


    def generate_node(self):
        new_node = Node(len(self.nodes) + 1)
        self.nodes.insert(-1, new_node)
        return new_node

    def add_edge_direct(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def add_edge_indirect(self, edge_start, edge_end, guard, action, update):
        new_edge = Edge(edge_start, edge_end, guard, action, update)
        if new_edge not in self.edges:
            self.edges.append(new_edge)

    def del_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print "the edge does not exist"


    def draw_sa(self, file):
        '''
        show sa in graph, this function write the data to file
        :param file:
        :return: noting
        '''
        file = open(file, "w")
        print >> file, "digraph {"
        for node in self.nodes:
            print >> file, "    %s" %node
        for edge in self.edges:
            lable = "\"" + edge.guard + edge.action + edge.update + "\""
            print >> file, "        %s -> %s [label=%s]" %(edge.start.id, edge.end.id, lable.strip())
        print >> file, '}'


    def update_edge(self, edge, field, new_value):
        '''
        update the five fields value of edge
        :param edge: a edge in SA
        :param field: a list of field to change
        :param new_value: a list
        :return: nothing
        '''
        print type(edge)
        edge.update_edge(field, new_value)

    def sa_str(self):
        for edge in self.edges:
            print edge

    def insert_sa(self, start, end, sa):
        '''
        can not use now!!!
        some bug, the nodes will conflict
        :param start:
        :param end:
        :param sa:
        :return:
        '''
        del_edge = []
        for edge in self.edges:
            if edge.start == start and edge.end == end:
                del_edge.append(edge)
        self.edges = list(set(self.edges) - set(del_edge))
        for edge in sa.edges:
            self.edges.append(edge)


class Edge(object):
    '''
    edge is composed of two nodes, guard, action, update
    guard is the string joined with &&
    update is the string joined with &&
    '''

    def __init__(self, start, end, guard, action, update):
        assert type(start) == Node
        assert type(end) == Node
        self.start = start
        self.end = end
        self.guard = guard
        self.action = action
        self.update = update

    def update_edge(self, field, new_value):
        field_value = zip(field, new_value)
        for f, v in field_value:
            setattr(self, f, v)

    def __str__(self):
        return ",".join([str(self.start), self.guard, self.action, self.update, str(self.end)])

class Node(object):

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        return self.id == other.id





