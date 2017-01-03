import SA

def sa_construct():
    start = SA.Node(1)
    end = SA.Node(2)
    sa = SA.SA(start,end)
    sa.add_edge(start,end,"if i<1", "FWD(.)", "i++")
    print sa.sa_str()
    return sa

def sa_update():
    sa = sa_construct()
    edge = sa.edges[0]
    print type(edge)
    print edge
    print type(sa)
    sa.update_edge(edge, ["update"], ["i--"])
    print sa.sa_str()


sa_update()
