#coding = utf-8
import SA
import reg2_DFA
import copy
import pickle

# Merlin abstract syntax: [s1;...;sn], fai
# [ x : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 20) -> .* dpi .* ;
# y : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 21) -> .* ;
# z : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 80) -> .* dpi .* nat .* ],
# max(x + y,50MB/s) and min(z,100MB/s)

function = ["dpi", "nat", "count", "ftp"]
fun_switch = {'dpi':['a', 'b'], 'nat':['c', 'd'], 'count':['e'], 'ftp':['f']}
fun_guard_update = {'dpi':['', ''], 'nat':['', ''], 'count':['', 'rv(CNT)']}

def get_switch_fun(fun_switch):
    result = {}
    for fun, switch in fun_switch.items():
        for sw in switch:
            result[sw] = fun
    return result

switch_fun = get_switch_fun(fun_switch)

def statement2_dict(statement):
    if not statement:
        return
    result = {}
    statement = statement.strip("[ ]")
    stetements = statement.split(";")
    for state in stetements:
        key, value = state.split(":")
        predict, functions = value.split("->")
        predict = predict.strip(' ()').replace("and", "&&")
        result[key.strip()] = (predict, functions)
    return result

def constraint2_dict(constraint):
    result = {}
    if not constraint:
        return
    constraints = constraint.strip().split("and")
    for const in constraints:
        const = const.strip()
        if const.startswith("max"):
            id, rate = const.replace("max", "").strip("( )").split(",")
            flag = "max"
        elif const.startswith("min"):
            id, rate = const.replace("min", "").strip("( )").split(",")
            flag = "min"
        else:
            raise Exception
        result[id.strip()] = (flag, rate)
    return result

def parser_policy(policy):
    if policy.__contains__(","):
        statement, constraint = policy.split("],")
    else:
        statement, constraint = policy, ''
    statement = statement2_dict(statement)
    if constraint == '':
        constraint = {}
    else:
        constraint = constraint2_dict(constraint)
    return statement, constraint


def change_format(nodes, edges):
    dfa_edges = edges
    dfa_nodes = [list(x) for x in nodes]
    add_edge = []
    del_edge = []
    for edge in edges:
        if edge[2].__contains__(','):
            del_edge.append(edge)
            for sw in edge[2].split(','):
                add_edge.append([edge[0], edge[1], sw])
    dfa_edges.extend(add_edge)
    if len(del_edge) != 0:
        for a in del_edge:
            dfa_edges.remove(a)
    # dfa_nodes and dfa_edges have meet the requirements
    return dfa_nodes, dfa_edges


