map      = {
	0    : {"a" : {1:["g1","u1"]}   , "b" : {2:["g2","u2"]}},
	1 	 : {"a" : {2:["g3","u3"]}	  , "b" : {1:["g4","u4"]}},
	2    : "",
}
for value in map.values():
    print value
    print type(value)