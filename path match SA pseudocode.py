def accepts(path, start, state):
    if len(path) == 0:
	    for edge in sa.edges:
			if start == edge.start and edge.end == sa.end:
				return True
		return False
	for edge in sa.edges:
		init_sate_configuration()
		if edge.start = start:
			handle_packet_guard()
			handle_global_guard()
			handle_local_guard()
			old_state = state
			update_packet_update()
			update_global_update()
			update_local_update()
			next_sw = get_next_hop(edge.action)
			if next_sw == '.':
				return accepts(path[1:], edge.end, state)
			elif next_sw == path[0]:
				return accepts(path[1:], edge.end, state)
			else:
				state = old_state
				continue
