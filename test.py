#-*- coding:utf-8 -*-
# use cn1

import matplotlib.pyplot as plt
import numpy as np
import time 


from Shokac import ShokacChip, LetterDetector
		
#main
if  __name__ == "__main__":

	# censor chip setting
	shokacChip = ShokacChip()
	shokacChip.init_serial()
	shokacChip.init_device()

	letterDetector = LetterDetector()
	
	# plot setting
	fig, ax = plt.subplots(1, 1)
	xPoints = np.array([0.0, 0.0])
	yPoints = np.array([0.0, 0.0])
	lines, = ax.plot(xPoints, yPoints)

	plotLim = 10.0
	ax.set_xlim((-plotLim, plotLim))
	ax.set_ylim((-plotLim, plotLim))
	
	while True:
		press_arr =  shokacChip.one_read()
		#print (press_arr)
		

		x = press_arr[0]
		y = press_arr[1]
		z = press_arr[2]
		rec = letterDetector.newPressInput(x, y, z)
		innerVal = letterDetector.getInnerPressVal()

		print (innerVal)
		print (letterDetector.inputOn)
		print (letterDetector.inputOnCount)
		print ("\n\n")

		#xPoints = np.append(xPoints, y)
		#yPoints = np.append(yPoints, z)
		xPoints[1] = innerVal[0] 
		yPoints[1] = innerVal[1]

		#lines.set_data(xPoints, yPoints)
		#lines.set_data(np.array(letterDetector._yList), np.array(letterDetector._zList))
		#plt.pause(.01)
		if rec:
			lines.set_data(np.array(letterDetector.posWList), np.array(letterDetector.posHList))
			print (letterDetector.posWList)
			print (letterDetector.posHList)
			plt.pause(.01)

		pos = {"x": x , "y" : y, "z" : z }

		#json_str = json.dumps(pos)
		
		time.sleep(0.05)
	
	ser.close()
