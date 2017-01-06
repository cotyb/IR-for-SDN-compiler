#coding = utf-8
import SA
import reg2_DFA

# Merlin abstract syntax: [s1;...;sn], fai
# [ x : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 20) -> .* dpi .* ;
# y : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 21) -> .* ;
# z : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 80) -> .* dpi .* nat .* ],
# max(x + y,50MB/s) and min(z,100MB/s)

function = ["dpi", "nat"]

def statement2_dict(statement):
    result = {}
    statement = statement.strip("[ ]")
    stetements = statement.split(";")
    for stete in stetements:
        key, value = stete.split(":")
        predict, functions = value.split("->")
        result[key.strip()] = (predict, functions)
    return result

def constraint2_dict(constraint):
    result = {}
    constraints = constraint.split("and")
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
    statement, constraint = policy.split("],")
    statement = statement2_dict(statement)
    constraint = constraint2_dict(constraint)
    return statement, constraint

def policy2_SA(statement, constraint):
    all_sa = []
    for state_id in statement:
        if state_id not in constraint.keys():
            predict, functions = statement[state_id][0], statement[state_id][1]
            dfa = reg2_DFA.RegexDFA(functions.strip())
            dfa.minimize_dfa()




if __name__ == "__main__":
    policy ="[ x : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 20) -> .* dpi .* ;\
    y : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 21) -> .* ;\
    z : (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 80) -> .* dpi .* nat .* ],\
    max(x,50MB/s) and min(z,100MB/s)"

    statement, constraint = parser_policy(policy)
    policy2_SA(statement, constraint)
