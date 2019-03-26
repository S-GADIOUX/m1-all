#! /usr/bin/python
# -*- encoding: utf8 -*-

# -----
# TP Implémentation de l'algorithme Earley (avec fonction pred)
# 
# 1) Familiarisez-vous avec le code.
# 2) Implémentez les fonctions incomplètes (celles contenant le mot-clef "pass").
# 3) Expliquez s'il existe des contraintes sur la grammaire pour que votre algorithme fonctionne (ou si, au contraire, il marche dans tous les cas) ; si oui, pour les plus avancés d'entre-vous, il est envisageable de produire une fonction permettant de tester si une grammaire donnée satisfait ces contraintes.
# 4) Faites une copie du fichier et modifiez le code pour retourner (et afficher de manière lisible) un arbre syntaxique lorsque l'analyse est réussie (n'hésitez pas pour cela à faire évoluer les classes existantes).
# Vous avez évidemment le droit de définir des fonctions auxiliaires ou d'ajouter des méthodes aux classes, mais tout votre code doit être soigneusement commenté :
# – le rôle ou la valeur de retour de chaque fonction doit être indiqué, ainsi que son fonctionnement ;
# – toute création de variable doit être accompagnée d'un commentaire sur son rôle/sens.

class Symbol:
	# field name: String
	# (no methods)
	
	def __init__(self, name):
		# name: String
		
		self.name = name;
	
	def __str__(self):
		return self.name;

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
	# field name: String
	# method createNewSymbol: String -> Symbol
	# method isNonTerminal: Symbol -> Boolean
		
	def __init__(self, symbols, axiom, rules, name):
		# symbols: list of Symbol
		# axiom: Symbol
		# rules: list of Rule
		# name: String
		
		self.symbols = symbols;
		self.axiom = axiom;
		self.rules = rules;
		self.name = name;
		
		self.nonTerminals = set();
		for rule in rules:
			self.nonTerminals.add(rule.lhs)
	
	# Returns a new symbol (with a new name build from the argument)
	def createNewSymbol(self, symbolName):
		# symbolName: String
		
		name = symbolName
		
		ok = False
		while (ok == False):
			ok = True
			for s in self.symbols:
				if s.name == name:
					ok = False
					continue
			
			if ok == False:
				name = name + "'"
		
		return Symbol(name)
		
	def isNonTerminal(self, symbol):
		# symbol: Symbol
		
		return symbol in self.nonTerminals
		
	def __str__(self):
		return "{" +\
			"symbols = [" + ",".join([str(s) for s in self.symbols]) + "]; " +\
			"axiom = " + str(self.axiom) + "; " +\
			"rules = [" + ", ".join(str(r) for r in self.rules) + "]" +\
			"}"

class Item:
	# field i: Integer
	# field j: Integer
	# field lhs: Symbol
	# field bd: list of Symbol
	# field ad: list of Symbol
	
	def __init__(self, i, j, lhs, bd, ad): # [lhs --> bd . ad, i, j]
		self.i = i
		self.j = j
		self.lhs = lhs
		self.bd = bd
		self.ad = ad
		
	def __str__(self):
		return "[%d, %d, %s --> %s * %s]" % \
			(self.i, self.j, str(self.lhs), ",".join([str(s) for s in self.bd]), ",".join([str(s) for s in self.ad]))
			
	def __eq__(self, other):
		return self.i == other.i and self.j == other.j and \
			self.lhs == other.lhs and self.bd == other.bd and self.ad == other.ad
			
class ParseChart:
	# field ch: list of Item
	# field ag: list of Item
	# method agAppend: Item -> (void)
	# method chAppend: Item -> (void)
	
	ch = [] # Chart
	ag = [] # Agenda
	
	def __init__(self):
		self.ch = []
		self.ag = []
		
	# Adds an item at the end of the agenda (+ prints some log)
	def agAppend(self, item, reason = None):
		self.ag.append(item)
		
		if reason != None:
			print( str(item) + " appended to the agenda (" + reason + ")")
		else:
			print( str(item) + " appended to the agenda")
		
	# Adds an item at the end of the chart (+ prints some log)
	def chAppend(self, item, reason = None):
		self.ch.append(item)
		
		if reason != None:
			print( str(item) + " appended to the chart (" + reason + ")" )
		else:
			print( str(item) + " appended to the chart" )

