a = "1,2:3"
b,c = a.split(",")
print b,c

a = {1:2,3:4}
for b in a:
    print b


a = [set([1, 'S']), set([3]), set([2]), set([5, 'T']), set([4])]
print type(a[-1].pop())


print " 1" in ["1","2"]

line = 'fsdlafjsdlfkfoofsad;lfjsd;fsadf'
import re
print re.split(r'foo | fjs' , line)

a = ' .*dpi.*nat.*'
print a.__contains__('dpi')
b = a.replace('dpi','1')
print b

a = [1,2]
a.insert(-1,3)
print a

a = [2,3,4]
b = [2,3]
a.extend(b)
print a

a = 1
print "%s" %a

