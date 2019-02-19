#!/usr/bin/python
# -*- encoding: utf-8 -*-

class Symbol:
	# field name: String
	# (no methods)
	
	def __init__(self, name):
		# name: String		
		self.name = name;
	
	def __str__(self):
		return self.name;

	def __eq__(self, other) :
		return self.name == other.name

class Rule:
	# field lhs: Symbol
	# field rhs: list of Symbol
	# (no methods)
	
	def __init__(self, lhs, rhs):
		# lhs: Symbol
		# rhs: list of Symbol
		
		self.lhs = lhs;
		self.rhs = rhs;
		
	def __str__(self):
		return str(self.lhs) + " --> [" + ",".join([str(s) for s in self.rhs]) + "]";

class Grammar:
	# field symbols: list of Symbol
	# field axiom: Symbol
	# field rules: list of Rule
	# field nonTerminals: set of Symbol
	# method createNewSymbol: String -> Symbol
	# method isNonTerminal: Symbol -> Boolean
		
	def __init__(self, symbols, axiom, rules):
		# symbols: list of Symbol
		# axiom: Symbol
		# rules: list of Rule
		
		self.symbols = symbols
		self.axiom = axiom
		self.rules = rules
		
		self.nonTerminals = set()
		for rule in rules :
			self.nonTerminals.add(rule.lhs)
	
	# Returns a new symbol (with a new name build from the argument)
	def createNewSymbol(self, symbolName):
		# symbolName: String
		
		name = symbolName
		
		ok = False;
		while (ok == False):
			ok = True
			for s in self.symbols :
				if s.name == name :
					ok = False
					break
			
			if ok == False:
				name = name + "'"
		
		return Symbol(name)
		
	def isNonTerminal(self, symbol):
		# symbol: Symbol
		
		return symbol in self.nonTerminals;
		
	def __str__(self):
		return "{" +\
			"symbols = [" + ",".join([str(s) for s in self.symbols]) + "]; " +\
			"axiom = " + str(self.axiom) + "; " +\
			"rules = [" + ", ".join(str(r) for r in self.rules) + "]" +\
			"}";

# Definition of the symbols
symE = Symbol("E")
symT = Symbol("T")
symF = Symbol("F")
symPlus = Symbol("+")
symTimes = Symbol("*")
symOpenBracket = Symbol("(")
symClosingBracket = Symbol(")")
symTerminalA = Symbol("a")

# Definition of the grammar
grammar = Grammar(
	# Alphabet
	[symE, symT, symF, symPlus, symTimes, symOpenBracket, symClosingBracket, symTerminalA],
	
	# Axiom
	symE,
	
	# List of rules
	[
		Rule(symE, [symE, symPlus, symT]), 		# E --> E+T
		Rule(symE, [symT]), 					# E --> T
		Rule(symT, [symT, symTimes, symF]), 	# T --> T*F
		Rule(symT, [symF]), 					# T --> F
		Rule(symF, [symOpenBracket, symE, symClosingBracket]), 	# F --> (E)
		Rule(symF, [symTerminalA]) 				# F --> a
	]
)

# Return (l1, l2) where l1 is the list of rewriting rules of g for symbol and l2 are the other rules of g
def getRules(g, symbol):
	# g: Grammar
	# symbol: Symbol
	l1 = []
	l2 = []
	for rule in g.rules :
		if rule.lhs == symbol :
			l1.append(rule)
		else :
			l2.append(rule)
	
	return (l1, l2)

# Return (l1, l2) where l1 are the (directly) recursive rules of l and l2 are the other rules of l
def getLeftRecursiveRules(l):
	# l: list of Rule
	# symbol: Symbol
	l1 = []
	l2 = []
	for rule in l :
		if rule.lhs == rule.rhs[0]:
			l1.append(rule)
		else :
			l2.append(rule)
	
	return (l1, l2)
	
# Return the grammar obtained by removing from g the direct left recursion for symbol
# The original grammar g should not be modified (a new one should be defined)
def removeDirectRecursionSymbol(g, symbol):
	# g: Grammar
	# symbol: Symbol
	
	# First, separate (using the previously defined functions) the rules of interest
	sym_rules, others_1 = getRules(g, symbol)

	rec_rules, others_2 = getLeftRecursiveRules(sym_rules)
	
	# Then, create a new list of rules (for the new grammar) containing the rules we don't need to change
	standars_rules = others_1 + others_2;
	
	# Add the new derecursified rules
	"""
	Algorithm:
	A −→ Aα1 | Aα2 | . . . | Aαm | β 1 | . . . | βk
	becomes
	A  −→ β1 A′ | β2 A′ | . . . | βk A′
	A′  −→ α1  A′ | α2 A′ | . . . | αm A′ | ε
	"""
	pass;
	
	# Create and return the new grammar
	pass;

# Return the grammar obtained by removing all direct left recursion in g
# The original grammar g should not be modified (a new one should be defined)
def removeDirectRecursion(g):
	# g: Grammar
	
	pass;

print ("Élimination de la récursivité directe :")
print ("")
print (grammar)
print ("")
print (removeDirectRecursion(grammar))

# Return the grammar obtained by removing all left recursion in g (direct and indirect)
# The original grammar g should not be modified (a new one should be defined)
def removeRecursion(g):
	# g: Grammar

	"""
	Algorithm:
	Build an (arbitrary) order over non-terminals
	For A1 in V,
	   For A2 < A1,
		  Replace any rule A1 −→ A2 α with A1 −→  δ1 α | δ2 α | . . . |δh α
		  (for A2 −→ δ1 | δ2 | . . . | δh)
	   Remove direct recursion in A1-productions
	"""
	pass;

print ("")
print ("Élimination de toutes les récursivités :")
print ("")

# Definition of the symbols
symS = Symbol("S")
symA = Symbol("A")
symTerminalA = Symbol("a")
symTerminalB = Symbol("b")
symTerminalC = Symbol("c")
symTerminalD = Symbol("d")

# Definition of the grammar
grammar = Grammar(
	# Alphabet
	[symS, symA, symTerminalA, symTerminalB, symTerminalC, symTerminalD],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symTerminalA]), 	# S --> Aa
		Rule(symS, [symTerminalB]), 		# S --> b
		Rule(symA, [symA, symTerminalC]), 	# A --> Ac
		Rule(symA, [symS, symTerminalD]), 	# A --> Sd
		Rule(symA, [symTerminalC]), 		# A --> C
	]
)

print (grammar)
print ("")
print (removeRecursion(grammar))

# Furhter testing of the removeRecursion function can be performed on the grammar from exercice 3
