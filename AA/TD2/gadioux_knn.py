#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import sys, re,  argparse
from math import *
from collections import defaultdict
import numpy as np

# du fait d'erreurs de calcul, on se retrouve parfois avec des distances négatives
# on prend ici une valeur minimale de distance, positive (pour pouvoir prendre la racine) et non nulle (pour pouvoir prendre l'inverse)
MINDIST =  1e-18

class Indice :
	"""
	Classe servant à faire un lien entre des mots et leur index.
	"""
	def __init__(self):
		self.words_to_ind = {}
		self.ind_to_words = []
	
	def size_of(self):
		return len(self.ind_to_words)

	def add_words(self, word):
		if word not in self.words_to_ind :
			self.words_to_ind[word] = len(self.ind_to_words)
			self.ind_to_words.append(word)

	def get_indice(self, word):
		if word not in self.words_to_ind :
			self.add_words(word)
		return self.words_to_ind[word]

class Example:
	"""
	Un exemple : 
	vector = représentation vectorielle (Ovector) d'un objet
	gold_class = la classe gold pour cet objet
	"""
	def __init__(self, example_number, gold_class):
		self.gold_class = gold_class
		self.example_number = example_number
		self.vector = Ovector()

	def add_feat(self, featname, val):
		self.vector.add_feat(featname, val)

class Ovector:
	"""
	Un vecteur représentant un objet

	membres
	- f= simple dictionnaire nom_de_trait => valeur
		 Les traits non stockés correspondent à une valeur nulle
	- norm_square : la norme au carré
	"""
	def __init__(self):
		self.f = {}
		self.norm_square = 0

	def add_feat(self, featname, val = 0.0):
		self.f[featname] = val
		self.norm_square += val*val

	def prettyprint(self):
		for feat in sorted(self.f, lambda x,y: cmp( self.f[y], self.f[x] ) or cmp(x,y)):
			print (feat + "	" + str(self.f[feat]))

def read_examples(infile, indice):
	""" Lit un fichier d'exemples 
	et retourne une liste d'instances de Example,
	tout en chargeant une classe Indice.
	"""
	stream = open(infile)
	examples = []
	example = None
	while True:
		line = stream.readline()
		if not line:
			break
		line = line[0:-1]
		if line.startswith("EXAMPLE_NB"):
			if example is not None:
				examples.append(example)
			cols = line.split('	')
			gold_class = cols[3]
			example_number = cols[1]
			example = Example(example_number, gold_class)
		elif line and example is not None:
			(featname, val) = line.split('	')
			indice.add_words(featname)
			example.add_feat(featname, float(val))

	if example is not None:
		examples.append(example)
	return examples

def give_me_the_matrix(example_list, indice):
	X_matrix = np.zeros((len(example_list), indice.size_of()))
	Y_vector = []
	i = 0
	for example in example_list :
		Y_vector.append(example.gold_class)
		for feat in example.vector.f :
			X_matrix[i, indice.get_indice(feat) ] = example.vector.f[feat]
		i += 1
	return X_matrix, Y_vector

def return_norm(matrix):
	return np.apply_along_axis(np.linalg.norm,1, matrix)

def normalize_matrix(matrix, norm_of):
	return matrix/norm_of[:,None]

def create_cos_matrix(X_train, X_test):
	norm_train = return_norm(X_train)
	norm_test = return_norm(X_test)
	classed = np.dot( normalize_matrix(X_test, norm_test ), normalize_matrix(X_train, norm_train).transpose())
	return classed

def KNN(classed_matrix, Y_train, Y_test, k):
	"""
	We assume classed matrix as a matrix where lines are test and columns are train, so in a line we have cosinus of all 
	"""
	global_result = []
	for line in classed_matrix :
		best = sorted([(Y_train[x],line[x]) for x in range(len(line))], key = lambda x : x[1], reverse = True)
		#Extracts nearests neighbors
		result = []
		i_class = defaultdict(int)
		for i in range(k):
			i_class[best[i][0]] += best[i][1]
			top_ones = 0 # top_ones is for preventing list out of range while sorting alphabeticals.
			classes = sorted(i_class.items(), key = lambda x : x[1], reverse = True)
			alpha = set()
			while top_ones < len(classes) and classes[top_ones][1] == classes[0][1] :
				alpha.add(classes[top_ones][0])
				top_ones += 1
			result.append(sorted(alpha)[0])
		global_result.append((result, Y_test.pop(0)))
	return global_result

def classify(X_train, Y_train, vec, k):
	var = KNN(create_cos_matrix(X_train, vec[None,:]), Y_train, ["UNKWOWN"], k)
	return var[0] 

def calc_acc(results, k):
	acc = [0 for i in range(k)]
	for result in results :
		result_example = [1 if result[1]== class_i else 0 for class_i in result[0]]
		acc = [x + y for x, y in zip(acc, result_example)]
	return [a / len(results) for a in acc]

usage = """ CLASSIFIEUR de DOCUMENTS, de type K-NN

  """+sys.argv[0]+""" [options] EXAMPLES_FILE TEST_FILE

  EXAMPLES_FILE et TEST_FILE sont au format *.examples

"""

parser = argparse.ArgumentParser(usage = usage)
parser.add_argument('examples_file', default = None,
					help = 'Exemples utilisés comme voisins pour la prédiction KNN (au format .examples)')

parser.add_argument('test_file', default = None,
					help = 'Exemples de test (au format .examples)')

parser.add_argument('-k', "--k", default = 1, type = int,
					help = 'Hyperparametre K : le nombre max de voisins a considerer pour la classification (toutes les valeurs de 1 a k seront testees). Default = 1')

parser.add_argument('-v', "--trace", action = "store_true",
					help = "A utiliser pour declencher un mode verbeux. Default = False")

parser.add_argument('-w', "--weight_neighbors", action = "store_true",
					help = "Ponderation des voisins : si cosinus: ponderation par le cosinus, si distance, ponderation par l'inverse de la distance. Defaut = None")

parser.add_argument('-c', "--use_cosinus", action = "store_true",
					help = "A utiliser pour passer a une mesure de similarite cosinus, au lieu d'une distance euclidienne. Default = False")

parser.add_argument('-t', "--tune", action = "store_true", default = "",
					help = 'A utiliser pour declencher le tuning des hyperparametres: cos ou dist, avec ou sans ponderation, et figure des performances en fonction de k. Default = False')

parser.add_argument('-f', "--figure_file", default = "graphique.pdf",
					help = 'Pour le mode "tune": Base de nom de fichier pour graphique precision en fonction de K. Default = "graphique.pdf".')

args = parser.parse_args()

#------------------------------------------------------------
indexer = Indice()
# Chargement des exemples d'apprentissage du classifieur KNN
training_examples = read_examples(args.examples_file, indexer)
# Chargement des exemples de test
test_examples = read_examples(args.test_file, indexer)
#Creation des matrices
X_train, Y_train = give_me_the_matrix(training_examples, indexer)
X_test, Y_test = give_me_the_matrix(test_examples, indexer)
# Calcul de la matrice cosinus
cos_matrix = create_cos_matrix(X_train, X_test)
#Calcul des KNN
scores = KNN(cos_matrix, Y_train, Y_test, args.k)
#Calcul de la precision
accuracies = calc_acc(scores , args.k)

for i in range(len(accuracies)):
	print("ACCURACY FOR K =", i+1, "\t: ","{:.2%}".format(accuracies[i]) )
