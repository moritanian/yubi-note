#-*- coding:utf-8 -*-
# use cn1
import matplotlib.pyplot as plt
import numpy as np
import atexit
import time 
import pickle

def data_view(file_path):
	filename = open(file_path, 'rb')
	fig = pickle.load(filename)
	plt.plot(fig["time"] ,fig["raw"]["x"], '.', label="x")
	plt.plot(fig["time"] ,fig["raw"]["y"], '.', label="y")
	plt.plot(fig["time"] ,fig["raw"]["z"], '.', label="z")
	plt.plot(fig["time"] ,fig["raw"]["T"], '.', label="T")
	font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }

	plt.xlabel('time (s)', fontdict=font)
	plt.ylabel('', fontdict=font)
	plt.legend(loc='best')
	plt.show()

base_name = "./data/dump/"

file_name = "saveData2017_06_22_22_28_08.pickle"
print(base_name + file_name)
data_view(base_name + file_name)
