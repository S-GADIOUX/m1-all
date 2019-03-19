#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Perceptron
import sklearn

import argparse
import numpy as np # pour learning curve, pour plot confusion_matrix

def read_examples(infile):
    """ Lecture d'un fichier au format onedocperline, et transformation en 
    (liste de docs, liste de classes gold)
    un doc = une string
    une classe = une string
    Les données d'entrée peuvent être multilabel (plusieurs classes pour un doc) mais sont transformées artificiellement en monolabel:
    Pour un doc associé à plusieurs classes, le document est dupliqué autant de fois qu'il a de classes gold.
    """
    docs = []
    classes = []
    instream = open(infile)
    for line in instream.readlines():
        (class_list, doc) = line.split("\t", 1)
        classes_of_this_doc = class_list.split(",")
        classes += classes_of_this_doc
        # on duplique le document autant de fois qu'il a de classes gold
        for x in range(len(classes_of_this_doc)):
            docs.append(doc)
    return docs, classes



usage = """ Utilisation de sklearn pour un pb de classification de documents """

parser = argparse.ArgumentParser(usage=usage)
parser.add_argument('train_file', help = 'train file in onedocperline format', default = None)
parser.add_argument('train_pred_output_file', help = 'train_pred_output_file (prediction on train file)', type=argparse.FileType('w'), default = None)
parser.add_argument('test_file', help = 'test file in onedocperline format ', default = None)
parser.add_argument('test_pred_output_file', help = 'test_pred_output_file (prediction on test file) ', type=argparse.FileType('w'), default = None)
parser.add_argument('-v', '--verbose', help = 'Verbose level (int) for the sklearn classifier. Default=0', type=int, default = 0)
parser.add_argument('-s', '--early_stopping', help = 'Whether to Verbose level (int) for the sklearn classifier. Default=0', type=int, default = 0)
parser.add_argument('-n', '--max_nb_epochs', help = 'Max number of epochs (max_iter in sklearn). Defaut=5', type=int, default = 5)
parser.add_argument('-l', '--learning_rate', help = 'Constant learning rate (eta0 in sklearn Perceptron). Default=1', type=float, default=1)
parser.add_argument('-r', '--regularization', help = 'Regularization term (penalty in sklearn.perceptron)  "l1", "l2" or None. Default=None', default=None)
#malgré un membre "average" pour la classe perceptron, l'averaged perceptron n'est visiblement pas implémenté ds sklearn
parser.add_argument('-a', '--averaged', action="store_true", help = 'If set, use averaged perceptron')

args = parser.parse_args()

# lecture des exemples, et transformation en (liste de strings, liste de classes gold)
# chaque string est un doc
# (cf. format attendu par le vectorizer utilisé infra, 
#      cf. le notebook de présentation des Vectorizer:
#      sklearn_extract_features_from_text.ipynb )
(docs_train, Y_train) = read_examples(args.train_file)
(docs_test, Y_test) = read_examples(args.test_file)

vectorizer = TfidfVectorizer()

X_train = vectorizer.fit_transform(docs_train)
X_test = vectorizer.transform(docs_test)

print("X_train shape : %s" % str(X_train.shape))
print("X_test shape : %s" % str(X_test.shape))

myclassifier = Perceptron(verbose = args.verbose, 
                          eta0 = args.learning_rate,
                          #average=args.average, pas implémenté
                          max_iter = args.max_nb_epochs,
                          penalty = args.regularization)

print("SETTINGS:")
for a in sorted(myclassifier.__dict__.keys()):
    print("%s\t%s" % (a, str(myclassifier.__dict__[a])))

myclassifier.fit(X_train, Y_train)


# --------- prediction sur le test---------------
Y_test_pred = myclassifier.predict(X_test)
print("SCORE OF PERCEPTRON ON TEST FILE", args.test_file, ": ", sklearn.metrics.accuracy_score(Y_test, Y_test_pred))
# ecriture des classes predites
args.test_pred_output_file.write( '\n'.join(Y_test_pred) + "\n" )
    

# --------- prediction sur le train--------------
Y_train_pred = myclassifier.predict(X_train)
print("SCORE OF PERCEPTRON ON TRAIN FILE", args.train_file, ": ", sklearn.metrics.accuracy_score(Y_train, Y_train_pred))
# ecriture des classes predites
args.train_pred_output_file.write( '\n'.join(Y_train_pred) + "\n" )



