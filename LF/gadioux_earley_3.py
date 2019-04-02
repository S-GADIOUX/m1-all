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
	# field tree: class Tree usefull for the syntax tree
	
	def __init__(self, i, j, lhs, bd, ad, tree = None): # [lhs --> bd . ad, i, j]
		self.i = i
		self.j = j
		self.lhs = lhs
		self.bd = bd
		self.ad = ad
		self.tree = tree
		
	def __str__(self):
		return "[%d, %d, %s --> %s * %s]" % \
			(self.i, self.j, str(self.lhs), ",".join([str(s) for s in self.bd]), ",".join([str(s) for s in self.ad]))
			
	def __eq__(self, other):
		return self.i == other.i and self.j == other.j and \
			self.lhs == other.lhs and self.bd == other.bd and self.ad == other.ad

	def __hash__(self):
		return str(self).__hash__()
			
class ParseChart:
	# field ch: list of Item
	# field ag: list of Item
	# method agAppend: Item -> (void)
	# method chAppend: Item -> (void)
	
	ch = [] # Chart
	ag = [] # Agenda
	
	def __init__(self, verbose = False):
		self.ch = []
		self.chset = set()
		self.ag = []
		self.agset = set() # Because thank you recursives stupids rules...
		self.verbose = verbose
		
	# Adds an item at the end of the agenda (+ prints some log)
	def agAppend(self, item, reason = None):
		if item not in self.agset :
			self.ag.append(item)
			self.agset.add(item)
			if reason != None:
				print( str(item) + " appended to the agenda (" + reason + ")")
			else:
				print( str(item) + " appended to the agenda")
		else :
			print( str(item) + " already in agenda ")

		
	# Adds an item at the end of the chart (+ prints some log)
	def chAppend(self, item, reason = None):
		if item not in self.chset :
			self.ch.append(item)
			self.chset.add(item)
			if reason != None:
				print( str(item) + " appended to the chart (" + reason + ")")
			else:
				print( str(item) + " appended to the chart")
			return True
		else :
			print( str(item) + " already in chart !!!!!!!!!!!!!!")
			return False

class Tree:
	# field branches: liste de longueur 1 ou 2 (seules possibilités avec une grammaire en FNC).
	# Si la longueur est 1, l'element est une liste de 1 symbole.
	# Si la longueur est 2, les éléments sont eux-mêmes des arbres.
	# field label: Symbol
	# (no methods)

	def __init__(self, label, branches):
			self.branches = branches
			self.label = label
	
	def __str__(self):
		if len(self.branches) == 1:
			return self.label.name + "\n  " + (str(self.branches[0]).replace("\n", "\n  "))
		else:
			return self.label.name + "\n  " + str(self.branches[0]).replace("\n", "\n  ") + "\n  " + str(self.branches[1]).replace("\n", "\n  ")

# ------------------------

# Initialisation
def init(g, w, t):
	# g: Grammar
	# w: list of Symbol
	# t: ParseChart
	for rule in g.rules :
		if rule.lhs == g.axiom :	# Ajout des règles axiomatiques.
			t.agAppend( Item(0, 0, g.axiom, [], rule.rhs ), "Init" )
			if t.verbose :
				input()

# Insère dans l'agenda les éventuels nouveaux items issus de la règle pred ou scan pour l'item it
def pred_scan(g, w, it, t):
	# g: Grammar
	# w: list of Symbol
	# it: Item
	# t: ParseChart
	if it.ad : # Si la règle est active.
		#Pred
		if g.isNonTerminal(it.ad[0]) :
			for rule in g.rules :	# Recherche des règles pouvant être produite à partir de la tête de la partie encore active de l'item.
				if rule.lhs.name == it.ad[0].name and not ( len(rule.rhs) == 1 and rule.lhs.name == rule.rhs[0].name ):
					t.agAppend( Item(it.j, it.j, rule.lhs, [], rule.rhs), "Pred")
		#Scan
		else :
			if it.j < len(w) and w[it.j].name == it.ad[0].name :	# Comparaison de la tête de lecture avec le terminal dans la règle.
				t.agAppend( Item(it.j, it.j+1, it.lhs, it.bd + [it.ad[0]], it.ad[1:], tree = Tree( it.lhs ,[w[it.i]]) ), "Scan") # Ajout egalement de l'arbre syntaxique produit par la regle.
	if t.verbose :
		input()

