#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import sys
import re
import argparse
from math import *
from collections import defaultdict


# du fait d'erreurs de calcul, on se retrouve parfois avec des distances négatives
# on prend ici une valeur minimale de distance, positive (pour pouvoir prendre la racine) et non nulle (pour pouvoir prendre l'inverse)
MINDIST =  1e-18


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

	def distance_to_vector(self, other_vector):
		""" distance euclidienne entre self et other_vector, en ayant precalculé les normes au carre de chacun """
		# NB: passer par la formulation  sigma [ (ai - bi)^2 ] = sigma (ai^2) + sigma (bi^2) -2 sigma (ai*bi) 
		#													= norm_square(A) + norm_square(B) - 2 A.B

		return sqrt(self.norm_square + other_vector.norm_square - 2* self.dot_product(other_vector))

	def dot_product(self, other_vector):
		""" rend le produit scalaire de self et other_vector """
		dot = 0
		for feat in self.f :
			if feat in other_vector.f :
				dot += self.f[feat]*other_vector.f[feat]
		return dot

	def cosinus(self, other_vector):
		""" rend le cosinus de self et other_vector """
		return self.dot_product(other_vector) / sqrt(self.norm_square * other_vector.norm_square)


class KNN:
	"""
	K-NN pour la classification de documents (multiclasse)

	membres = 

	k = l'hyperparametre K : le nombre de voisins a considerer

	examples = liste d'instances de Example

	classes = liste des classes (telles que recensées dans les exemples)

	"""
	def __init__(self, examples, K = 1, weight_neighbors = None, use_cosinus = False, trace = False):
		""" 
		simple positionnement des membres et recensement des classes connues
		"""
		# les exemples : liste d'instances de Example
		self.examples = examples
		# le nb de voisins
		self.K = K
		# booleen : on pondere les voisins (par inverse de la distance) ou pas
		self.weight_neighbors = weight_neighbors

		# booleen : pour utiliser plutot la similarité cosinus
		self.use_cosinus = use_cosinus

		self.trace = trace
		

	def weigth(self, x) :
		if not self.weight_neighbors :
			return 1
		elif self.use_cosinus :
			return x
		else :
			return 1/x

	def classify(self, ovector):
		"""
		Réalise la prédiction du classifieur K-NN pour le ovector
		pour les valeurs de k allant de 1 à self.K

		A partir d'un vecteur de traits représentant un objet
		retourne un vecteur des classes assignées de longueur K : 
		la classe à la i-eme  position est la classe assignée par l'algo K-NN, avec K = i
		"""
		#Select the classifying function
		if self.use_cosinus :
			prox = Ovector.cosinus
		else :
			prox = Ovector.distance_to_vector
		
		#Classify
		neighbors = []
		for example in self.examples :
			neighbors.append((example.gold_class, prox(example.vector, ovector)))

		#Sort neighbors
		best = sorted(neighbors, key = lambda x : x[1], reverse = self.use_cosinus)

		#Extracts nearests neighbors
		result = []
		i_class = defaultdict(int)
		for i in range(self.K):
			i_class[best[i][0]] += self.weigth(best[i][1])
			top_ones = 0 # top_ones is for preventing list out of range while sorting alphabeticals.
			classes = sorted(i_class.items(), key = lambda x : x[1], reverse = True)
			alpha = set()
			while top_ones < len(classes) and classes[top_ones][1] == classes[0][1] :
				alpha.add(classes[top_ones][0])
				top_ones += 1
			result.append(sorted(alpha)[0])
		return result


	def evaluate_on_test_set(self, test_examples):
		""" Application du classifieur sur une liste d'exemples de test, et evaluation (accuracy) 
		pour les valeurs de k allant de 1 à self.K
		Retourne une liste d'accuracy (pour les valeurs de k à self.K)
		"""
		results = [0 for i in range(self.K)]
		for example in test_examples :
			class_example = self.classify(example.vector)
			result_example = [1 if example.gold_class == class_i else 0 for class_i in class_example]
			results = [x + y for x, y in zip(results, result_example)]
		return [acc / len(test_examples) for acc in results]
		
		

def read_examples(infile):
	""" Lit un fichier d'exemples 
	et retourne une liste d'instances de Example
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
			example.add_feat(featname, float(val))

	if example is not None:
		examples.append(example)
	return examples



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
# Chargement des exemples d'apprentissage du classifieur KNN
training_examples = read_examples(args.examples_file)
# Chargement des exemples de test
test_examples = read_examples(args.test_file)

myclassifier = KNN( examples = training_examples,
					K = args.k,
					weight_neighbors = args.weight_neighbors,
					use_cosinus = args.use_cosinus,
					trace = args.trace)

# classification et evaluation sur les exemples de test
accuracies = myclassifier.evaluate_on_test_set(test_examples)
for i in range(len(accuracies)):
	print("ACCURACY FOR K =", i+1, " : ","{:.2%}".format(accuracies[i]),
			"(weight =", args.weight_neighbors, "dist_or_cos =", "cos)" if args.use_cosinus else "dist)" )

