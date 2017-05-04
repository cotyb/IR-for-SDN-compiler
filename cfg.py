# function = ["dpi", "nat", "count", "ftp"]
# fun_switch = {'dpi':['a', 'b'], 'nat':['c', 'd'], 'count':['j'], 'ftp':['f']}
# fun_guard_update = {'dpi':['', ''], 'nat':['', ''], 'count':['', 'rv(CNT)'], 'ftp':['']}

function = ["dpi", "nat","ftp"]
fun_switch = {'dpi':['a', 'b'], 'nat':['c', 'd'], 'ftp':['f']}
fun_guard_update = {'dpi':['', ''], 'nat':['', ''],  'ftp':['']}


header_field = ["dstip", "srcip", "srcport", "dstport"]
header_field_1 = ["ip.dst", "ip.src", "tcp.src", "tcp.dst"]
global_resource = ['bw', 'NUM']