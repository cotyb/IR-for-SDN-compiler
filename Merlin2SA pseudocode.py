1 def Merlin2SA(policy):
2     Merlin_sa = []
3     statement, constraint = parser_policy(policy)
4 	for state_id in statement:
5 	    if state_id not in constraint:
6 		    predict, path_regression = parser_statement(statement)
7 			path = replace_fun_with_switch(path_regression)
8 			dfa = reg2DFA(path)
9 			start, end, nodes = get_info(dfa)
10			sa_edges = []
11			for edge in dfa.edges:
12			    e_start, e_end, guard, action, update = tranfer_edge(edge)
13				sa_edge = construct_edge(e_start, e_end, guard, action, update)
14				sa_edges.append(sa_edge)
15			sa = construct_sa(start, end, nodes, sa_edges)
16			Merlin_sa.append(sa)			
17			
18		else:
19		    flag, rate = parser_constraint(constraint)
20			predict, path_regression = parser_statement(statement)
21			path = replace_fun_with_switch(path_regression)
22			dfa = reg2DFA(path)
23			start, end, nodes = get_info(dfa)
24			sa_edges = []
25			for edge in dfa.edges:
26			    e_start, e_end, guard, action, update = tranfer_edge(edge)
27				guard += generate_guard(flag, rate)
28				update += generate_update(flag, rate)
29				sa_edge = construct_edge(e_start, e_end, guard, action, update)
30				sa_edges.append(sa_edge)
31			sa = construct_sa(start, end, nodes, sa_edges)
32			Merlin_sa.append(sa)
33	return Merlin_sa