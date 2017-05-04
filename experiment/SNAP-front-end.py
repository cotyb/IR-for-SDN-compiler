import time
import SNAP2_SA
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import random
import snap.policies as policies
import snap.stateful as stateful

ports = [1,2,3,4,5,6]
all_p = [policies.get_dns_tunnel_policy(ports), policies.get_sidejack_policy(ports),
         policies.get_dns_tunnel_simplified_policy(ports),policies.get_stateful_firewall_policy(ports),policies.get_domains_per_ip_policy(ports),policies.get_ips_per_domain_policy(ports),
         policies.get_dns_ttl_change_policy(ports),policies.get_spam_detection_policy(ports),policies.get_ftp_monitoring_policy(ports),policies.get_super_spreader_detection_policy(ports),
         policies.get_flow_size_policy(ports),policies.get_sample_small_policy(ports),policies.get_sample_med_policy(ports),policies.get_sample_large_policy(ports),
         policies.get_size_based_sampling_policy(ports),policies.get_selective_mpeg_policy(ports),policies.get_dns_amplification_policy(ports),policies.get_udp_flood_detection_policy(ports),
         policies.get_heavy_hitter_policy(ports),policies.get_tcp_state_machine_policy(ports),policies.get_snort_policy(ports)]

def test():
    x = np.linspace(1, 22)
    y = np.linspace(0, 0.1)
    plt.style.use('ggplot')
    plt.xlabel("SNAP app")
    plt.ylabel("Time/s")
    # plt.title("Time and the num of Merlin statements")
    for i in range(len(all_p)):
        # policy = construct_Merlin_policy(100)
        t_s = time.time()
        policy = all_p[i]
        assumption = policies.get_route_and_assump_policy(ports)[1]
        xfdd = stateful.compile_to_xfdd(policy, assumption, ports)
        xfdd_tree = SNAP2_SA.xfdd2_binarytree(xfdd)
        sa = SNAP2_SA.xfdd_tree2_SA(xfdd_tree)

        using_time = time.time() - t_s
        plt.scatter(i,using_time)
        # plt.plot(x, using_time)
    plt.show()

test()