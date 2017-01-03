#coding=utf-8
import networkx as nx
import snap.policies as policies
import snap.stateful as stateful

def SNAP_policy2_xFDD():
    graph_demo = nx.DiGraph()
    traffic_req = {}
    ports = [1,2,3,4,5,6]
    # policy = policies.get_dns_tunnel_policy(ports)
    policy = policies.get_ftp_monitoring_policy(ports)
    assumption = policies.get_route_and_assump_policy(ports)[1]
    xfdd = stateful.compile_to_xfdd(policy, assumption, ports)
    return xfdd

xfdd = SNAP_policy2_xFDD()
print xfdd
result = xfdd.split("\n")
print result
