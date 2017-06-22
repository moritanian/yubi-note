#-*- coding:utf-8 -*-
# use cn1

import matplotlib.pyplot as plt
import numpy as np
import atexit
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
	xPoints = []
	yPoints = []
	zPoints = []
	times = []

	count = 0
	start = time.clock()

	while True:
		press_arr =  shokacChip.one_read()
		x = press_arr[0]
		y = press_arr[1]
		z = press_arr[2]
		
		rec = letterDetector.newPressInput(x, y, z)

		#if letterDetector.inputOn:
		xPoints.append(x)
		yPoints.append(y)
		zPoints.append(z)
		times.append(time.clock() -start)
		time.sleep(0.02)

		
		if time.clock() - start > 10:
			break

		count += 1
		if count == 5:
			count = 0
			print(press_arr)


			#break

	print ("plot")
	plt.plot(times, xPoints, '-', label="x[N]")
	plt.plot(times, yPoints, '-', label="y[N]")
	plt.plot(times, zPoints, '-', label="z[N]")
	font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }

	plt.xlabel('time (s)', fontdict=font)
	plt.ylabel('f (N)', fontdict=font)

	plt.legend(loc='best')
	plt.show()