# ------------------------

# Initialisation
def init(g, w, t):
	# g: Grammar
	# w: list of Symbol
	# t: ParseChart
	for rule in g.rules :
		if rule.lhs == g.axiom :
			t.agAppend( Item(0, 0, g.axiom, [], rule.rhs ), "Init" )

# Insère dans l'agenda les éventuels nouveaux items issus de la règle pred ou scan pour l'item it
def pred_scan(g, w, it, t):
	# g: Grammar
	# w: list of Symbol
	# it: Item
	# t: ParseChart
	if it.ad :
		#Pred
		if g.isNonTerminal(it.ad[0]) :
			for rule in g.rules :
				if rule.lhs.name == it.ad[0].name:
					t.agAppend( Item(it.j, it.j, rule.lhs, [], rule.rhs), "Pred")
		#Scan
		else :
			if w[it.i].name == it.ad[0].name :
				t.agAppend( Item(it.j, it.j+1, it.lhs, it.bd + [it.ad[0]], it.ad[1:]), "Scan")

# Insère dans l'agenda les éventuels nouveaux items issus de la règle comp pour l'item it
def comp(g, w, it, t):
	# g: Grammar
	# w: list of Symbol
	# it: Item
	# t: ParseChart
	
	# Si l'item n'est pas inactif, pouvant avancer
	b = False
	if it.ad :
		for item in t.ch :
			if not item.ad :
				if it.j == item.i and it.ad[0].name == item.lhs.name:
					t.agAppend( Item(it.i, item.j, it.lhs, it.bd + [it.ad[0]], it.ad[1:]))
					b = True

	# Si l'item correspond à une règle inactive (terminée), pouvant faire avancer un autre item
	else :
		for item in t.ch :
			if item.ad :
				if it.i == item.j and item.ad[0].name == it.lhs.name :
					t.agAppend( Item(item.i, it.j, item.lhs, item.bd + [item.ad[0]], item.ad[1:]), "Comp")
					b = True

	return b

# Renvoie True si l'analyse a été réussie, False sinon
def table_complete(g, w, t):
	# g: Grammar
	# w: list of Symbol
	# t: ParseChart
	
	for item in t.ch :
		if item.lhs.name == g.axiom.name and not item.i and item.j == len(w) and not item.ad :
			return True
	
	return False

# Parse le mot w pour la grammaire g ; retourne le chart à la fin de l'algorithme
def parse_earley(g, w):
	# g: Grammar
	# w: list of Symbol
	
	T = ParseChart()
	
	# Initialisation
	init(g, w, T)
	
	# Boucle sur l'agenda : on sort un item, on l'insère dans la chart, et toutes ses conséquences sont insérées dans l'agenda
	while T.ag != []:
		it = T.ag.pop(0)
		T.chAppend(it)
		if not comp(g, w, it, T) :
			pred_scan(g, w, it ,T)
		
	if table_complete(g, w, T):
		print( "parsing réussi" )
	else:
		print( "parsing échoué" )
	
	return T.ch


# --------------

# Definition of the symbols
symS = Symbol("S")
symA = Symbol("A")
symTerminalA = Symbol("a")
symTerminalB = Symbol("b")

# Definition of a grammar
g1 = Grammar(
	# All symbols
	[symS, symA, symTerminalA, symTerminalB],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symS]), 				# S --> AS
		Rule(symS, [symTerminalB]), 				# S --> b
		Rule(symA, [symTerminalA]), 				# A --> a
	],
	
	# name
	"g1"
)

print( g1 )

words = ["aab", "b", "aaaaab", "abab"]
#words = ["aab"]

# Transform a word (as a String) to the symbolic representation (a list of terminal symbols)
def wordToTerminals(w, g):
	# w: String
	# g: Grammar
	
	result = []
	
	for i in range(len(w)):
		symbolFound = False
		
		for s in g.symbols:
			if s.name == w[i]:
				result.append(s)
				symbolFound = True
				break
				
		if symbolFound != True:
			print( "ERROR: symbol " + w[i] + " not in grammar " + g.name )
			exit(0)
				
	return result

for w in words:
	print( "\nmot : " + w )
	
	chart = parse_earley(g1, wordToTerminals(w, g1))
	
	print( "chart:" )
	for item in chart:
		print( "\t" + str(item) )
	
