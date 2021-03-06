#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import time
import argparse
import numpy
from decimal import Decimal
# tutoriel numpy : http://www.scipy.org/Tentative_NumPy_Tutorial

class Dendrogram:
	""" Un dendrogramme : utilisé pour représenter tout cluster obtenu par clustering hiérarchique
	Contient 
	- soit un seul objet (cluster singleton), dans self.child1 (et child2 vaut None)
	- soit une paire de dendrogrammes (les 2 noeuds fils) et leur similarité
	Membres :
	- child1 : string (si singleton) ou instance de Dendrogram
	- child2 : None (si singleton) ou instance de Dendrogram
	- sim : similarité entre child1 et child2
	- members : la liste à plat des objets contenus dans le dendrogramme (cf. pb de récursion trop profonde)
	"""
	def __init__(self, child1, child2=None, sim=0):
		self.sim = sim
		self.child1 = child1
		self.child2 = child2
		# on stocke au fur et à mesure la string d'affichage, pour éviter les pbs de récursion trop profonde
		if child2 == None:
			self.members = [ child1 ]
		else:
			self.members = child1.members + child2.members

	def is_singleton(self):
		""" Retourne True s'il s'agit d'un cluster réduit à un seul objet, False sinon """
		return (self.child2 == None)

	def print_members(self, stream):
		""" écrit la liste d'objets présents dans le cluster 
		"""
		stream.write(' '.join( [ x for x in self.members ] ))
	
	def __str__(self):
		""" Affichage parenthésé du dendrogramme (illisible si dendrogramme trop gros...) """
		if self.is_singleton():
			return str(self.child1)
		return str(self.sim) + ':(' + str(self.child1) + ' + ' + str(self.child2) + ')'

class HAC:
	"""
	Classe implémentant le single-link hierarchical agglomerative clustering

	Membres:
	* clusters : liste python de clusters, de type Dendrogram 
				 (éventuellement réduits à un seul objet)
				 IMPORTANT: le rang dans cette liste sert d'id de cluster dans les autres membres 
				 (matrice de sim, et ppc)
	* sim_matrix : matrice de similarite entre clusters (type numpy.ndarray)
	* ppc : Liste de paires :
			pour chaque cluster, identifié par son rang,
			stocke une paire (similarité avec le ppc, ppc)
	"""
	def __init__(self, trace):
		self.clusters = []
		self.sim_matrix = None
		self.ppc = []
		self.actif = []

		self.trace = trace

	def get_sim_c(self, c1, c2):
		""" Retourne la similarite entre les clusters d'id c1 et c2 
		( gere le fait que dans la matrice ne sont remplies que les cases c1 < c2) """
		if c1 != c2:
			return self.sim_matrix[c1,c2]
		else :
			return 1

	def set_sim_c(self, c1, c2, val):
		""" Affecte la valeur val comme similarite des clusters d'id c1 et c2
		(gere le stockage en partie superieure de la matrice uniquement)
		"""
		self.sim_matrix[c1,c2] = val
		self.sim_matrix[c2,c1] = val

	def initialize_clustering(self, object_names, sim_matrix):
		"""
		Initialisation de 
		- la liste des clusters (les singletons d'objets)
		- la liste des ppc (clusters les plus proches de chaque cluster)
		- la matrice (fournie en argument)
		"""
		# matrice de similarité entre clusters (au départ entre objets)
		self.sim_matrix = sim_matrix

		# le nb d'objets
		self.nb_objects = len(object_names)
		if self.nb_objects != sim_matrix.shape[0]:
			exit("La matrice et la liste d'objets ne sont pas de meme taille! J'arrête tout!")
		self.actif = list(range(len(object_names)))
		
		#Création des premiers plus proches clusters
		for i in range(len(object_names)) : 
			key = numpy.argmax(sim_matrix[i,:])
			self.ppc.append((max(sim_matrix[i,:]),  key))
			self.clusters.append(Dendrogram(object_names[i]))
		
		
	def clusterize(self, object_names, sim_matrix, nbclusters=1):
		""" Calcule le clustering étant donnés :
		object_names = une liste de noms d'objets (dont le rang constitue l'id)
		sim_matrix   = une matrice de similarite entre ces objets
		nbclusters   = le nb de clusters voulus
		"""
		self.initialize_clustering(object_names, sim_matrix)
		if self.trace :
			for i in self.clusters :
				print(i)
		while len(self.actif) > nbclusters :
			similar, to_merge = max(self.ppc)
			mergeur = numpy.argmax(self.ppc, axis = 0)[0]

			k = 0
			for clu in self.ppc :
				if clu[1] == to_merge:
					self.ppc[k] = (clu[0], mergeur)
				k += 1
			
			sim_matrix[: ,to_merge] = numpy.zeros(sim_matrix.shape[0])
			self.ppc[mergeur] = (max(sim_matrix[mergeur,:]), numpy.argmax(sim_matrix[mergeur,:]) )
			self.ppc[to_merge] = (0,-1)
			self.actif.remove(to_merge)
			if self.trace:
				print("Merged", object_names[to_merge],
					"with",	object_names[mergeur],
					"at",		similar)
			
			self.clusters[mergeur] = Dendrogram(\
								self.clusters[mergeur],\
								self.clusters[to_merge],\
								similar)
			self.clusters[to_merge] = None
		
		self.clusters = filter(lambda a: a, self.clusters)

	def dump(self,stream):
		""" Affichage des membres des clusters, en l'état courant du clustering hiérarchique """
		for c,cl in enumerate(self.clusters):
			stream.write('Cluster ' + str(c) + ' = ')
			cl.print_members(stream)
			stream.write('\n')

