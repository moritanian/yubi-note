#-*- coding:utf-8 -*-
# use cn1

import serial
import numpy as np
import time 
import sys
import atexit
import time 
import pickle
from datetime import datetime

import os
import math


class ShokacChip:
	# static member
	Censor_Cof_A = np.array([[-2.369 ,0.053, -0.529],[-0.078, -2.037, -0.349],[0.085, 0.357, 1.665]]) # 2U43
		# np.array([[-2.835 ,-0.478, -1.271],[-0.084, -3.414, -0.736],[0.872, -0.019, 2.729]])  kihara
		# np.array([[-2.171, 0.4, -0.137],[-0.095, -2.788, -0.456],[0.323, 0.172, 1.826]])
	Censor_Cof_T = np.array([-0.201, 0.454, -0.506]) # 2U43
		#np.array([-0.215, 0.609, -0.913])
	
	SAVE_FLAG = True

	def __init__ (self):	
		self.init_press_arr = np.zeros(3)
		self.ser = None
		self.save_data_list = {
			"raw": {"x": [], "y": [], "z": [], "T":[]},
			"f": {"x": [], "y": [], "z": []},
			"time": []
		}
		self.start_time = None 

		 # [[times, dataX, dataY, dataZ, T][times, dataX, dataY,dataZ]]

	# raw_val : 2byte int * 4element
	def calc_f_from_arr(self, raw_arr):
		dv_arr = np.array([raw_arr[0], raw_arr[1], raw_arr[2], raw_arr[3]]) * 3.3 /1024.0
		dv_arr_dash = dv_arr[0:3] - ShokacChip.Censor_Cof_T * dv_arr[3]
		f = np.dot(ShokacChip.Censor_Cof_A ,dv_arr_dash) - self.init_press_arr

		if ShokacChip.SAVE_FLAG:
			self.save_data_list["raw"]["x"].append(raw_arr[0])
			self.save_data_list["raw"]["y"].append(raw_arr[1])
			self.save_data_list["raw"]["z"].append(raw_arr[2])
			self.save_data_list["raw"]["T"].append(raw_arr[3])
			self.save_data_list["f"]["x"].append(f[0])
			self.save_data_list["f"]["y"].append(f[1])
			self.save_data_list["f"]["z"].append(f[2])
			if self.start_time == None:
				self.start_time = time.clock()
			self.save_data_list["time"].append(time.clock() - self.start_time)

		return f

	# character からint　array に変換	
	def convert_array_from_char(self, str):
		OffsetIndex = 4 # 2
		raw_arr = np.empty(4)
		for i in range(4):
			int_num = int(str[OffsetIndex + i*4 : OffsetIndex+(i+1)*4], 16) # 2-5, 6-9, 10-15, 16-19 X, Y, Z, T
			raw_arr[i] = int_num
		return raw_arr		
	
	def one_read(self):
		self.ser.write("020201".encode("ascii")) # 020201
		raw_str = self.ser.read(22) # 20
		#print (raw_str)
		raw_arr = self.convert_array_from_char(raw_str)
		#print (raw_arr)
		return self.calc_f_from_arr(raw_arr)
	
	def init_serial(self):
		atexit.register(self.exit)

		if(sys.platform.startswith('linux') or sys.platform.startswith('cygwin')):
			dev_list = os.listdir('/dev/')
			for i in range(5):
				dev_name = "ttyACM" + str(i)
				if dev_name in dev_list:
					break 
			print (dev_name)
			full_dev_path = "/dev/" + dev_name
			self.ser = serial.Serial(full_dev_path, timeout=0.1) 
		elif(sys.platform.startswith('win')):
			print("windos")
			self.ser = serial.Serial()
			self.ser.baudrate = 9600 # 変える？
			for i in range(20):
				try:
					self.ser.port = "COM" + str(i)
					self.ser.open()
					print ("open" + str(i) + " port")
					break
				except:
					#print("miss" + str(i))
					i=i				

		self.ser.write("020301".encode("ascii")) # 020301
		return

	# センサ初期値 補正
	def init_device(self):
		time.sleep(2.0) # wait for stable
		
		sum_arr = np.zeros(3)
		get_num = 10
		for i in range(get_num):
			time.sleep(0.2)
			sum_arr += self.one_read()

		self.init_press_arr = sum_arr/get_num
		print ("init_press arr = ")
		print (self.init_press_arr)

	def exit(self):
		self.ser.close()	
		if ShokacChip.SAVE_FLAG:
			self.saveData()

		print ("successfully ended")

	def saveData(self, file_path = ""):
		if file_path == "":
			file_path = "./data/dump/saveData" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".pickle"
		filename = open(file_path, 'wb')
		pickle.dump(self.save_data_list, filename)
		filename.close()

class LetterDetector:
	# parameter
	REQUIRE_INPUT_COUNT = 5
	OUT_COUNT = 5
	INPUT_PRESSX_THRETHOLD_HIGH = 0.3 # [N]	
	INPUT_PRESSX_THRESHOLD_LOW = 0.2 # [n]

	def __init__ (self):
		self.inputOn = False
		self.resetParams()
		self.posWList = []
		self.posHList = []
	

	def resetParams(self):
		self._x = 0.0
		self._y = 0.0
		self._z = 0.0
		self._xList = [0.0]
		self._yList = [0.0]
		self._zList = [0.0]
		self.inputOnCount = 0
		

	def newPressInput(self, x, y, z):
		lp_ratio = 0.4
		self._x = self._x * (1 - lp_ratio) + x * lp_ratio	
		self._y = self._y * (1 - lp_ratio) + y * lp_ratio	
		self._z = self._z * (1 - lp_ratio) + z * lp_ratio

		if self.inputOn == False:
			if self._z > LetterDetector.INPUT_PRESSX_THRETHOLD_HIGH:
				self.inputOnCount += 1
			else:
				self.inputOnCount = 0
			
			if self.inputOnCount > LetterDetector.REQUIRE_INPUT_COUNT:
				self.inputOnCount = 0
				self.inputOn = True
				self.posWList = []
				self.posHList = []

		else:
			if self._z < LetterDetector.INPUT_PRESSX_THRESHOLD_LOW:
				self.inputOnCount += 1
			else: 
				self.inputOnCount = 0 

			if self.inputOnCount > LetterDetector.OUT_COUNT: # out + recognition
				self.inputOnCount = 0
				self.inputOn = False
				self.recogLetter()
				self.resetParams()
				return True

		if self.inputOnCount == False:
			return

		self._xList.append(self._x)
		self._yList.append(self._y)
		self._zList.append(self._z)
		if self.posWList == []:
			self.posWList.append(- self._x)
			self.posHList.append(- self._y)			
		else:
			self.posWList.append(self.posWList[-1] -  self._x)
			self.posHList.append(self.posHList[-1] - self._y)
		return False

	def getInnerPressVal(self):
		return np.array([self._x, self._y, self._z])

	def recogLetter(self):
		return