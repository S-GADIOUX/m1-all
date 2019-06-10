#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Vectors:

    def __init__(self):


class K-means:

    """
    data : dictionnaire contenant tous les vecteurs de données
    K : le nombre choisi de clusters à faire

    """

    def __init__(self, data, K):
        # Data = les vecteurs des données dont on dispose (en liste ou dico ?)
        self.data = data
        # K = Le nombre de clusters qu'on forme
        self.K = K

        #Dictionnaire qui contiendra pour chaque cluster:
            #Ses membres, son hypercentre courant, la similarité intracluster
        self.clusters


        #self.results = Les meilleurs résultats obtenus sur les runs avec différentes graines

        #Self graines = liste ou dico de vecteurs de taille K où le cluster i sera à la position i de la liste
        #self.graines = 


    def seeds_init(self, graines):
        """ Selon le choix fait peut initialiser les graines :
        - Au hasard
        - Sur des points au hasard
        - Further-first
        - K-means ++
        - Contrainte 1
        - Contrainte 2
        ...
        """

        #self.graines = 

        pass;



    def run(self, graines, data, K):
        
    """ Le run devra être effectué jusqu'à ce que la condition d'arrêt soit atteinte
    (A choisir : quand les clusters ne bougent plus ou autres ?)
    """
        

        # While les conditions d'arrêt pas atteintes:
            # On parcours les données une par une
            for vector in data :
                #Calcule les distances à chaque graine et retient la plus proche
                for g in graines:
                    #Appel à la fonction qui calcule et retient la meilleure distance ?

                #Ajoute le vecteur au dico de cluster là où ça correspond

            #Une fois l'itération finie :
            #Pour chaque cluster du dico clusters
                #On recalcule l'hypercentre

        #Quand les conditions d'arrêt sont atteintes et qu'on est sortis du while
        #Pour chaque cluster du dico clusters:
            #On calcule la similarité intracluster