def thesaurus2simmatrix(thesaurusstream):
	""" Lit un stream contenant un thesaurus au format "un objet par ligne, et ses similaires separes par tab"
	et construit la liste des objets representes, 
	et une matrice de similarite entre ces objets
	"""
	# dictionnaire de dictionnaire, pour la sim entre 2 objets
	# clé1=id1 clé2=id2 val= sim(id1,id2)
	object2objectsim = {}
	# la liste des objets, dans laquelle le rang de l'objet est son id
	objects = []
	# dictionnaire cle=objet (string), valeur = id, rang dans la matrice de similarite
	object2id = {}

	id = -1
	linen = 0
	line = thesaurusstream.readline()
	while line != '':
		linen += 1
		line = line[0:-1]
		cols = line.split('\t')
		object1 = cols[0]
		if object1 not in object2id:
			id += 1
			object2id[object1] = id
			objects.append(object1)
		id1 = object2id[object1]
		for objsim in cols[1:]:
			if not objsim:
				continue
			(object2, sim) = objsim.split(':', 1)
			sim = Decimal(sim)
			if object2 not in object2id:
				id += 1
				object2id[object2] = id
				objects.append(object2)
			id2 = object2id[object2]

			if id1 in object2objectsim:
				object2objectsim[id1][id2] = sim
			else:
				object2objectsim[id1] = { id2 : sim }

		line = thesaurusstream.readline()

	# nb d'objets à clusteriser
	n = len( objects )

	# matrice nxn, remplie avec des 0 (objet numpy.ndarray : tableau multi-dimensionnel)
	matrix = numpy.zeros( (n,n), dtype=Decimal )

	for id1 in object2objectsim:
		for id2 in object2objectsim[id1]:
			# on ne stocke que la demi-matrice : uniquement les id2 superieurs aux id1
			#if id2 > id1:
			matrix[id1][id2] = object2objectsim[id1][id2] 

	return (objects, matrix)

usage = """Implementation du clustering ascendant agglomeratif (HAC)
		   de type single-link ou complete-link
		   """+sys.argv[0]+""" [options] THESAURUS_FILE
			  
		   Convertit le thesaurus fourni en matrice de similarité et calcule le clustering
"""

parser = argparse.ArgumentParser(usage=usage)
parser.add_argument('thesaurus_file', help = 'fichier thesaurus', default=None)
parser.add_argument('-n', "--nbclusters", type=int, default=1, help='Nb (minimal) de clusters voulu. Default=1')
parser.add_argument('-t', "--trace", type=int, default=0, help='entier 0, 1 ou 2 : Déclenche diverses traces pendant le déroulement de l\'algo. Default=0')
args = parser.parse_args()


sys.stderr.write("Ouverture thesaurus...\n")
thesaurus_stream = open(args.thesaurus_file)

sys.stderr.write("Lecture thesaurus...\n")
(object_names, simmatrix) = thesaurus2simmatrix(thesaurus_stream)

sys.stderr.write("Nb d'objets a clusteriser : " + str(len(object_names)) + "\n")

hac = HAC(trace=args.trace)
for i in hac.clusters :
	print(i)
# A DECOMMENTER une fois l'implementation faite
hac.clusterize(object_names, simmatrix, nbclusters=args.nbclusters)

print("\nRésultat clustering hiérarchique en %d clusters:\n" % args.nbclusters)
hac.dump(sys.stdout)

if hac.trace:
	sys.stderr.write( "\nDétail des fusions:\n" + '\n'.join([str(x) for x in hac.clusters]) + "\n")
