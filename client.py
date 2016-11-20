import cv2
import numpy as np
import socket
import time
directory = '/usr/share/OpenCV/haarcascades/'
cap = cv2.VideoCapture(0)
cap.set(5, 144)

lower = np.array([0,50,50], dtype = 'uint8')
upper = np.array([21,255,255], dtype = 'uint8')
#eyesHaar = cv2.CascadeClassifier( directory + 'haarcascade_eye_tree_eyeglasses.xml' )
#facesLbp = cv2.CascadeClassifier ( '/usr/share/OpenCV/lbpcascades/lbpcascade_frontalface.xml')
last_known_face = None
initiated = None

redLower=np.array([0, 120, 100], dtype = 'uint8') # old [0,120,140] [0,120,140]
redUpper=np.array([45, 255, 255], dtype = 'uint8')


blackLower = np.array([110,100,40], dtype = 'uint8')#[110,130,60 - noapte], [110,100,0] - zi
blackUpper = np.array([130,255,255], dtype = 'uint8')#[130,255,255]
pointerX = 222
pointerY = 222
clicked = False 
clickedDr = False
modTastatura = False
scaleFactor = 1

#[ X , Y , W , H , LITERA ] 
KeybCoord = [600,0,640,40]

#APO : CULORI....LOWER,UPPER
'''	[86, 31, 4], [220, 88, 50],
	[25, 146, 190], [62, 174, 250],
	[103, 86, 65], [145, 133, 128]], dtype = 'uint8')'''
hsv = None
frame = None
def findContourCenter(lower,upper,color,debugName,debug,areaMin,areaMax):
	rezultat = (-1,-1,-1,-1)
	global hsv,frame
	mask = cv2.inRange(hsv,lower,upper)
	maxArea = 0 
	trash,contours,trash = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		# CAT DE MARE SA FIE CONTURUL CA SA IL LUAM DE BUN
		myArea = cv2.contourArea(cnt)
		if areaMin<myArea:
			cv2.drawContours(frame,[cnt],0,color,2)
			x3,y3,w3,h3 = cv2.boundingRect(cnt)
			cv2.rectangle(frame,(x3,y3),(x3+w3, y3+h3),color,2)
			if(myArea > maxArea):
				maxArea = w3 * h3 
				rezultat = (x3,y3,w3,h3)
		
	#detected = cv2.bitwise_and(frame, frame, mask=mask)
	#cv2.imshow(debugName, detected)
	return rezultat
def findContourCenterBlack(lower,upper,color,x,y,w,h):
	rezultat = []
	global hsv,frame
	hsv_pt_black = hsv[y:y+h, x:x+w]
	mask = cv2.inRange(hsv_pt_black,lower,upper) 
	trash,contours,trash = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		# CAT DE MARE SA FIE CONTURUL CA SA IL LUAM DE BUN
		if 5 <cv2.contourArea(cnt) < 200:
			#cv2.drawContours(frame,[cnt],0,color,2)
			x3,y3,w3,h3 = cv2.boundingRect(cnt)
			cv2.rectangle(frame,(x + x3,y + y3),(x + x3+w3, y + y3+h3),color,2)
			clickSt = x3 + w3/2
			clickDr = y3 + h3/2
			rezultat.append([x3,y3,w3,h3])
	return rezultat
def click():
	global clicked, clickedDr
	if(False == clicked) :
		check_hit_tastatura()
	clicked = True
def clickDr():
	global clickedDr
	clickedDr = True
def notClickDr():
	global clickedDr
	clickedDr = False

def notClick():
	global clicked
	clicked = False
def mutaCursor(x,y):
	global pointerX, pointerY, frame
	pointerX = x
	pointerY = y
	cv2.circle(frame, (x,y),5, (255,255,0),2)
	#print 'MUT LA ' + str(x) + ' , ' + str(y)
def undeMut(patrat):
	(x,y,w,h) = patrat
	if(-1 == x ) :
		return 
	mutaCursor( x + w / 2 , y + h / 2 ) 
def sendInfo():
	global pointerX,pointerY,clicked,sok,scaleFactor
	my_bytes = bytearray();
	auxX = int( pointerX / scaleFactor)
	auxY = int ( pointerY / scaleFactor)
	my_bytes.append(auxX >> 8)
	my_bytes.append(auxX & 0xff)
	my_bytes.append(auxY >> 8)
	my_bytes.append(auxY & 0xff)
	if( clicked ) :
		my_bytes.append(1)
	else :
		my_bytes.append(0)
	#print ('TRIMIT : ', pointerX,pointerY, 0 +  clicked)
	sok.send(my_bytes)
