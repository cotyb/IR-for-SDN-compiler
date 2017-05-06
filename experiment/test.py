import re
import random
a = 'FWD(b)'
pattern = re.compile('FWD\\((.*)\\)')
to_sw = re.match(pattern, a).expand(r'\1')
print to_sw

print random.sample([1,2],3)