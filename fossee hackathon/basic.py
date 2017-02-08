import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
import copy
import findcons

numofim=11

def removenoise(im):
	max=0
	for i in range(0,len(im)):
		for j in range(0,(len(im[0]))):
			if im[i][j]<50:

				im[i][j]=0

def find_stars(obj):
	l = []
	limit = int( (len(obj) / 30.0) + 0.5 )
	for i in range(len(obj)-limit):
		for j in range(len(obj[0])-limit):
			if obj[i][j]>100:
				sum = 0
				max = 0
				max_loc=[0, 0]
				for ii in range(limit):
					for jj in range(limit):
						if(obj[i+ii][j+jj] > 100):
							sum+=obj[i+ii][j+jj]
							if obj[i+ii][j+jj]>max:
								max = obj[i+ii][j+jj]
								max_loc = [i+ii , j+ jj]
							obj[i+ii][j+jj] = 0
				l.append([sum , max_loc])
	return l

def shift_origin (l , pos):
	shiftx=pos[0]
	shifty=pos[1]
	for i in range(len(l)):
		l[i][1][0] -= shiftx
		l[i][1][1] -= shifty

def normalise (l , pos):
	if abs(pos[0])>0.00001:
		theta = math.atan(1.0*pos[1] / pos[0])
		if pos[1]<0 and pos[0]<0:
			theta=theta-math.pi

		elif pos[0]<0 and pos[1]>0:
			theta=theta+math.pi

		elif pos[1]==0:
			if (pos[0]>0):
				theta = 0
			else:
				theta = math.pi

	else:
		if pos[1]>0:
			theta=math.pi/2
		else:
			theta=-math.pi/2

	factor = 1000.0 / math.sqrt(pos[0]*pos[0] + pos[1]*pos[1])
	for i in range(len(l)):
		x = l[i][1][0]
		y = l[i][1][1]
		l[i][1][0] = factor*(x*math.cos(theta) + y*math.sin(theta))
		l[i][1][1] = factor*(y*math.cos(theta) - x*math.sin(theta))


def check (x_list , y_list , conlist,factor,maxval):
	tolerance = 5.0*factor
	maxclose=int(0)
	for i in range (len(conlist)):

		closeness = 0
		for j in range (2,7):
			maxclose=0
			for k in range (len(x_list)):
				if x_list[k] >= conlist[i][j][0]-tolerance and x_list[k]<=conlist[i][j][0] + tolerance:
					if y_list[k] >= conlist[i][j][1]-tolerance and y_list[k]<=conlist[i][j][1] + tolerance:
						dx = x_list[k] - conlist[i][j][0]
						dy = y_list[k] - conlist[i][j][1]
						maxclose= max(maxclose,(1-(math.sqrt((dy*dy+dx*dx)/2)/tolerance))*20)
						#if (1-(math.sqrt((dy*dy+dx*dx)/2)/tolerance))*20>0:
							#print(str(i)+" "+str(j)+" "+str(conlist[i][j])+" "+str(x_list[k])+" "+str(y_list[k]))

			closeness+=maxclose			
		maxval[i]=max(maxval[i],closeness)

		
		
def caller(to_check, final_stars, conlist,maxval):
	for i in range(0,len(final_stars)):
		for j in range(0, len(final_stars)):
			if j==i:
				continue
			#temp=copy.deepcopy(to_check);
	#for i in range (2,3):
	#	for j in range (1,2):
			shift_origin(to_check , to_check[i][1])
			pos = to_check[j][1]
			factor = 1000.0 / math.sqrt(pos[0]*pos[0] + pos[1]*pos[1])
			normalise (to_check , to_check[j][1])
			
			x_coods = []
			y_coods = []
			for k in range (len (to_check)):
				x_coods.append(to_check[k][1][0])
				y_coods.append(to_check[k][1][1])

			check(x_coods , y_coods , conlist , factor,maxval)
			templ=copy.deepcopy(to_check)




print('\n')
print("Namasate! Welcome to the constellation detection program:")
print("You will have to enter the file you want to check...")
print("enter the number of file you want to check (between 1 and 10): ")
s=''

while ( 1):
	s=input()
	if int(s)>0 and int(s)<11:
		break;
	else:
		print('Invalid Input. Please enter a number between 1 and 10 :')	
	
s='samples/sample'+str(s)+'.jpg'

image = cv2.imread(s)
print('')
print("Your image is being processed...")
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#img = cv2.imread('gray_image2.png',0)
#ret,thresh1 = cv2.threshold(img,100,255,cv2.THRESH_BINARY)
#ret,thresh2 = cv2.threshold(img,100,255,cv2.THRESH_BINARY_INV)
#ret,thresh3 = cv2.threshold(img,127,255,cv2.THRESH_TRUNC)
#ret,thresh4 = cv2.threshold(img,127,255,cv2.THRESH_TOZERO)
#ret,thresh5 = cv2.threshold(img,127,255,cv2.THRESH_TOZERO_INV)

conlist=[]
findcons.findconstellation(numofim , conlist)


removenoise(gray_image)

obj = gray_image
stars = find_stars(obj)
stars.sort()
final_stars = []
to_check = []
num = min(len(stars) , 7)
num2 = min(len(stars) , 10)
last = len(stars)
for i in range(num):
	final_stars.append(stars[last-1-i])
for i in range(num2):
	to_check.append(stars[last-1-i])

maxval=[]
for i in range(numofim):
	maxval.append(0)
caller(to_check, final_stars, conlist,maxval)

ans=[]
f=file("images/pics.txt", "r")
fl=f.readlines()
for i in range(numofim):
	ans.append([maxval[i],fl[i].split("\n")[0]])
print(ans)
ans.sort()
ans.reverse()

if (ans[0][0]<30):
	print("This does not match any of the constellations in our database at first attempt...")
	a = raw_input("Press 'y' if you want to conduct a deeper check. Note that these answers may not be accurate: ")
	if (a == 'y'):
		for i in range(5):
			if (ans[i][0] > 15.5):
				print(str(i+1) + ". " + ans[i][1])

else:
	print("The constellation(s) it resembles the most in decreasing order is: ")
	for i in range(5):
		if (i>0 ) and (ans[0][0]-15>ans[i][0]):
			break
		if(ans[i][0]>20):
			print(str(i+1) + ". " + ans[i][1])