startTime = 0
images = 0
def detect():
	while(True):
		# Capture frame-by-frame
		
		global hsv,frame,clicked,scaleFactor,images,startTime,KeybCoord
		ret, frame = cap.read()
		frame = cv2.flip(frame,1)
		if(startTime == 0 ):
			startTime = time.time()
		#print time.time() - startTime
		images = images + 1
		maxY,maxX,trash = frame.shape

		#print frame.shape
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (21,21), 0 ), cv2.COLOR_BGR2HSV)
		
		#faces = facesLbp.detectMultiScale (gray, 1.1, 5 ) 
		'''
		#FACE DETECT
		for (x,y,w,h) in faces:
			sub_gray = gray[y:y+h, x:x+w]
			eyes = eyesHaar.detectMultiScale(sub_gray, 1.1, 5 ) 
			if(len(eyes) == 0 ):
				continue;
			for (x2,y2,w2,h2) in eyes:
				cv2.rectangle(frame,(x+x2,y+y2),(x+x2+w2,y2+y+h2),(0,255,0),2)
			cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
		'''
		''' skin color detect :
		mask = cv2.inRange(hsv , lower, upper)
	
	
		skin = cv2.bitwise_and(frame, frame, mask = mask)
		cv2.imshow('skin',skin)
		'''
		#AICI FACI TU APO
		cntsBlue = findContourCenter(blackLower,blackUpper,(0,255,255),'blue',0,100,12000)
		cntsRed = findContourCenter(redLower,redUpper,(0,255,255),'red',0,300,24000)
		# CE,UNDE MUT:	
		#if(len(cntsBlue) == 1 ) :
		undeMut( cntsBlue )
		#if( len( cntsRed) == 1):
		check( cntsRed)
		if(clicked):
			cv2.rectangle(frame,(0,0),(20,20),(255,0,255),5)
		if(clickedDr):
			cv2.rectangle(frame,(30,0),(50,20),(255,0,255),5)
		cv2.rectangle(frame,(0,0),(int(maxX * scaleFactor) ,int(maxY * scaleFactor)), (0,255,255), 2)
		sendInfo()
		cv2.putText(frame,str(int(images / (time.time() - startTime))) + ' FPS ',(20,450),  cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2)

		keyboardDoYourJob()
		
		cv2.imshow('f2', frame)
		if cv2.waitKey(1) & 0xFF == ord('q') :
			break
		
	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()
shift = False
ctrl = False

def trimit_text(char):
	global lastPrintedChar,shift,ctrl
	lastPrintedChar = char
	if('sh' == char ) :
		shift = True
		return
	if('ct' == char ) :
		ctrl = True 
		return
	lastPrintedChar = ''
	if(ctrl):
		lastPrintedChar = lastPrintedChar + 'ctrl-'
	if(shift):
		lastPrintedChar = lastPrintedChar + 'sh-'
	shift = False
	ctrl = False
	lastPrintedChar = lastPrintedChar + char

	
def check_hit_tastatura():
	global KeybCoord, modTastatura, pointerX, pointerY
	if(KeybCoord[0] < pointerX < KeybCoord[2] + KeybCoord[0] and KeybCoord[1] < pointerY < KeybCoord[3] + KeybCoord[1]):
		modTastatura = not modTastatura
		return 
	if(False == modTastatura ) :
		return 
	if( margin > pointerY ) :
		return 
	for (x,y,w,h,char) in litere:
		if(x< pointerX < x + w and y < pointerY < y + h):
			trimit_text(char)
			return
def keyboardDoYourJob():
		global KeybCoord
		if(False == modTastatura) : 
			cv2.rectangle(frame,(KeybCoord[0],KeybCoord[1]), (KeybCoord[0] + KeybCoord[2] , KeybCoord[1] + KeybCoord[3]), (150,150,0), 4)
			return 
		cv2.rectangle(frame,(KeybCoord[0],KeybCoord[1]), (KeybCoord[0] + KeybCoord[2] , KeybCoord[1] + KeybCoord[3]), (0,0,255), 4)
		printTaste()

		## ce am gasit
		cv2.rectangle(frame, (300,0),(400,40),(0,0,0),-1)
		cv2.putText(frame,lastPrintedChar,(300,20),  cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2)
litere = []
margin = KeybCoord[1] + KeybCoord[3] + 5
lastPrintedChar = ''
taste = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l', 'en', 'z','x','c','v','b','n','m','ct','sh','bk', 'ct', 'ct', 'sh', 'sh', 'sp', 'sp', 'sp', 'sp', 'sp', 'sp', 
'enter','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a']
def init():
	X = 640
	Y = 480
	#for i in range ( )
	#for i in range(0 , 5 ):
		#for j in range ( 0, 12):
			#litere.append ( ( Y * i / 5,  X * j / 12 , Y / 5, X / 12 , taste [ i * 12 + j ]))
	for i in range(0,10):
		for j in range(0,4):
			litere.append((X * i / 10, margin + Y * j / 4, X/10 , Y/4,taste[i + j*10]))
	return
def printTaste():
	for (x,y,w,h,char) in litere:
		cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
		cv2.putText(frame,char,(x + w/4,y+h/2),cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,255),2)
def check( b ):
	marginOfError = 15
	#if( a[1] + a[3] + marginOfError > b[1] ) : 
	cv2.circle(frame, (b[0] + b[2]/2,b[1] + b[3]/2),5, (255,0,255),2)
	if( b[1] + b[3]/2 < 240 ) :
		click()
	else:
		notClick()
	if( b[0] + b[2] / 2 > 320 ) :
		clickDr()
	else:
		notClickDr()

sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sok.connect(('10.0.0.100', 10000))
#sok.connect(('10.0.0.100', 10000))
#sok.connect(('localhost',10010))
sok.send('Kappa\0')
init()
detect()