# Insère dans l'agenda les éventuels nouveaux items issus de la règle comp pour l'item it
def comp(g, w, it, t):
	# g: Grammar
	# w: list of Symbol
	# it: Item
	# t: ParseChart
	
	b = False
	for item in t.ch :	# Parcours des autres item de la chart.
			if it.ad and not item.ad : 	 # Si l'item principal est actif
				b += comp_help(it, item, t)
			elif not it.ad and item.ad : # Si l'autre item est actif
				b += comp_help(item, it, t)
	if t.verbose :
		input()
	return b

def comp_help(act, inact, t):
	# Fonction de support de comp qui prend en entrée deux item, un actif et l'autre inactif ainsi qu'une table T.
	# La fonction tente ensuite une compilation.
	if act.j == inact.i and act.ad[0].name == inact.lhs.name :
		t.agAppend( Item(act.i, inact.j, act.lhs, act.bd + [act.ad[0]], act.ad[1:], tree = Tree(inact.lhs, [act.tree, inact.tree] ) if act.tree else inact.tree ), "Comp")
		#les arbres sont egalement gérés au dessus.
		return True
	return False

# Renvoie True si l'analyse a été réussie, False sinon
def table_complete(g, w, t):
	# g: Grammar
	# w: list of Symbol
	# t: ParseChart
	axioms = []
	for item in t.ch : # Verifie si l'item est l'axiome, qu'il a bien lu tout le mot et que la regle est inactive.
		if item.lhs.name == g.axiom.name and not item.i and item.j == len(w) and not item.ad :
			axioms.append(item)
	
	return axioms

# Parse le mot w pour la grammaire g ; retourne le chart à la fin de l'algorithme
def parse_earley(g, w, v):
	# g: Grammar
	# w: list of Symbol
	
	T = ParseChart(v)
	
	# Initialisation
	init(g, w, T)
	
	# Boucle sur l'agenda : on sort un item, on l'insère dans la chart, et toutes ses conséquences sont insérées dans l'agenda
	while T.ag != []:
		if not v :
			print("")
		it = T.ag.pop(0)	# Sortie de l'agenda
		T.agset.remove(it)
		if T.chAppend(it) :		# Ajout dans la table
			if not comp(g, w, it, T) :	#Calcul de comp
				pred_scan(g, w, it ,T)	# Calcul de pred et scan
	trees = table_complete(g, w, T)
	if len(trees):
		print( "\n****Parsing réussi****" )
		for tree in trees :
			print("Tree :\n" + str(tree.tree))
	else:
		print( "\n****Parsing échoué****" )
	
	return T.ch


# --------------

# Definition of the symbols
symS = Symbol("S")
symA = Symbol("A")
symTerminalA = Symbol("a")
symTerminalB = Symbol("b")
symEpsilon = Symbol("")

# Definition of a grammar
g1 = Grammar(
	# All symbols
	[symS, symA, symTerminalA, symTerminalB],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symS]), 					# S --> AS
		Rule(symS, [symTerminalB]), 				# S --> b
		Rule(symA, [symTerminalA]), 				# A --> a
	],
	
	# name
	"g1"
)

g2 = Grammar(
	# All symbols
	[symS, symA, symTerminalA, symTerminalB],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symS]), 		# S --> AS
		Rule(symS, [symTerminalB]), 	# S --> b
		Rule(symA, [symTerminalA]), 	# A --> a
		Rule(symA, [symA]), 			# A --> A
	],
	
	# name
	"g2"
	)

g3 = Grammar(
	# All symbols
	[symS, symA, symTerminalA, symTerminalB, symEpsilon],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symS]), 					# S --> AS
		Rule(symS, [symA]), 						# S --> A
		Rule(symS, [symTerminalB]), 				# S --> b
		Rule(symS, [symTerminalB, symTerminalB]), 	# S --> bb
		Rule(symA, [symTerminalA]), 				# A --> a
		Rule(symA, [symS]), 						# A --> S
		Rule(symA, [symEpsilon]),					# A --> e
	],
	
	# name
	"g3"
	)

print( g2 )

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
	print( "\n#### Mot : " + w + " ####")
	
	chart = parse_earley(g1, wordToTerminals(w, g3), False)
	
	print( "chart:" )
	for item in chart:
		print( "\t" + str(item) )
	
