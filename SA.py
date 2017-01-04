#coding = utf-8

class SA(object):
    '''
    define the structure of SA
    SA is composed of edges
    edge is composed of two nodes, guard, action, update
    for all SA, node 1 is the start, node 2 is the end
    '''

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.edges = []

    def add_edge(self, edge_start, edge_end, guard, action, update):
        new_edge = Edge(edge_start, edge_end, guard, action, update)
        if new_edge not in self.edges:
            self.edges.append(new_edge)

    def del_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print "the edge does not exist"


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





