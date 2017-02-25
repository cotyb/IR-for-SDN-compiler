# -*- coding: utf-8 -*-

'''
	Finite state machine library.
'''

class anything_else_cls:
	'''
		This is a surrogate symbol which you can use in your finite state machines
		to represent "any symbol not in the official alphabet". For example, if your
		state machine's alphabet is {"a", "b", "c", "d", fsm.anything_else}, then
		you can pass "e" in as a symbol and it will be converted to
		fsm.anything_else, then follow the appropriate transition.
	'''
	def __str__(self):
		return "anything_else"
	def __repr__(self):
		return "anything_else"

# We use a class instance because that gives us control over how the special
# value gets serialised. Otherwise this would just be `object()`.
anything_else = anything_else_cls()

def key(symbol):
	'''Ensure `fsm.anything_else` always sorts last'''
	return (symbol is anything_else, symbol)

class OblivionError(Exception):
	'''
		This exception is thrown while `crawl()`ing an FSM if we transition to the
		oblivion state. For example while crawling two FSMs in parallel we may
		transition to the oblivion state of both FSMs at once. This warrants an
		out-of-bound signal which will reduce the complexity of the new FSM's map.
	'''
	pass

class fsm:
	'''
		A Finite State Machine or FSM has an alphabet and a set of states. At any
		given moment, the FSM is in one state. When passed a symbol from the
		alphabet, the FSM jumps to another state (or possibly the same state).
		A map (Python dictionary) indicates where to jump.
		One state is nominated as a starting state. Zero or more states are
		nominated as final states. If, after consuming a string of symbols,
		the FSM is in a final state, then it is said to "accept" the string.
		This class also has some pretty powerful methods which allow FSMs to
		be concatenated, alternated between, multiplied, looped (Kleene star
		closure), intersected, and simplified.
		The majority of these methods are available using operator overloads.
	'''
	def __setattr__(self, name, value):
		'''Immutability prevents some potential problems.'''
		raise Exception("This object is immutable.")

	def __init__(self, alphabet, states, initial, finals, map):
		'''
			`alphabet` is an iterable of symbols the FSM can be fed.
			`states` is the set of states for the FSM
			`initial` is the initial state
			`finals` is the set of accepting states
			`map` may be sparse (i.e. it may omit transitions). In the case of omitted
			transitions, a non-final "oblivion" state is simulated.
		'''

		# Validation. Thanks to immutability, this only needs to be carried out once.
		if not initial in states:
			raise Exception("Initial state " + repr(initial) + " must be one of " + repr(states))
		if not finals.issubset(states):
			raise Exception("Final states " + repr(finals) + " must be a subset of " + repr(states))
		

		# Initialise the hard way due to immutability.
		self.__dict__["alphabet"] = set(alphabet)
		self.__dict__["states"  ] = set(states)
		self.__dict__["initial" ] = initial
		self.__dict__["finals"  ] = set(finals)
		self.__dict__["map"     ] = map

	def accepts(self, input):
		'''
			Test whether the present FSM accepts the supplied string (iterable of
			symbols). Equivalently, consider `self` as a possibly-infinite set of
			strings and test whether `string` is a member of it.
			This is actually mainly used for unit testing purposes.
			If `fsm.anything_else` is in your alphabet, then any symbol not in your
			alphabet will be converted to `fsm.anything_else`.
		'''
		state = self.initial
		for symbol in input:
			if anything_else in self.alphabet and not symbol in self.alphabet:
				symbol = anything_else

			# Missing transition = transition to dead state
			if not (state in self.map and symbol in self.map[state]):
				return False

			state = self.map[state][symbol][0]
		return state in self.finals

	def __contains__(self, string):
		'''
			This lets you use the syntax `"a" in fsm1` to see whether the string "a"
			is in the set of strings accepted by `fsm1`.
		'''
		return self.accepts(string)

	def reduce(self):
		'''
			A result by Brzozowski (1963) shows that a minimal finite state machine
			equivalent to the original can be obtained by reversing the original
			twice.
		'''
		return reversed(reversed(self))

	def __repr__(self):
		string = "fsm("
		string += "alphabet = " + repr(self.alphabet)
		string += ", states = " + repr(self.states)
		string += ", initial = " + repr(self.initial)
		string += ", finals = " + repr(self.finals)
		string += ", map = " + repr(self.map)
		string += ")"
		return string

	def __str__(self):
		rows = []

		# top row
		row = ["", "name", "final?"]
		row.extend(str(symbol) for symbol in sorted(self.alphabet, key=key))
		rows.append(row)

		# other rows
		for state in self.states:
			row = []
			if state == self.initial:
				row.append("*")
			else:
				row.append("")
			row.append(str(state))
			if state in self.finals:
				row.append("True")
			else:
				row.append("False")
			for symbol in sorted(self.alphabet, key=key):
				if state in self.map and symbol in self.map[state]:
					row.append(str(self.map[state][symbol]))
				else:
					row.append("")
			rows.append(row)

		# column widths
		colwidths = []
		for x in range(len(rows[0])):
			colwidths.append(max(len(str(rows[y][x])) for y in range(len(rows))) + 1)

		# apply padding
		for y in range(len(rows)):
			for x in range(len(rows[y])):
				rows[y][x] = rows[y][x].ljust(colwidths[x])

		# horizontal line
		rows.insert(1, ["-" * colwidth for colwidth in colwidths])

		return "".join("".join(row) + "\n" for row in rows)

	def concatenate(*fsms):
		'''
			Concatenate arbitrarily many finite state machines together.
		'''
		alphabet = set().union(*[fsm.alphabet for fsm in fsms])

		def connect_all(i, substate):
			'''
				Take a state in the numbered FSM and return a set containing it, plus
				(if it's final) the first state from the next FSM, plus (if that's
				final) the first state from the next but one FSM, plus...
			'''
			result = {(i, substate)}
			while i < len(fsms) - 1 and substate in fsms[i].finals:
				i += 1
				substate = fsms[i].initial
				result.add((i, substate))
			return result

		# Use a superset containing states from all FSMs at once.
		# We start at the start of the first FSM. If this state is final in the
		# first FSM, then we are also at the start of the second FSM. And so on.
		initial = {}
		if len(fsms) > 0:
			initial.update(connect_all(0, fsms[0].initial))
		

		def final(state):
			'''If you're in a final state of the final FSM, it's final'''
			for (i, substate) in state:
				if i == len(fsms) - 1 and substate in fsms[i].finals:
					return True
			return False

		def follow(current, symbol):
			'''
				Follow the collection of states through all FSMs at once, jumping to the
				next FSM if we reach the end of the current one
				TODO: improve all follow() implementations to allow for dead metastates?
			'''
			next = set()
			for (i, substate) in current:
				fsm = fsms[i]
				if substate in fsm.map and symbol in fsm.map[substate]:
					next.update(connect_all(i, fsm.map[substate][symbol][0]))
			if len(next) == 0:
				raise OblivionError
			return frozenset(next)

		return crawl(alphabet, initial, final, follow).reduce()

	def __add__(self, other):
		'''
			Concatenate two finite state machines together.
			For example, if self accepts "0*" and other accepts "1+(0|1)",
			will return a finite state machine accepting "0*1+(0|1)".
			Accomplished by effectively following non-deterministically.
			Call using "fsm3 = fsm1 + fsm2"
		'''
		return self.concatenate(other)

	def star(self):
		'''
			If the present FSM accepts X, returns an FSM accepting X* (i.e. 0 or
			more Xes). This is NOT as simple as naively connecting the final states
			back to the initial state: see (b*ab)* for example.
		'''
		alphabet = self.alphabet

		initial = {self.initial}

		def follow(state, symbol):
			next = set()
			for substate in state:
				if substate in self.map and symbol in self.map[substate]:
					next.add(self.map[substate][symbol])

				# If one of our substates is final, then we can also consider
				# transitions from the initial state of the original FSM.
				if substate in self.finals \
				and self.initial in self.map \
				and symbol in self.map[self.initial]:
					next.add(self.map[self.initial][symbol])

			if len(next) == 0:
				raise OblivionError

			return frozenset(next)

		def final(state):
			return any(substate in self.finals for substate in state)

		return crawl(alphabet, initial, final, follow) | epsilon(alphabet)

	def times(self, multiplier):
		'''
			Given an FSM and a multiplier, return the multiplied FSM.
		'''
		if multiplier < 0:
			raise Exception("Can't multiply an FSM by " + repr(multiplier))

		alphabet = self.alphabet

		# metastate is a set of iterations+states
		initial = {(self.initial, 0)}

		def final(state):
			'''If the initial state is final then multiplying doesn't alter that'''
			for (substate, iteration) in state:
				if substate == self.initial \
				and (self.initial in self.finals or iteration == multiplier):
					return True
			return False

		def follow(current, symbol):
			next = []
			for (substate, iteration) in current:
				if iteration < multiplier \
				and substate in self.map \
				and symbol in self.map[substate]:
					next.append((self.map[substate][symbol], iteration))
					# final of self? merge with initial on next iteration
					if self.map[substate][symbol][0] in self.finals:
						next.append((self.initial, iteration + 1))
			if len(next) == 0:
				raise OblivionError
			return frozenset(next)

		return crawl(alphabet, initial, final, follow).reduce()

	def __mul__(self, multiplier):
		'''
			Given an FSM and a multiplier, return the multiplied FSM.
		'''
		return self.times(multiplier)

	def union(*fsms):
		'''
			Treat `fsms` as a collection of arbitrary FSMs and return the union FSM.
			Can be used as `fsm1.union(fsm2, ...)` or `fsm.union(fsm1, ...)`. `fsms`
			may be empty.
		'''
		return parallel(fsms, any)

	def __or__(self, other):
		'''
			Alternation.
			Return a finite state machine which accepts any sequence of symbols
			that is accepted by either self or other. Note that the set of strings
			recognised by the two FSMs undergoes a set union.
			Call using "fsm3 = fsm1 | fsm2"
		'''
		return self.union(other)

	def intersection(*fsms):
		'''
			Intersection.
			Take FSMs and AND them together. That is, return an FSM which
			accepts any sequence of symbols that is accepted by both of the original
			FSMs. Note that the set of strings recognised by the two FSMs undergoes
			a set intersection operation.
			Call using "fsm3 = fsm1 & fsm2"
		'''
		return parallel(fsms, all)

	def __and__(self, other):
		'''
			Treat the FSMs as sets of strings and return the intersection of those
			sets in the form of a new FSM. `fsm1.intersection(fsm2, ...)` or
			`fsm.intersection(fsm1, ...)` are acceptable.
		'''
		return self.intersection(other)

	def symmetric_difference(*fsms):
		'''
			Treat `fsms` as a collection of sets of strings and compute the symmetric
			difference of them all. The python set method only allows two sets to be
			operated on at once, but we go the extra mile since it's not too hard.
		'''
		return parallel(fsms, lambda accepts: (accepts.count(True) % 2) == 1)

	def __xor__(self, other):
		'''
			Symmetric difference. Returns an FSM which recognises only the strings
			recognised by `self` or `other` but not both.
		'''
		return self.symmetric_difference(other)

	def everythingbut(self):
		'''
			Return a finite state machine which will accept any string NOT
			accepted by self, and will not accept any string accepted by self.
			This is more complicated if there are missing transitions, because the
			missing "dead" state must now be reified.
		'''
		alphabet = self.alphabet

		initial = {0 : self.initial}

		def follow(current, symbol):
			next = {}
			if 0 in current and current[0] in self.map and symbol in self.map[current[0]]:
				next[0] = self.map[current[0]][symbol]
			return next

		# state is final unless the original was
		def final(state):
			return not (0 in state and state[0] in self.finals)

		return crawl(alphabet, initial, final, follow).reduce()

	def reversed(self):
		'''
			Return a new FSM such that for every string that self accepts (e.g.
			"beer", the new FSM accepts the reversed string ("reeb").
		'''
		alphabet = self.alphabet
		#print alphabet
		# Start from a composite "state-set" consisting of all final states.
		# If there are no final states, this set is empty and we'll find that
		# no other states get generated.
		initial = frozenset(self.finals)
		#print "reversed"
		# Find every possible way to reach the current state-set
		# using this symbol.
		def follow(current, symbol):
			a=[]  #a为所有可到达current中状态的状态集合
			c=[]  #c为a中所有状态对应的经symbol到达的状态
			b=[]  #b为每次经过比较划分出的guard与update完全相同的几组状态集合 全部存入next中
			next=[] 
			gandup=[]  #gandup为guard与update的存储集合
			result={}  #next与gandup一起存入result作为函数的返回值用于之后map的计算
			i=0
			for i in range(len(self.states)):
				if i in self.finals and i not in self.map.keys():
					self.map[i]=""
			for i in range(len(self.states)):                             #通过for循环得到集合a与c
				for state in current:
					if symbol in self.map[i] and state  in self.map[i][symbol].keys():
						a.append(i)
						c.append(state)
			while len(a)!=0:                                              #对集合a中元素进行分类 guard与update相同的为一组存入next中
				#print self.map[a[0]],symbol
				#print self.map[a[0]][symbol][c[0]][0]
				guard=self.map[a[0]][symbol][c[0]][0]
				update=self.map[a[0]][symbol][c[0]][1]
				gandup.append(guard)
				gandup.append(update)
				i=0
				for i in range(len(a)):
					if self.map[a[i]][symbol][c[i]][0]==guard and self.map[a[i]][symbol][c[i]][1]==update:
						b.append(a[i]) 
				#print "b",b
				i=0
				while i in range(len(a)):
					if a[i] in b:
						del a[i]
						del c[i]
						i=0
					else:
						i+=1
				next.append(b)
				#print "next",next,"gandup",gandup
				
				b=[]
				
			
			result[0]=next
			result[1]=gandup
			return result
		
		def change(current,symbol):
			a=[]  #a为所有可到达current中状态的状态集合
			c=[]  #c为a中所有状态对应的经symbol到达的状态
			d=[]
			e=[]
			chang=[]
			i=0
			for i in range(len(self.states)):
				if i in self.finals and i not in self.map.keys():
					self.map[i]=""
			
			for i in range(len(self.states)):                             #通过for循环得到集合a与c
				for state in current:
					if symbol in self.map[i] and state  in self.map[i][symbol].keys():
						a.append(i)
						c.append(state)
		#	print "a",a
			for i in range(len(a)):
				#print "111111",self.map[a[i]][symbol][c[i]]
				if len(self.map[a[i]][symbol][c[i]])>2:
					d.append(a[i])
					e.append(c[i])
		#	print "d",d,"e",e
			for i in range(len(d)):
				chang.append(self.map[d[i]][symbol][e[i]])
		#	print chang
			return chang
			
		# A state-set is final if the initial state is in it.
		def final(state):
			return self.initial in state

		# Man, crawl() is the best!
		return redu(alphabet, initial, final, follow,change)
		# Do not reduce() the result, since reduce() calls us in turn

	def __reversed__(self):
		'''
			Return a new FSM such that for every string that self accepts (e.g.
			"beer", the new FSM accepts the reversed string ("reeb").
		'''
		return self.reversed()

	def islive(self, state):
		'''A state is "live" if a final state can be reached from it.'''
		reachable = [state]
		i = 0
		while i < len(reachable):
			current = reachable[i]
			if current in self.finals:
				return True
			if current in self.map:
				for symbol in self.map[current]:
					next = self.map[current][symbol]
					if next not in reachable:
						reachable.append(next)
			i += 1
		return False

	def empty(self):
		'''
			An FSM is empty if it recognises no strings. An FSM may be arbitrarily
			complicated and have arbitrarily many final states while still recognising
			no strings because those final states may all be inaccessible from the
			initial state. Equally, an FSM may be non-empty despite having an empty
			alphabet if the initial state is final.
		'''
		return not self.islive(self.initial)

	def strings(self):
		'''
			Generate strings (lists of symbols) that this FSM accepts. Since there may
			be infinitely many of these we use a generator instead of constructing a
			static list. Strings will be sorted in order of length and then lexically.
			This procedure uses arbitrary amounts of memory but is very fast. There
			may be more efficient ways to do this, that I haven't investigated yet.
			You can use this in list comprehensions.
		'''

		# Many FSMs have "dead states". Once you reach a dead state, you can no
		# longer reach a final state. Since many strings may end up here, it's
		# advantageous to constrain our search to live states only.
		livestates = set(state for state in self.states if self.islive(state))

		# We store a list of tuples. Each tuple consists of an input string and the
		# state that this input string leads to. This means we don't have to run the
		# state machine from the very beginning every time we want to check a new
		# string.
		strings = []

		# Initial entry (or possibly not, in which case this is a short one)
		cstate = self.initial
		cstring = []
		if cstate in livestates:
			if cstate in self.finals:
				yield cstring
			strings.append((cstring, cstate))

		# Fixed point calculation
		i = 0
		while i < len(strings):
			(cstring, cstate) = strings[i]
			if cstate in self.map:
				for symbol in sorted(self.map[cstate], key=key):
					nstate = self.map[cstate][symbol]
					nstring = cstring + [symbol]
					if nstate in livestates:
						if nstate in self.finals:
							yield nstring
						strings.append((nstring, nstate))
			i += 1

	def __iter__(self):
		'''
			This allows you to do `for string in fsm1` as a list comprehension!
		'''
		return self.strings()

	def equivalent(self, other):
		'''
			Two FSMs are considered equivalent if they recognise the same strings.
			Or, to put it another way, if their symmetric difference recognises no
			strings.
		'''
		return (self ^ other).empty()

	def __eq__(self, other):
		'''
			You can use `fsm1 == fsm2` to determine whether two FSMs recognise the
			same strings.
		'''
		return self.equivalent(other)

	def different(self, other):
		'''
			Two FSMs are considered different if they have a non-empty symmetric
			difference.
		'''
		return not (self ^ other).empty()

	def __ne__(self, other):
		'''
			Use `fsm1 != fsm2` to determine whether two FSMs recognise different
			strings.
		'''
		return self.different(other)

	def difference(*fsms):
		'''
			Difference. Returns an FSM which recognises only the strings
			recognised by the first FSM in the list, but none of the others.
		'''
		return parallel(fsms, lambda accepts: accepts[0] and not any(accepts[1:]))

	def __sub__(self, other):
		return self.difference(other)

	def cardinality(self):
		'''
			Consider the FSM as a set of strings and return the cardinality of that
			set, or raise an OverflowError if there are infinitely many
		'''
		num_strings = {}
		def get_num_strings(state):
			# Many FSMs have at least one oblivion state
			if self.islive(state):
				if state in num_strings:
					if num_strings[state] is None: # "computing..."
						# Recursion! There are infinitely many strings recognised
						raise OverflowError(state)
					return num_strings[state]
				num_strings[state] = None # i.e. "computing..."

				n = 0
				if state in self.finals:
					n += 1
				if state in self.map:
					for symbol in self.map[state]:
						n += get_num_strings(self.map[state][symbol][0])
				num_strings[state] = n

			else:
				# Dead state
				num_strings[state] = 0

			return num_strings[state]

		return get_num_strings(self.initial)

	def __len__(self):
		'''
			Consider the FSM as a set of strings and return the cardinality of that
			set, or raise an OverflowError if there are infinitely many
		'''
		return self.cardinality()

	def isdisjoint(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if they are disjoint
		'''
		return (self & other).empty()

	def issubset(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a subset
			of `other`... `self` recognises no strings which `other` doesn't.
		'''
		return (self - other).empty()

	def __le__(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a subset
			of `other`... `self` recognises no strings which `other` doesn't.
		'''
		return self.issubset(other)

	def ispropersubset(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a proper
			subset of `other`.
		'''
		return self <= other and self != other

	def __lt__(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a strict
			subset of `other`.
		'''
		return self.ispropersubset(other)

	def issuperset(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a
			superset of `other`.
		'''
		return (other - self).empty()

	def __ge__(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a
			superset of `other`.
		'''
		return self.issuperset(other)

	def ispropersuperset(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a proper
			superset of `other`.
		'''
		return self >= other and self != other

	def __gt__(self, other):
		'''
			Treat `self` and `other` as sets of strings and see if `self` is a
			strict superset of `other`.
		'''
		return self.ispropersuperset(other)

	def copy(self):
		'''
			For completeness only, since `set.copy()` also exists. FSM objects are
			immutable, so I can see only very odd reasons to need this.
		'''
		return fsm(
			alphabet = self.alphabet,
			states   = self.states,
			initial  = self.initial,
			finals   = self.finals,
			map      = self.map,
		)

	def derive(self, input):
		'''
			Compute the Brzozowski derivative of this FSM with respect to the input
			string of symbols. <https://en.wikipedia.org/wiki/Brzozowski_derivative>
			If any of the symbols are not members of the alphabet, that's a KeyError.
			If you fall into oblivion, then the derivative is an FSM accepting no
			strings.
		'''
		try:
			# Consume the input string.
			state = self.initial
			for symbol in input:
				if not symbol in self.alphabet:
					if not anything_else in self.alphabet:
						raise KeyError(symbol)
					symbol = anything_else

				# Missing transition = transition to dead state
				if not (state in self.map and symbol in self.map[state]):
					raise OblivionError

				state = self.map[state][symbol][0]

			# OK so now we have consumed that string, use the new location as the
			# starting point.
			return fsm(
				alphabet = self.alphabet,
				states   = self.states,
				initial  = state,
				finals   = self.finals,
				map      = self.map,
			)

		except OblivionError:
			# Fell out of the FSM. The derivative of this FSM is the empty FSM.
			return null(self.alphabet)

def null(alphabet):
	'''
		An FSM accepting nothing (not even the empty string). This is
		demonstrates that this is possible, and is also extremely useful
		in some situations
	'''
	return fsm(
		alphabet = alphabet,
		states   = {0},
		initial  = 0,
		finals   = set(),
		map      = {
			0: dict([(symbol, 0) for symbol in alphabet]),
		},
	)

def epsilon(alphabet):
	'''
		Return an FSM matching an empty string, "", only.
		This is very useful in many situations
	'''
	return fsm(
		alphabet = alphabet,
		states   = {0},
		initial  = 0,
		finals   = {0},
		map      = {},
	)

def parallel(fsms, test):
	'''
		Crawl several FSMs in parallel, mapping the states of a larger meta-FSM.
		To determine whether a state in the larger FSM is final, pass all of the
		finality statuses (e.g. [True, False, False] to `test`.
	'''
	alphabet = set().union(*[fsm.alphabet for fsm in fsms])

	initial = dict([(i,fsm.initial) for (i, fsm) in enumerate(fsms)])

	# dedicated function accepts a "superset" and returns the next "superset"
	# obtained by following this transition in the new FSM
	def follow(current, symbol):
		next = {}
		#print "current1",current,symbol
		for i in range(len(fsms)):
			if i in current \
			and current[i] in fsms[i].map \
			and symbol in fsms[i].map[current[i]]\
			and  fsms[i].map[current[i]][symbol]!="":
				next[i] = fsms[i].map[current[i]][symbol].keys()[0]
		if len(next.keys()) == 0:
			raise OblivionError
		#print "next",next,symbol
		return next
	
	def gandup(current,symbol):                   #计算guard与update
		gandup=[]
		guard={}
		update={}
		next=follow(current, symbol)
		#print next
		if 0 not in next.keys() and fsms[1].map[current[1]][symbol].values()[0]!="":
			gandup=fsms[1].map[current[1]][symbol].values()[0]
			#print "11111111111111"
		elif 1 not in next.keys() and fsms[0].map[current[0]][symbol].values()[0]!="":
			gandup=fsms[0].map[current[0]][symbol].values()[0]
			#print "222222222222"
		elif 0 in next.keys() and 1 in next.keys():
			if	 current[0]not in fsms[0].finals \
			and current[1]not in fsms[1].finals \
			and  fsms[1].map[current[1]][symbol]!="" \
			and fsms[0].map[current[0]][symbol]!=""\
			and symbol in fsms[0].map[current[0]].keys() \
			and symbol in fsms[1].map[current[1]].keys() :
				#print "a",symbol
				a=[len(fsms[1].map[current[1]][symbol].values()[0])/2,len(fsms[0].map[current[0]][symbol].values()[0])/2]
				
				for i in range(a[0]*a[1]):
					guard[i]=""
					update[i]=""
				
				for i in range(len(fsms)):
					if i in current \
					and current[i] in fsms[i].map \
					and symbol in fsms[i].map[current[i]]:
				#		print "i",i
						k=0
						m=0
						#print "77777777777777777777777777777777777777777777777777777777777777"
						while k<a[0]*a[1] and i==0:
							for j in range(a[0]):
								if guard[k+j]=="" and fsms[0].map[current[0]][symbol].values()[0][m]!="" :
									guard[k+j]=fsms[0].map[current[0]][symbol].values()[0][m]
								if update[k+j]==""and fsms[0].map[current[0]][symbol].values()[0][m+1]!="":
									update[k+j]=fsms[0].map[current[0]][symbol].values()[0][m+1]
							#	print "update",update,"k",k,"j",j,a[0]
							m+=2
							k=k+a[0]
				#			print "update",update,"k",k,"j",j,"mm",m
						
						k=0
						m=0
						while k<a[0]*a[1]and i==1:
							#print "1111111",k
							for j in range(a[0]):
				#				print "22222",j,fsms[1].map[current[1]][symbol].values()[0][m+1]
								if fsms[1].map[current[1]][symbol].values()[0][m]!="":
									guard[k+j]=guard[k+j]+" and "+fsms[1].map[current[1]][symbol].values()[0][m]
									update[k+j]= update[k+j]+" and "+fsms[1].map[current[1]][symbol].values()[0][m+1]
								#print "333333333"
								m+=2
							#	print "update",update,"k",k,"j",j,m
							#print "update",update,"k",k,"j",j,"m",m
							k=k+a[0]
							m=0	
					k=a[0]*a[1]+1
				#	print k
				i=0
				j=0
				while i <2*a[0]*a[1]:
					gandup.append(guard[j])
					gandup.append(update[j])
					j+=1
					i+=2
		return gandup		
	# Determine the "is final?" condition of each substate, then pass it to the
	# test to determine finality of the overall FSM.
	def final(state):
		accepts = [i in state and state[i] in fsm.finals for (i, fsm) in enumerate(fsms)]
		return test(accepts)

	return crawl(alphabet, initial, final, follow,gandup).reduce()

def crawl(alphabet, initial, final, follow, gandup):   #交并补函数中计算得到的fsm 主要是map 的函数
	'''
		Given the above conditions and instructions, crawl a new unknown FSM,
		mapping its states, final states and transitions. Return the new FSM.
		This is a pretty powerful procedure which could potentially go on
		forever if you supply an evil version of follow().
	'''
	#print "not reduce"
	#print "alphabet",sorted(alphabet, key=key)
	states = [initial]
	finals = set()
	map = {}

	# iterate over a growing list
	i = 0
	while i < len(states):
		state = states[i]

		# add to finals
		if final(state):
			finals.add(i)

		# compute map for this state
		map[i] = {}
		for symbol in sorted(alphabet, key=key):
			try:
				#print "88888888888",state,symbol
				next = follow(state, symbol)
				#print "00000000000000",states
				gandu= gandup(state,symbol)
				#print "gandup",gandu
				try:
					j = states.index(next)
				except ValueError:
					j = len(states)
					states.append(next)
					
			except OblivionError:
				# Reached an oblivion state. Don't list it.
				continue

			map[i][symbol]={j:gandu}
			#print map[i][symbol],i,symbol
			#print "6666666666666666666",state,symbol,next,map[i][symbol]	
		i += 1
	return fsm(
		alphabet = alphabet,
		states   = range(len(states)),
		initial  = 0,
		finals   = finals,
		map      = map,
	)
def redu(alphabet, initial, final, follow,change):         #reversed函数中计算map
	states = [initial]
	finals = set()
	map = {}
	#print "reduce"
	# iterate over a growing list
	i = 0
	while i < len(states):
		
		state = states[i]

			# add to finals
		if final(state):
			finals.add(i)

			# compute map for this state
		map[i] = {}
		for symbol in sorted(alphabet, key=key):	#计算map根据之前定义的reversed（）中follow函数得到的result进行计算
			result=follow(state,symbol)
			
			change1=change(state,symbol)
			#print state,symbol
			a=result[0]
			gandup=result[1]
			while len(a)>0:
				try:
					next =set(a[0])
					guard =gandup[0]
					update =gandup[1]
					try:
						j = states.index(next)
					except ValueError:
						j = len(states)
						states.append(next)
				except OblivionError:
				# Reached an oblivion state. Don't list it.
					continue
				if symbol not in map[i].keys():
					map[i][symbol]={j:[guard,update]}
				else:
					map[i][symbol][j]=[guard,update]
				del a[0]
				del gandup[1]
				del gandup[0]
			#print "map",map
			
			for k in range(len(change1)):
				#print "hhhhhhhhhhhhhhhhhhhhhhh" ,change1
				#print "states",states
				for j in range(len(states)):
			#		print "j",j,map[i][symbol]
					if j in map[i][symbol].keys()and map[i][symbol][j][0]==change1[k][0] and map[i][symbol][j][1]==change1[k][1]:
			#			print "8888888888",map[i][symbol][j]
						map[i][symbol][j]=change1[k]
			#			print "222222222222",change1,"3333333333",map[i][symbol]
				#print"66666666666" ,len(change1),
				#print "states",states     
				#print "finals",finals
				#print "initial",initial
		i += 1
	#print "88888888888888",states
	#print  fsm(   								#打印每次reversed得到的状态机   可注释掉 
	#	alphabet = alphabet,
	#	states   = range(len(states)),
	#	initial  = 0,
	#	finals   = finals,
	#	map      = map,
	#)	
	return fsm(
			alphabet = alphabet,
			states   = range(len(states)),
			initial  = 0,
			finals   = finals,
			map      = map,
		)
if __name__ == "__main__":
	a = fsm(
			alphabet = {'FWD(.)', 'FWD(z)', 'FWD(e)'},
			states   = {1, 2, 3},
			initial  = 1,
			finals   = {3},
			map      = {
				1: {'FWD(.)': {1: ['bw[s1][s2]>100MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}, 
				'FWD(z)': {2: ['bw[s1][s2]>100MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}},
				2: {'FWD(.)': {2: ['bw[s1][s2]>100MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}, 'FWD(e)': {3: ['', '']},}
				
			},
		)
	b = fsm(
			alphabet = {'FWD(.)', 'FWD(a)', 'FWD(b)', 'FWD(e)', 'FWD(.) && dpi'},
			states   = {1, 2, 3, 4, 5},
			initial  = 1,
			finals   = {5},
			map      = {
				1: {'FWD(.)': {1: ['bw[s1][s2]<50MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}, 'FWD(a)': {3: [' (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 20)  && bw[s1][s2]<50MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}, 'FWD(b)': {4: [' (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 20)  && bw[s1][s2]<50MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}}, 
				2: {'FWD(.)': {2: ['bw[s1][s2]<50MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}, 'FWD(e)': {5: ['', '']}},
				3: {'FWD(.) && dpi': {2: [' && bw[s1][s2]<50MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}}, 
				4: {'FWD(.) && dpi': {2: [' && bw[s1][s2]<50MB/s', 's1=s2, bw[s1][s2]-=rate, s2=rv(FWD)']}},
			},
		)
	c=fsm(
			alphabet = {'FWD(a)', 'FWD(.) && nat', 'FWD(b)', 'FWD(c)', 'FWD(.)', 'FWD(d)', 'FWD(e)', 'FWD(.) && dpi'},
			states   = {1, 2, 3, 4, 5, 6, 7, 8},
			initial  = 1,
			finals   = {8},
			map      = {1: {'FWD(.)': {1: ['', '']}, 'FWD(a)': {4: [' (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 80) ', '']}, 'FWD(b)': {5: [' (ip.src = 192.168.1.1 and ip.dst = 192.168.1.2 and tcp.dst = 80) ', '']}}, 
						2: {'FWD(.)': {2: ['', '']}, 'FWD(e)': {8: ['', '']}}, 
						3: {'FWD(.)': {3: ['', '']}, 'FWD(d)': {7: ['', '']}, 'FWD(c)': {6: ['', '']}},
						4: {'FWD(.) && dpi': {3: ['', '']}},
						5: {'FWD(.) && dpi': {3: ['', '']}}, 
						6: {'FWD(.) && nat': {2: ['', '']}}, 
						7: {'FWD(.) && nat': {2: ['', '']}}},
		)
	d=fsm(
			alphabet = {'FWD(.)', 'FWD(e)'},
			states   = {1, 2},
			initial  = 1,
			finals   = {2},
			map      = {1: {'FWD(.)': {1: ['', '']}, 
			'FWD(e)': {2: ['dstip = 10.0.0.6/32 && (srcport = 53) && (srcip = 10.0.0.6/32) && (orphan[dstip,rdata] = (False,)) && (susp[dstip] = (4,)) ', 
			'{[orphan[dstip,rdata] <- (True,) ; susp[dstip] <- 1 ; blacklist[dstip] <- (True,)]}',
			'dstip = 10.0.0.6/32 && (srcport = 53) && (srcip = 10.0.0.6/32) && (orphan[dstip,rdata] = (False,)) && (susp[dstip] != (4,)) ',
			'{[orphan[dstip,rdata] <- (True,) ; susp[dstip] <- 1]}', 
			'dstip = 10.0.0.6/32 && (srcport = 53) && (srcip = 10.0.0.6/32) && (orphan[dstip,rdata] != (False,)) && (orphan[srcip,dstip] = (True,)) ', 
			'{[orphan[srcip,dstip] <- (False,) ; susp[srcip] <- -1]}',
			'dstip = 10.0.0.6/32 && (srcport = 53) && (srcip = 10.0.0.6/32) && (orphan[dstip,rdata] != (False,)) && (orphan[srcip,dstip] != (True,)) ',
			'{[id <- id]}', 'dstip = 10.0.0.6/32 && (srcport = 53) && (srcip != 10.0.0.6/32) && (orphan[dstip,rdata] = (False,)) && (susp[dstip] = (4,)) ', 
			'{[orphan[dstip,rdata] <- (True,) ; susp[dstip] <- 1 ; blacklist[dstip] <- (True,)]}', 'dstip = 10.0.0.6/32 && (srcport = 53) && (srcip != 10.0.0.6/32) && (orphan[dstip,rdata] = (False,)) && (susp[dstip] != (4,)) ', 
			'{[orphan[dstip,rdata] <- (True,) ; susp[dstip] <- 1]}', 
			'dstip = 10.0.0.6/32 && (srcport = 53) && (srcip != 10.0.0.6/32) && (orphan[dstip,rdata] != (False,)) ',
			'{[id <- id]}', 'dstip = 10.0.0.6/32 && (srcport != 53) && (srcip = 10.0.0.6/32) && (orphan[srcip,dstip] = (True,)) ', 
			'{[orphan[srcip,dstip] <- (False,) ; susp[srcip] <- -1]}',
			'dstip = 10.0.0.6/32 && (srcport != 53) && (srcip = 10.0.0.6/32) && (orphan[srcip,dstip] != (True,)) ', 
			'{[id <- id]}', 'dstip = 10.0.0.6/32 && (srcport != 53) && (srcip != 10.0.0.6/32) ', 
			'{[id <- id]}', 
			'dstip != 10.0.0.6/32 && (srcip = 10.0.0.6/32) && (orphan[srcip,dstip] = (True,)) ',
			'{[orphan[srcip,dstip] <- (False,) ; susp[srcip] <- -1]}', 
			'dstip != 10.0.0.6/32 && (srcip = 10.0.0.6/32) && (orphan[srcip,dstip] != (True,)) ', 
			'{[id <- id]}', 'dstip != 10.0.0.6/32 && (srcip != 10.0.0.6/32) ', '{[id <- id]}']}}},
		)

	print a.union(b)
	print c.union(d)
	

	#a，b相并
	#使用时需要定义如上数据类型的fsm  交为 a.intersection(b)  补为 a.symmetric_difference(b) 化简为a.reduce()