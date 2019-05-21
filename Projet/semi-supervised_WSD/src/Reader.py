# coding: utf-8
import pprint as pp
import pandas as pd
from itertools import chain

class cat_dict :

	def __init__(self):
		self.dict = {"BEFORE" : 0, "AFTER" : 1}

	def add_cat(self, cat):
		if cat.upper() not in self.dict :
			self.dict[cat.upper()] = len(self.dict)

	def vector_of_cat(self, cat) :
		vec = [0 for i in range(len(self.dict))]
		vec[self.dict[cat.upper()]] = 1
		return vec

def embedding_reader(file):
	embeddings = {}
	with open(file, encoding = "utf-8" ) as stream :
		nb, dim = [ int(s) for s in stream.readline()[:-1].split(" ") ]
		sums = [0 for i in range(dim)]
		for i in range(nb) :
			datas = stream.readline()[:-1].split(" ")
			vec = [float(s) for s in datas[1:]]
			embeddings[datas[0]] = vec
			sums = [sums[i]+vec[i] for i in range(dim)]
			stream.readline()
		sums = [sums[i]/nb for i in range(dim)]
		embeddings["#MEDIAN#"] = sums
	return embeddings

def sentence2vec(list_of_conll_lines, key, embeddings, left, right, cat_dictio) :
	datas = pd.DataFrame(
			columns = ["index", "surf", "lemme", "simpCat", "detCat",
						"Useless", "linkIndex", "linkRel"])
	for word in list_of_conll_lines :
		datas = datas.append(pd.Series( word, index = datas.columns ), ignore_index = True, )
	datas.drop(columns = ['Useless'], inplace = True)
	datas.set_index('index', inplace = True)
	datas["linkIndex"] = [int(s.split("|")[0]) for s in datas["linkIndex"]]
	datas["linkRel"] = [s.split("|")[0] for s in datas["linkRel"]]
	for cat in datas["detCat"] :
		cat_dictio.add_cat(cat)
	key_index = int(datas["lemme"][datas["lemme"] == key].index[0])
	vector = []
	cats = []
	for i in chain(range(max(1, key_index-left), key_index),
					range(key_index+1, min(len(list_of_conll_lines), key_index+right)+1)) :
		vector+= embeddings.get(datas["lemme"].at[str(i)], embeddings["#MEDIAN#"])
		cats += [datas["detCat"].at[str(i)]]
		
	return (vector,cats)

def file2vec(file, key, embeddings, left, right):
	vec_and_cats = []
	cat_dictio = cat_dict()
	with open(file, encoding = "utf-8") as stream :
		line = stream.readline()
		current = []
		while line :
			if line[:-1]:
				current.append(line[:-1].split("\t")[:-2])
			else :
				vec_and_cats.append(sentence2vec(current, key, embeddings, left, right, cat_dictio))
				current = []
			line = stream.readline()
	
	vector_list = []
	for vec, cats in vec_and_cats :
		for cat in cats :
			vec+= cat_dictio.vector_of_cat(cat)
		vector_list.append(vec)
	return vector_list

def merge_with_gold_file(vectors, gold_file):
	vec_and_gold = []
	with open(gold_file, encoding = "utf-8") as stream :
		for vector in vectors :
			gold = int(stream.readline()[:-1])
			vec_and_gold.append((vector, gold))
	return vec_and_gold

		

embeddings = embedding_reader("../data/w2v_final.txt")

vecs = file2vec("../data/compter/compter-150.conll", "compter", embeddings, 2, 3)

datas = merge_with_gold_file(vecs,"../data/compter/compter-150.gold")
pp.pprint(datas)