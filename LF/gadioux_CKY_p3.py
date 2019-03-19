#!/usr/bin/python
# -*- encoding: utf-8 -*-

# ----------------------------------------------------------------------
# CKY
# ----------------------------------------------------------------------

class Symbol:
	# field name: String
	# (no methods)
	
	def __init__(self, name):
		# name: String
		
		self.name = name
	
	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name

	def __hash__(self):
		return self.name.__hash__()

class Rule:
	# field lhs: Symbol
	# field rhs: list of Symbol
	# (no methods)
	
	def __init__(self, lhs, rhs):
		# lhs: Symbol
		# rhs: list of Symbol
		
		self.lhs = lhs
		self.rhs = rhs
		
	def __str__(self):
		return str(self.lhs) + " --> [" + ",".join([str(s) for s in self.rhs]) + "]"

class Grammar:
	# field symbols: list of Symbol
	# field axiom: Symbol
	# field rules: list of Rule
	# field name: String
	# field nonTerminals: set of Symbol
	# method createNewSymbol: String -> Symbol
	# method isNonTerminal: Symbol -> Boolean
		
	def __init__(self, symbols, axiom, rules, name):
		# symbols: list of Symbol
		# axiom: Symbol
		# rules: list of Rule
		# name: String
		
		self.symbols = symbols
		self.axiom = axiom
		self.rules = rules
		self.name = name
		
		self.nonTerminals = set()
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

	def giveMeRules(self, listOfSymbol):
		# Return all rules that generate the given list of symbol.
		ret = set()
		for rule in self.rules :
			if rule.rhs == listOfSymbol :
				ret.add(rule)
		return ret
		
	def __str__(self):
		return "{" +\
			"symbols = [" + ",".join([str(s) for s in self.symbols]) + "]; " +\
			"axiom = " + str(self.axiom) + "; " +\
			"rules = [" + ", ".join(str(r) for r in self.rules) + "]" +\
			"}"

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
			return "[ " + self.label.name + ", " + str(self.branches[0]) + " ]"
		else:
			return "[ " + self.label.name + ", " + str(self.branches[0]) + ", " + str(self.branches[1]) + " ]"

# Definition of the symbols
symS = Symbol("S")
symA = Symbol("A")
symB = Symbol("B")
symC = Symbol("C")
symX = Symbol("X")
symTerminalA = Symbol("a")
symTerminalB = Symbol("b")
symTerminalC = Symbol("c")
# On peut bien sûr rajouter des symboles si nécessaire

# Définition de trois grammaires pour tester le parseur

g1 = Grammar(
	# Alphabet
	[symS, symA, symB, symTerminalA, symTerminalB],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symB]),				# S --> AB
		Rule(symS, [symTerminalA]),			# S --> a
		Rule(symA, [symS, symB]),				# A --> SB
		Rule(symA, [symTerminalB]),			# A --> b
		Rule(symB, [symTerminalB])				# B --> b
	],
	
	# name
	"g1"
)

g2 = Grammar(
	# Alphabet
	[symS, symA, symTerminalA, symTerminalB],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symS]),				# S --> AS
		Rule(symS, [symTerminalB]),				# S --> b
		Rule(symA, [symTerminalA])				# A --> a
	],
	
	# name
	"g2"
)

g3 = Grammar(
	# Alphabet
	[symS, symA, symB, symX, symTerminalA, symTerminalB],
	
	# Axiom
	symS,
	
	# List of rules
	[
		Rule(symS, [symA, symX]),				# S --> AX
		Rule(symS, [symA, symB]),				# S --> AB
		Rule(symX, [symS, symB]),				# X --> SB
		Rule(symA, [symTerminalA]),				# A --> a
		Rule(symB, [symTerminalB])				# B --> b
	],
	
	# name
	"g3"
)


# ----------------------------------------------------------------------
# Version minimale de l'algorythme CYK
#
# Soit u un mot de longueur n ; pour 0 =< i < j <= n,
# T[i, j] est l'ensemble des non-terminaux A tels qu'il existe
# une dérivation de A vers le sous-mot 'u[i] u[i+1] ... u[j-1]'
# (i.e. A -->* u[i] ... u[j-1])
#
# Plus de détails : https://en.wikipedia.org/wiki/CYK_algorithm
# ----------------------------------------------------------------------

