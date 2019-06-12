# coding: utf-8
import pprint as pp
import pandas as pd
from itertools import chain

class cat_dict :
	#Class to create one hot vector of categories.
	#All cat are upper case.
	def __init__(self):
		#Initialize with before the sentence and after the sentence.
		self.dict = {"BEFORE" : 0, "AFTER" : 1}

	def add_cat(self, cat):
		#Add a cat in the dictionary.
		#input : string
		#output : None
		if cat.upper() not in self.dict :
			self.dict[cat.upper()] = len(self.dict)

	def vector_of_cat(self, cat) :
		#Return the one hot vector of the cat.
		#input : string
		#output : list[int]
		vec = [0 for i in range(len(self.dict))]
		vec[self.dict[cat.upper()]] = 1
		return vec

def embedding_reader(file):
	#Read a file which contains embeddings. 
	#input : string / path to the file
	#output : dic[string]->list[float] / embeddings of the key
	#Format of the file :	one embedding by line, the word, a blank, floats splits with blank.
	#				The first line contains two int, the first in the number of embeddings, the second is the dim
	
	#Dic to be returned
	embeddings = {}
	
	with open(file, encoding = "utf-8" ) as stream :
		#Gathering of meta-data 
		nb, dim = [ int(s) for s in stream.readline()[:-1].split(" ") ]
		#Sum is for the median vector
		sums = [0 for i in range(dim)]
		
		#Loop for reading a line and and adding the embedding with the key to the dic
		for i in range(nb) :
			datas = stream.readline()[:-1].split(" ")
			vec = [float(s) for s in datas[1:]]
			embeddings[datas[0]] = vec
			sums = [sums[i]+vec[i] for i in range(dim)]
			stream.readline()
		
		#Calculate of the median embedding
		sums = [sums[i]/nb for i in range(dim)]
		embeddings["#MEDIAN#"] = sums
	
	return embeddings

def sentence2vec(list_of_conll_lines, key, embeddings, left, right, cat_dictio) :
	#Turn a sentence to a vector.
	#input list_of_conll_lines : list[] / list of words and meta datas in a sentence
	#input key : string / the word we want to classify
	#input embeddings : dic[string]->list[float] / embeddings
	#input left : int / left window
	#input right : int / right window
	#input cat_dictio : dictio of categories
	
	#Initialise a dataFrame, one row is one line of a conll file
	datas = pd.DataFrame(
			columns = ["index", "surf", "lemme", "simpCat", "detCat",
						"Useless", "linkIndex", "linkRel"])
	#Add all words and meta datas in the data frame
	for word in list_of_conll_lines :
		datas = datas.append(pd.Series( word, index = datas.columns ), ignore_index = True, )
	#Clean the dataframe.
	datas.drop(columns = ['Useless'], inplace = True)
	datas.set_index('index', inplace = True)
	datas["linkIndex"] = [int(s.split("|")[0]) for s in datas["linkIndex"]]
	datas["linkRel"] = [s.split("|")[0] for s in datas["linkRel"]]
	
	#Add all categories into the dictio of categories
	for cat in datas["detCat"] :
		cat_dictio.add_cat(cat)
	
	#Find the index of the word to classify
	key_index = int(datas["lemme"][datas["lemme"] == key].index[0])
	

	vector = []
	cats = []
	#Add the median vector when the word is near the start of the sentence
	if key_index-left < 1:
		for i in range(key_index-left,1):
			vector += embeddings["#MEDIAN#"]
			cats += ["BEFORE"]
	#Add all vectors inside the sentence
	for i in chain(range(max(1, key_index-left), key_index),
					range(key_index+1, min(len(list_of_conll_lines), key_index+right)+1)) :
		vector+= embeddings.get(datas["lemme"].at[str(i)], embeddings["#MEDIAN#"])
		cats += [datas["detCat"].at[str(i)]]
	#Add the median vector when the word is near the end of the sentence
	if len(list_of_conll_lines) < key_index+right:
		for i in range(len(list_of_conll_lines)+1,key_index+right+1):
			vector += embeddings["#MEDIAN#"]
			cats += ["AFTER"]
	return (vector,cats)

def file2vec(file, key, embeddings, left, right) :
	#Turn a file into a list of vector
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
	print(embeddings["#MEDIAN#"])
	return vector_list

def merge_with_gold_file(vectors, gold_file):
	vec_and_gold = []
	with open(gold_file, encoding = "utf-8") as stream :
		for vector in vectors :
			gold = int(stream.readline()[:-1])
			vec_and_gold.append((vector, gold))
	return vec_and_gold



embeddings = embedding_reader("../data/w2v_final.txt")
print("embeddings")
vecs = file2vec("../data/compter/compter-150.conll", "compter", embeddings, 2, 3)
print("vecs")

datas = merge_with_gold_file(vecs,"../data/compter/compter-150.gold")
import pickle
pickle.dump(datas, open('compter.pkl', 'wb'))
with open('compter.pkl', 'rb') as f1:
	datas = f1.read()