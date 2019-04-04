# coding: utf8 

import torch, torch.nn

class MyNetwork(torch.nn.Module):

	def __init__(self):
		super(MyNetwork, self).__init__()
		self.hidden = []
		self.activation = nn.Tanh()
