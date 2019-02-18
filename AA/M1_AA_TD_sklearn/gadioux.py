#!/usr/bin/env python
# -*- coding: utf-8-*-

import sys, argparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import Perceptron

def read_examples(infile, vectorizer, train = True ):
	""" Lit un fichier d'exemples 
	et retourne une liste d'instances de Example,
	tout en chargeant une classe Indice.
	"""
	stream = open(infile)
	classes = []
	examples = []
	line = stream.readline()
	
	while line :
		#Recuperation des classes et du document.
		goldes, phrases = line.split('\t')
		golds = goldes.split(",")
		#Phase de multiplication des exemples multi-classes
		for gold in golds :
			classes.append(gold)
			examples.append(phrases)
		line = stream.readline()
	
	if train :
		return classes, vectorizer.fit_transform(examples)
	else :
		return classes, vectorizer.transform(examples)

usage = """ CLASSIFIEUR de DOCUMENTS, de type K-NN

  """+sys.argv[0]+""" [options] EXAMPLES_FILE TEST_FILE

  EXAMPLES_FILE et TEST_FILE sont au format *.examples

"""

parser = argparse.ArgumentParser(usage = usage)
parser.add_argument('examples_file', default = None,
					help = 'Exemples utilisés comme voisins pour la prédiction KNN (au format .examples)')

parser.add_argument('test_file', default = None,
					help = 'Exemples de test (au format .examples)')

parser.add_argument('--tfidf', '-i', action='store_true',
					help = 'Exemples de test (au format .examples)')

args = parser.parse_args()


#------------------------------------------------------------
if args.tfidf :
	vectorizer = TfidfVectorizer(token_pattern = r"\w+")
else :
	vectorizer = CountVectorizer(token_pattern = r"\w+")
# Chargement des exemples d'apprentissage du classifieur KNN
Y_train, X_train = read_examples(args.examples_file, vectorizer)
# Chargement des exemples de test
Y_test, X_test = read_examples(args.test_file, vectorizer, False)
#Creation des matrices

perceptron = Perceptron().fit(X_train, Y_train)
print(perceptron.score(X_test, Y_test))