# coding: utf-8
import pprint as pp
import pandas as pd

def sentence2vec(listOfConllLines, key, embeddings, left, right) :
	#index, surf, lemme, simpCat, detCat, _, linkIndex, linkRel = 
	datas = pd.DataFrame(
			columns = ["index", "surf", "lemme", "simpCat", "detCat",
						"Useless", "linkIndex", "linkRel"])
	for word in listOfConllLines :
		print(pd.Series( word, index = datas.columns ))
		datas = datas.append(pd.Series( word, index = datas.columns ), ignore_index = True, )
	datas.drop(columns = ['Useless'], inplace = True)
	datas.set_index('index', inplace = True)
	datas["linkIndex"] = [int(s.split("|")[0]) for s in datas["linkIndex"]]
	datas["linkRel"] = [s.split("|")[0] for s in datas["linkRel"]]
	print(datas)
	input()
		
	pass 

def file2vec(file, embeddings, key):
	vecs = []
	with open(file, encoding = "utf-8") as stream :
		line = stream.readline()
		current = []
		while line :
			if line[:-1]:
				current.append(line[:-1].split("\t")[:-2])
			else :
				vecs.append(sentence2vec(current, key, embeddings,2, 3))
				current = []

			line = stream.readline()

def embeddingReader(file):
	embeddings = {}
	with open(file, encoding = "utf-8" ) as stream :
		nb, dim = [ int(s) for s in stream.readline()[:-1].split(" ") ]
		for i in range(nb) :
			datas = stream.readline()[:-1].split(" ")
			embeddings[datas[0]] = [float(s) for s in datas[1:]]
	return embeddings

embeddings = embeddingReader("../data/w2v_final.txt")

file2vec("../data/compter/compter-150.conll", "compter", embeddings)