"Création et initialisation de la table T pour le mot u et la grammaire gr"
def init(u, gr) :
	# i est utilisé en ordonné et j en abscisse
	# i représente le nombre de lettre lues moins 1
	# j représente l'index de la première lettre du sous mot. 
	# exemple avec abba
	"""
	i
	3 *
	2 * *
	1 * * *
	0 * * * *
	# a b b a
	# 0 1 2 3 j
	"""

	T = {}

	# Initialisation à vide
	for i in range(len(u)) :
		for j in range(len(u)-i):
			T[i, j] = set()
	
	# Ajout des arbres feuilles
	for i in range(len(u)) :
		for rule in gr.giveMeRules([Symbol(u[i])]):
			T[0,i].add(Tree(rule.lhs, rule.rhs)) 
	return T


"Remplissage de la table T (initialisation déjà effectuée) pour le mot u et la grammaire gr"
def loop(T, u, gr) :
	for i in range(1, len(u)) : 					# Nombre de lettres lues
		for j in range(len(u)-i) : 					# Indice de la première lettre lue
			for k in range(i):						# Nombre de lettre après la première où la subdivision a lieu.
				for symb1 in T[k,j]:				# Tous les arbres pour générer la partie gauche
					for symb2 in T[i-1-k,j+1+k]:	# Tous les arbres pour générer la partie droite
						for rule in gr.giveMeRules([symb1.label, symb2.label]): # Pour chaque règle générant les arbres, ajouter l'arbre correspondant
							T[i,j].add(Tree(rule.lhs, [symb1, symb2]))

"Création de la table d'analyse du mot u pour la grammaire gr"
def buildTable(u, gr):
	T = init(u, gr)
	loop(T, u, gr)
	
	return T

"Affichage d'une table T pour un mot de taille n"
def printT(T, n):
	for i in range(n):
		for j in range(n-i):
			print(str((i,j)) + ": " + ", ".join(str(t.label) for t in T[i,j]))


# ----------------------------------------------------------------------
# L'algo est entièrement codé dans les trois fonctions précédentes, les
# fonctions qui suivent servent uniquement à afficher les résultats,
# et à réaliser facilement quelques tests
# ----------------------------------------------------------------------

"Une fois la table T remplie, détermine si l'analyse a réussi"
def isSuccess(T, u, gr):
	#check if axiom is in top emplacement
	return gr.axiom in set([ tree.label for tree in T[len(u)-1,0] ])

"Une fois l'analyse effectuée, retrouve et affiche l'arbre syntaxique à partir de la table"
def printTree(T, u, gr):
	#print all trees in top emplacement if they are axiom
	for tree in T[len(u)-1,0] :
		if gr.axiom == tree.label :
			print(tree)

"Vérifie que la grammaire est en forme normale de Chomsky"
def checkCNF(gr):
	for r in gr.rules:
		l = len(r.rhs) 
		if l == 1 and gr.isNonTerminal(r.rhs[0]) :
			print("Error 1 ","\n",r)
			return False
		elif l == 2 and (not gr.isNonTerminal(r.rhs[0])) and (not gr.isNonTerminal(r.rhs[1])): 
			print("Error 2 ","\n",r)
			return False
		elif l<1 or l>2 :
			print("Error 0 ","\n",r)
			return False
	return True

"Fonction globale d'analyse syntaxique"
def parse(u, gr):
	print("--- \"" + u + "\" - " + gr.name + " ---")
	
	if not checkCNF(gr):
		print("la grammaire n'est pas en forme normale de Chomsky!")
		return None
	
	T = buildTable(u, gr)
	
	print("table d'analyse :")
	printT(T, len(u))
	print("")
	
	if isSuccess(T, u, gr):
		print("le mot est généré par la grammaire")
		print("")
		print("arbre :")
		printTree(T, u, gr)
	else:
		print("le mot N'est PAS généré par la grammaire")


parse("bb", g1)
print("")

parse("abb", g1)
print("")

parse("aaab", g2)
print("")

" Facultatif: parser le mot abaca avec la grammaire ambiguë. Doit afficher deux arbres d'analyse."


g4 = Grammar(
	#Alphabet
	[symS, symA, symB, symC, symTerminalA, symTerminalB, symTerminalC],
	
	#Axiom
	symS,
	
	#List of rules
	[
		Rule(symS, [symS, symA]),				 #S --> SA
		Rule(symS, [symTerminalA]),				 #S --> a
		Rule(symA, [symB, symS]),				 #A --> BS
		Rule(symA, [symC, symS]),				 #A --> CS
		Rule(symB, [symTerminalB]),				 #B --> b
		Rule(symC, [symTerminalC])				 #C --> c
	],
	
	#name
	"g4"
)

parse("abaca", g4)
