Semi-supervised WSD README
==========================

Ce dossier contient les données pour réaliser des expériences dans le cadre des projets M1-LI sur le WSD semi-supervisé.

Description des données
-----------------------
	- README.md : ce fichier
	- data/ : répertoire contenant les données annotées pour 5 verbes (abattre, aborder, affecter, comprendre et compter)
		- .conll : fichier contenant les phrases au format conll.
		- .tok_ids : fichier contenant les ids des tokens cibles (Warning : les ids suivent le format conll et commencent à 1) alignés avec les phrases du fichier .conll correspondant.
		- .gold : fichier contenant les classes gold des tokens cibles alignées avec les phrases du fichier .conll correspondant.
	- inventaire_de_sens : fichier contenant l'inventaire de sens utilisé pour l'annotation des données. Il donne notamment les ids des classes (colonne SenseID) pour chaque verbe. 

 Référence
----------

	- Roberto Navigli Navigli, R. (2009). Word sense disambiguation: A survey. ACM computing surveys (CSUR), 41(2), 10 --> https://arxiv.org/pdf/1508.01346.pdf
		 * En particulier lire les chapitres:
			- 2.3 : Context representation
			- 4 : Unsupervised Disambiguation 