def policy2_SA(statement, constraint):
    all_sa = []
    for state_id in statement:
        # different logic according to whether rate constraint
        # if this statement does not have rate constraint
        if state_id not in constraint.keys():
            predict, functions = statement[state_id][0], statement[state_id][1]
            for fun, path in fun_switch.items():
                functions = functions.replace(fun, '(' + '|'.join(path) + ')')
            dfa = reg2_DFA.RegexDFA(functions.strip())
            dfa.minimize_dfa()
            try:
                dfa.draw_dfa()
            except:
                print "the graph is in dfa"
            # dfa._edges contains all the edges in DFA, so we can change it to SA
            # dfa._dfa_node contains all the nodes with the right order corresponding to DFA
            # handle dfa_nodes and dfa_edges to the syntax we want
            dfa_nodes, dfa_edges = change_format(dfa._dfa_node, dfa._dfa)
            start = SA.Node(dfa_nodes[0][0])
            end = SA.Node(dfa_nodes[-1][0])
            sa = SA.SA(start, end)
            sa.nodes = [SA.Node(x[0]) for x in dfa_nodes]


            print dfa_edges

            for edge in dfa_edges:
                sa_edge_start = SA.Node(int(edge[0]))
                sa_edge_end = SA.Node(int(edge[1]))
                if sa_edge_start == start:
                    if edge[2] == '.':
                        guard = ''
                        action = 'FWD(.)'
                        update = ''
                        sa.add_edge_indirect(sa_edge_start, sa_edge_start, guard, "FWD(.)", update)
                    elif edge[2] in switch_fun.keys():
                        guard = predict
                        new_node = sa.generate_node()
                        # action = 'FWD(%s)' %new_node.id
                        action = 'FWD(%s)' %edge[2]
                        update = ''
                        sa_edge = SA.Edge(sa_edge_start, new_node, guard, action, update)
                        sa.add_edge_direct(sa_edge)
                        new_edge_start = new_node
                        new_edge_end = sa_edge_end
                        guard = fun_guard_update[switch_fun[edge[2]]][0]
                        # action = "FW(%s)" %(new_edge_end.id) + " && " + switch_fun[edge[2]]
                        action = "FWD(.)" + " && " + switch_fun[edge[2]]
                        if fun_guard_update[switch_fun[edge[2]]][1] == '':
                            update = ''
                        else:
                            update = "%s(%s)=%s"   %(switch_fun, new_edge_start.id, fun_guard_update[edge[2]][1])
                        sa.add_edge_indirect(new_edge_start, new_edge_end, guard, action, update)
                    else:
                        guard = predict
                        action = 'FWD(%s)' %edge[2]
                        update = ''
                        sa_edge = SA.Edge(sa_edge_start, sa_edge_end, guard, action, update)
                        sa.add_edge_direct(sa_edge)

                else:
                    if edge[2] == '.':
                        guard = ''
                        action = 'FWD(.)'
                        update = ''
                        sa.add_edge_indirect(sa_edge_start, sa_edge_start, guard, "FWD(.)", update)
                    elif edge[2] in switch_fun.keys():
                        guard = ''
                        new_node = sa.generate_node()
                        # action = 'FWD(%s)' %new_node.id
                        action = 'FWD(%s)' %edge[2]
                        update = ''
                        sa_edge = SA.Edge(sa_edge_start, new_node, guard, action, update)
                        sa.add_edge_direct(sa_edge)
                        new_edge_start = new_node
                        new_edge_end = sa_edge_end
                        guard = fun_guard_update[switch_fun[edge[2]]][0]
                        # action = "FW(%s)" %(new_edge_end.id) + " && " + switch_fun[edge[2]]
                        action = "FWD(.)" + " && " + switch_fun[edge[2]]
                        if fun_guard_update[switch_fun[edge[2]]][1] == '':
                            update = ''
                        else:
                            update = "%s(%s)=%s"   %(switch_fun, new_edge_start.id, fun_guard_update[edge[2]][1])
                        sa.add_edge_indirect(new_edge_start, new_edge_end, guard, action, update)
                    else:
                        guard = ''
                        action = 'FWD(%s)' %edge[2]
                        update = ''
                        sa_edge = SA.Edge(sa_edge_start, sa_edge_end, guard, action, update)
                        sa.add_edge_direct(sa_edge)

            # add a edge to end
            generate_new_node = sa.generate_node()
            sa.add_edge_indirect(end, generate_new_node, '', 'FWD(e)', '')
            sa.change_end_node(generate_new_node)
            all_sa.append(sa)


        # if the statement has rate constraint
        else:
            flag, rate = constraint[state_id][0], constraint[state_id][1]

            predict, functions = statement[state_id][0], statement[state_id][1]
            for fun, path in fun_switch.items():
                functions = functions.replace(fun, '(' + '|'.join(path) + ')')
            dfa = reg2_DFA.RegexDFA(functions.strip())
            dfa.minimize_dfa()
            try:
                dfa.draw_dfa()
            except:
                print "the graph is in dfa"
            # dfa._edges contains all the edges in DFA, so we can change it to SA
            # dfa._dfa_node contains all the nodes with the right order corresponding to DFA
            # handle dfa_nodes and dfa_edges to the syntax we want
            dfa_nodes, dfa_edges = change_format(dfa._dfa_node, dfa._dfa)
            start = SA.Node(dfa_nodes[0][0])
            end = SA.Node(dfa_nodes[-1][0])
            sa = SA.SA(start, end)
            sa.nodes = [SA.Node(x[0]) for x in dfa_nodes]


            print dfa_edges

            for edge in dfa_edges:
                sa_edge_start = SA.Node(int(edge[0]))
                sa_edge_end = SA.Node(int(edge[1]))
                if sa_edge_start == start:
                    if edge[2] == '.':
                        guard = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        action = 'FWD(.)'
                        update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa.add_edge_indirect(sa_edge_start, sa_edge_start, guard, "FWD(.)", update)
                    elif edge[2] in switch_fun.keys():
                        fix_tmp = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        guard = predict + ' && ' + fix_tmp
                        new_node = sa.generate_node()
                        # action = 'FWD(%s)' %new_node.id
                        action = 'FWD(%s)' %edge[2]
                        update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa_edge = SA.Edge(sa_edge_start, new_node, guard, action, update)
                        sa.add_edge_direct(sa_edge)
                        new_edge_start = new_node
                        new_edge_end = sa_edge_end
                        fix_tmp = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        guard = fun_guard_update[switch_fun[edge[2]]][0] + ' && ' + fix_tmp if \
                            len(fun_guard_update[switch_fun[edge[2]]][0].strip())>0 else fix_tmp
                        # action = "FW(%s)" %(new_edge_end.id) + " && " + switch_fun[edge[2]]
                        action = "FWD(.)"  + " && " + switch_fun[edge[2]]
                        if fun_guard_update[switch_fun[edge[2]]][1] == '':
                            update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        else:
                            update = "%s(%s)=%s"   %(switch_fun, new_edge_start.id, fun_guard_update[edge[2]][1]) + ' && ' + \
                                     's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa.add_edge_indirect(new_edge_start, new_edge_end, guard, action, update)
                    else:
                        fix_tmp = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        guard = predict + ' && ' + fix_tmp
                        action = 'FWD(%s)' %edge[2]
                        update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa_edge = SA.Edge(sa_edge_start, sa_edge_end, guard, action, update)
                        sa.add_edge_direct(sa_edge)

                else:
                    if edge[2] == '.':
                        guard = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        action = 'FWD(.)'
                        update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa.add_edge_indirect(sa_edge_start, sa_edge_start, guard, "FWD(.)", update)
                    elif edge[2] in switch_fun.keys():
                        guard = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        new_node = sa.generate_node()
                        # action = 'FWD(%s)' %new_node.id
                        action = 'FWD(%s)' %edge[2]
                        update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa_edge = SA.Edge(sa_edge_start, new_node, guard, action, update)
                        sa.add_edge_direct(sa_edge)
                        new_edge_start = new_node
                        new_edge_end = sa_edge_end
                        fix_tmp = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        guard = fun_guard_update[switch_fun[edge[2]]][0] + ' && ' + fix_tmp if \
                            len(fun_guard_update[switch_fun[edge[2]]][0].strip())>0 else fix_tmp
                        # action = "FW(%s)" %(new_edge_end.id) + " && " + switch_fun[edge[2]]
                        action = "FWD(.)" + " && " + switch_fun[edge[2]]
                        if fun_guard_update[switch_fun[edge[2]]][1] == '':
                            update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        else:
                            update = "%s(%s)=%s"   %(switch_fun, new_edge_start.id, fun_guard_update[edge[2]][1]) + \
                                     ' && ' + 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa.add_edge_indirect(new_edge_start, new_edge_end, guard, action, update)
                    else:
                        guard = 'bw[s1][s2]<%s' %(rate) if flag == 'max' else 'bw[s1][s2]>%s' %(rate)
                        action = 'FWD(%s)' %edge[2]
                        update = 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)'
                        sa_edge = SA.Edge(sa_edge_start, sa_edge_end, guard, action, update)
                        sa.add_edge_direct(sa_edge)

            # add a edge to end
            generate_new_node = sa.generate_node()
            sa.add_edge_indirect(end, generate_new_node, '', 'FWD(e)', '')
            sa.change_end_node(generate_new_node)
            all_sa.append(sa)

    return all_sa



if __name__ == "__main__":
    policy ="[ x : (ip.src = '192.168.1.1' and ip.dst = '192.168.1.2' and tcp.dst = 20) -> .*dpi.*;\
    y : (ip.src = '192.168.1.1' and ip.dst = '192.168.1.2' and tcp.dst = 21) -> .*z.*;\
    z : (ip.src = '192.168.1.1' and ip.dst = '192.168.1.2' and tcp.dst = 80) -> .*dpi.*nat.*],\
    max(x,50MB/s) and min(y,100MB/s)"

    statement, constraint = parser_policy(policy)
    all_sa = policy2_SA(statement, constraint)
    num = 1
    all_sa[1].sa_str()
    # print all_sa[1].accepts(['a','c','d','e'])
    print all_sa[0].divide_sa().values()[0].sa_str()
    # print all_sa[1].end.id
    for sa in all_sa:
        # sa.sa_str()
        file = open("./Merlin_sa/Merlin_sa_"+str(num), "wb")
        pickle.dump(sa, file)
        file.close()
        num += 1

    for i in range(len(all_sa)):
        all_sa[i].draw_sa(str(i))
