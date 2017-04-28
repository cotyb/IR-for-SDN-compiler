#coding = utf-8
'''
edge: start, guard, action, update, end
guard: &&
update {[update1; update2; ...]}
'''
from collections import defaultdict
from cfg import header_field
from cfg import header_field_1
import re
import copy


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
        self.state_configuration = {}

    def add_state_configuration(self, key, value):
        self.state_configuration[key] = value

    def update_state_configuration(self, key, value):
        if key in self.state_configuration:
            self.state_configuration[key] = value
            

    def change_end_node(self, new_end_node):
        self.end = new_end_node

    def divide_sa(self):
        '''
        divide sa into many sub-sa according to traffic
        :return: result, {flag: sa} flag denotes specific traffic
        flag is a string : "srcip = xxx, dstip = xxx"
        '''
        result = {}
        initial_node = self.start.id
        # the traffic information only appears in the first two nodes
        edges_begin_with_sa_start = []
        edges_begin_not_with_sa_start = []
        no_traffic_info = []
        for edge in self.edges:
            if edge.start.id == self.start.id:
                if edge.extract_traffic_info() == '':
                    no_traffic_info.append(edge)
                else:
                    edges_begin_with_sa_start.append(edge)
        edges_begin_not_with_sa_start = list(set(self.edges) - set(edges_begin_with_sa_start))
        if edges_begin_with_sa_start == []:
            result[''] = self

        while len(edges_begin_with_sa_start) > 0:
            first_edge = edges_begin_with_sa_start[0]
            flag = first_edge.extract_traffic_info()
            this_sa_edges = [first_edge]
            other_sa_edges = []
            for edge in edges_begin_with_sa_start[1:]:
                if first_edge.conflicts(edge):
                    other_sa_edges.append(edge)
                else:
                    this_sa_edges.append(edge)
            edges_begin_with_sa_start = list(set(edges_begin_with_sa_start) - set(this_sa_edges))
            new_sa = copy.deepcopy(self)
            new_sa.clear_edges()
            for edge in this_sa_edges:
                new_sa.add_edge_direct(edge)
            for edge in edges_begin_not_with_sa_start:
                new_sa.add_edge_direct(edge)
            result[flag] = new_sa
        return result


    def accepts(self, path):
        '''
        Test whether the SA accepts the given path
        :param path: a list, like [a, b, c]
        :return: True or False
        '''
        if len(path) == 0:
            return False
        pattern = re.compile('FWD\\((.)\\)')
        state = self.start
        for edge in self.edges:
            if edge.start == state:
                to_sw = re.match(pattern, edge.action).expand(r'\1')
                if to_sw == '.':
                    return self.match(path[1:], edge.end)
                elif to_sw == path[0]:
                    return self.match(path[1:], edge.end)
                else:
                    continue
        return False


    def match(self, path, state):
        pattern = re.compile('FWD\\((.)\\)')
        if len(path) == 0:
            for edge in self.edges:
                if state == edge.start and edge.end == self.end:
                    return True
            return False
        else:
            for edge in self.edges:
                if state == edge.start:
                    to_sw = re.match(pattern, edge.action).expand(r'\1')
                    if to_sw == '.':
                        return self.match(path[1:], edge.end)
                    elif to_sw == path[0]:
                        return self.match(path[1:], edge.end)
                    else:
                        continue

    def accepts_with_state(self, path):
        '''
        Test whether the SA accepts the given path
        :param path: a list, like [a, b, c]
        :return: True or False
        '''
        if len(path) == 0:
            return False
        pattern = re.compile('FWD\\((.)\\)')
        state = self.start
        for edge in self.edges:
            if edge.start == state:
                guard = edge.guard
                guards = guard.split("&&")
                for guard in guards:
                    if len(guard.strip()) == 0:
                        continue
                    elif guard.__contains__("bw[s1][s2]"):
                        continue
                    eval(guard)
                to_sw = re.match(pattern, edge.action).expand(r'\1')
                if to_sw == '.':
                    return self.match_with_state(path[1:], edge.end)
                elif to_sw == path[0]:
                    return self.match_with_state(path[1:], edge.end)
                else:
                    continue
        return False


    def match_with_state(self, path, state):
        pattern = re.compile('FWD\\((.)\\)')
        if len(path) == 0:
            for edge in self.edges:
                if state == edge.start and edge.end == self.end:
                    return True
            return False
        else:
            for edge in self.edges:
                if state == edge.start:
                    to_sw = re.match(pattern, edge.action).expand(r'\1')
                    if to_sw == '.':
                        return self.match(path[1:], edge.end)
                    elif to_sw == path[0]:
                        return self.match(path[1:], edge.end)
                    else:
                        continue


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

    def clear_edges(self):
        self.edges = []

    def sa_backup(self):
        start = self.start
        end = self.end
        self.edges = []
        self.nodes = [start, end]

    def add_edge_indirect(self, edge_start, edge_end, guard, action, update):
        for i in range(len(header_field_1)):
            if guard.__contains__(header_field_1[i]):
                guard = guard.replace(header_field_1[i], header_field[i])

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
        for i in range(len(header_field_1)):
            if guard.__contains__(header_field_1[i]):
                guard = guard.replace(header_field_1[i], header_field[i])
        self.start = start
        self.end = end
        self.guard = guard
        self.action = action
        self.update = update

    def update_edge(self, field, new_value):
        field_value = zip(field, new_value)
        for f, v in field_value:
            setattr(self, f, v)

    def extract_traffic_info(self):
        flag = ''
        for field in header_field:
            if self.guard.__contains__(field):
                field_value_1 = self.guard[self.guard.find(field):]
                value_1 = field_value_1[field_value_1.find(field):field_value_1.find(' ',len(field)+4)]
                flag += value_1 + ',' + ' '
        if len(flag) > 0:
            return flag[:-2]
        return flag


    def conflicts(self, edge):
        '''
        for back end, test whether two edges are conflicted
        :param edge: an edge
        :return: True if conflicts, False if not conflicts
        '''
        for field in header_field:
            if self.guard.__contains__(field) and edge.guard.__contains__(field):
                field_value_1, field_value_2 = self.guard[self.guard.find(field):], \
                                               edge.guard[edge.guard.find(field):]
                value_1 = field_value_1[field_value_1.find(field):field_value_1.find(' ',len(field)+3)]
                value_2 = field_value_2[field_value_2.find(field):field_value_2.find(' ',len(field)+3)]
                if value_1 == value_2:
                    continue
                else:
                    return True
            else:
                continue
        return False


    def __str__(self):
        return ",".join([str(self.start), self.guard, self.action, self.update, str(self.end)])

class Node(object):

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        return self.id == other.id