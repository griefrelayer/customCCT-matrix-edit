import os
from os.path import exists,isdir,join
from datetime import datetime
import glob
from sys import argv

default_filename="customCCT.txt"
wrongFormat="Wrong matrix file format!"
backupDir="./cct_backup/"
"""
This script is made for more convenient editing
of Custom color matrix from PhotonCamera Android app
"""

def main():
	matrixArray=readMatrix(default_filename) #parsing the customCCT.txt file
	global previousMatrix
	previousMatrix=matrixArray
	global matrixTemperature
	matrixTemperature="warm"
	global saveToWhere
	saveToWhere=default_filename # Where to save the customCCT.txt
	
	createBackup(default_filename) # making a copy of initial matrix/matrixes to revert to
	curr_matrix=switchMatrix(matrixArray)
	#curr_matrix=saturate(saturate(curr_matrix))
	updateScreen(curr_matrix)
	menu(curr_matrix,"root")
	
	saveMatrix(curr_matrix,saveToWhere,len(matrix)==1,"warm")
	#revertBackup(default_filename)
	print("customCCT file has one matrix" if len(matrix)==1 else "customCCT file has two matrixes")
	if(len(matrix)==2):
		print("Using warm matrix" if curr_matrix==matrix[0] else "Using cool matrix")

def switchMatrix(matrixArray, mod="warm"):
	global matrixTemperature
	if(len(matrixArray)==1):
		return matrixArray[0]
	elif(mod=="warm"):
		matrixTemperature="warm"
		return matrixArray[0]
	elif(mod=="cool"):
		matrixTemperature="cool"
		return matrixArray[1]
		
def menu(matrix,level="root"):
	while(True):
		if(level=="root"):
			updateScreen(matrix)
			print("="*50)
			print("1. Исправление баланса белого\n2. Баланс цветов\n3. Насыщенность цветов\n4. Нормализовать векторы\n5. Вернуть как было(восстановить из бэкапа)\n6. Сохранить результат(локально)\n7. Выход")
			menuVariants=['1','2','3','4','5','6','7']
			if(os.name=="nt" and exists('./adb/adb.exe')):
				print("="*50)
				print("Функции adb(требуется включенная отладка\nпо usb и подключенный телефон):\n8. Скопировать customCCT.txt с телефона\n9. Сохранить результат в customCCT.txt на телефоне")
				print("="*50)
				menuVariants.append('8')
				menuVariants.append('9')
			if(twoMatrixes):
				print("0. Сменить матрицу(теплая/холодная, автосохранение)")
				menuVariants.append('0')
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
			level="root"+menuIndex
		elif(level=="root1"): # White balance correction menu
			updateScreen(matrix)
			print("="*50)
			print("Пользуйтесь только в случае крайней необходимости\n(обычно лучше калибровать дисплей)\nДобавить во все тона:\n1. Красный\n2. Зеленый\n3. Синий\nУбрать из всех тонов:\n4. Красный\n5. Зеленый\n6. Синий\n7. Назад")
			menuVariants=['1','2','3','4','5','6','7']
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
			if(menuIndex=="7"):
				level="root"
				continue
			elif(menuIndex=="1"):
				matrix=correctWB(matrix,"red")
				continue
			elif(menuIndex=="2"):
				matrix=correctWB(matrix,"green")
				continue
			elif(menuIndex=="3"):
				matrix=correctWB(matrix,"blue")
				continue
			elif(menuIndex=="4"):
				matrix=correctWB(matrix,"red","-")
				continue
			elif(menuIndex=="5"):
				matrix=correctWB(matrix,"green","-")
				continue
			elif(menuIndex=="6"):
				matrix=correctWB(matrix,"blue","-")
				continue
		elif(level=="root7"): # exit
			exit(0)
		elif(level=="root0"): # Switching between warm and cool matrixes with autosave
			updateScreen(matrix)
			saveMatrix(matrix,saveToWhere,False,matrixTemperature) #saving to customCCT.txt file
			matrixArray=readMatrix(default_filename) #parsing the customCCT.txt file
			global previousMatrix
			previousMatrix=matrixArray
			matrix=switchMatrix(previousMatrix,"warm" if matrixTemperature=="cool" else "cool")
			level="root"
			continue
			
		elif(level=="root2"): # Color balance correction menu
			updateScreen(matrix)
			print("="*50)
			menuVariants=['1','2','3','4']
			print("Правка баланса цветов. Выберите цвет:\n1. Красный\n2. Зеленый\n3. Синий\n4. Назад")
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
			if(menuIndex=="1"):
				level="root21"
				continue
			elif(menuIndex=="2"):
				level="root22"
				continue
			elif(menuIndex=="3"):
				level="root23"
				continue
			elif(menuIndex=="4"):
				level="root"
				continue
				
		elif(level=="root21"): # Color balance correction => Red
			updateScreen(matrix)
			print("="*50)
			menuVariants=['1','2','3','4','5']
			print("Правка баланса оттенков красного. Выберите вариант:\n1. Зеленый в красном +\n2. Синий в красном +\n3. Зеленый в красном -\n4. Синий в красном -\n5. Назад")
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
				if(menuIndex=="5"):
					level="root2"
				elif(menuIndex=='1'):
					matrix=correctColor(matrix,"green","red","+")
				elif(menuIndex=='2'):
					matrix=correctColor(matrix,"blue","red","+")
				elif(menuIndex=='3'):
					matrix=correctColor(matrix,"green","red","-")
				elif(menuIndex=='4'):
					matrix=correctColor(matrix,"blue","red","-")
			continue
			
		elif(level=="root22"): # Color balance correction => Green
			updateScreen(matrix)
			print("="*50)
			menuVariants=['1','2','3','4','5']
			print("Правка баланса оттенков зеленого. Выберите вариант:\n1. Красный в зеленом +\n2. Синий в зеленом +\n3. Красный в зеленом -\n4. Синий в зеленом -\n5. Назад")
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
				if(menuIndex=="5"):
					level="root2"
				elif(menuIndex=='1'):
					matrix=correctColor(matrix,"red","green","+")
				elif(menuIndex=='2'):
					matrix=correctColor(matrix,"blue","green","+")
				elif(menuIndex=='3'):
					matrix=correctColor(matrix,"red","green","-")
				elif(menuIndex=='4'):
					matrix=correctColor(matrix,"blue","green","-")
			continue
				
		elif(level=="root23"): # Color balance correction => Blue
			updateScreen(matrix)
			print("="*50)
			menuVariants=['1','2','3','4','5']
			print("Правка баланса оттенков синего. Выберите вариант:\n1. Красный в синем +\n2. Зеленый в синем +\n3. Красный в синем -\n4. Зеленый в синем -\n5. Назад")
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
				if(menuIndex=="5"):
					level="root2"
				elif(menuIndex=='1'):
					matrix=correctColor(matrix,"red","blue","+")
				elif(menuIndex=='2'):
					matrix=correctColor(matrix,"green","blue","+")
				elif(menuIndex=='3'):
					matrix=correctColor(matrix,"red","blue","-")
				elif(menuIndex=='4'):
					matrix=correctColor(matrix,"green","blue","-")
			continue
				
		elif(level=="root3"): # Color saturation menu
			updateScreen(matrix)
			print("="*50)
			menuVariants=['1','2','3','4','5','6','7','8','9']
			print("Изменить насыщенность цветов:\n1. Все цвета +\n2. Все цвета -\n3. Красный +\n4.Красный-\n5.Зеленый +\n6.Зеленый -\n7.Синий +\n8. Синий -\n9. Назад")
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
				if(menuIndex=="9"):
					level="root"
				elif(menuIndex=='1'):
					matrix=saturate(matrix,"all","+")
				elif(menuIndex=='2'):
					matrix=saturate(matrix,"all","-")
				elif(menuIndex=='3'):
					matrix=saturate(matrix,"red","+")
				elif(menuIndex=='4'):
					matrix=saturate(matrix,"red","-")
				elif(menuIndex=='5'):
					matrix=saturate(matrix,"green","+")
				elif(menuIndex=='6'):
					matrix=saturate(matrix,"green","-")
				elif(menuIndex=='7'):
					matrix=saturate(matrix,"blue","+")
				elif(menuIndex=='8'):
					matrix=saturate(matrix,"blue","-")
			continue
				
		elif(level=="root4"): # Normalize vectors
			matrix=normalizeByVectors(matrix)
			level="root"
			continue
			
		elif(level=="root5"): # Revert from backup
			revertBackup(saveToWhere)
			main()
			exit()
			
		elif(level=="root6"): # Save the matrix locally
			saveMatrix(matrix,saveToWhere,oneMatrix,matrixTemperature)
			level="root"
			continue
		elif(level=="root8"): # Get customCCT.txt from adb device
			os.system("adb\\adb.exe pull /sdcard/DCIM/PhotonCamera/customCCT.txt")
			main()
			exit()
		elif(level=="root9"): # Push customCCT.txt to the adb device
			saveMatrix(matrix,saveToWhere,oneMatrix,matrixTemperature)
			os.system("adb\\adb.exe push customCCT.txt /sdcard/DCIM/PhotonCamera/customCCT.txt")
			main()
			exit()
"""		elif(level=="root2"): # menu template
			updateScreen(matrix)
			menuVariants=['1','2','3']
			print()
			menuIndex=""
			while(menuIndex not in menuVariants):
				menuIndex=input('> ')
"""
			
def updateScreen(curr_matrix):
	os.system('cls' if os.name=='nt' else 'clear') #clearing the terminal
	drawMatrix(curr_matrix) #drawing the matrix table

def createBackup(filename):
	dateTimeNow=str(datetime.now())
	backupFileDate=dateTimeNow.replace(' ','').replace('-','').replace(':','')[:13]
	backupFileName=default_filename.replace('.txt','.bak.'+backupFileDate+'.txt')
	if(not exists(backupDir)):
		os.mkdir(backupDir)
	backup=open(backupDir+backupFileName,"w")
	backup.write(open(filename).read())
	backup.close()
	print("Backup file saved to "+backupDir+backupFileName)
	
def revertBackup(filename): #reverts to {filename} from last backup in backups dir
	backupFiles=[]
	for file in glob.glob(backupDir+"*.txt"):
		backupFiles.append(file)
	if(len(backupFiles)<1):
		print("No backup files!")
		return
	backupFiles.sort()
	backup=open(filename,"w")
	backup.write(open(backupFiles[-1]).read())
	backup.close()
	print("Backup restored!")
	
def saveMatrix(matrix,saveToWhere,oneMatrix=True,type="warm"):
	if(oneMatrix):
	
		fp=open(saveToWhere,'w')
		fp.write("MATRIX\n\n"+str(round(matrix['Rr'],4))+","+str(round(matrix['Rg'],4))+","+str(round(matrix['Rb'],4))+",\n"+str(round(matrix['Gr'],4))+","+str(round(matrix['Gg'],4))+","+str(round(matrix['Gb'],4))+",\n"+str(round(matrix['Br'],4))+","+str(round(matrix['Bg'],4))+","+str(round(matrix['Bb'],4)))
		fp.close()
	else:  #if two matrixes
		if(type=="warm"):
			content="MATRIXES\n\n"+matrix1_whitepoint+"\n\n"+str(round(matrix['Rr'],4))+","+str(round(matrix['Rg'],4))+","+str(round(matrix['Rb'],4))+",\n"+str(round(matrix['Gr'],4))+","+str(round(matrix['Gg'],4))+","+str(round(matrix['Gb'],4))+",\n"+str(round(matrix['Br'],4))+","+str(round(matrix['Bg'],4))+","+str(round(matrix['Bb'],4))+"\n\n"+matrix2_whitepoint+"\n\n"+coolRows[0][0]+","+coolRows[0][1]+","+coolRows[0][2]+",\n"+coolRows[1][0]+","+coolRows[1][1]+","+coolRows[1][2]+",\n"+coolRows[2][0]+","+coolRows[2][1]+","+coolRows[2][2]
			fp=open(saveToWhere,'w')
			fp.write(content)
			fp.close()
		else: #if cool matrix edited
			content="MATRIXES\n\n"+matrix1_whitepoint+"\n\n"+warmRows[0][0]+","+warmRows[0][1]+","+warmRows[0][2]+",\n"+warmRows[1][0]+","+warmRows[1][1]+","+warmRows[1][2]+",\n"+warmRows[2][0]+","+warmRows[2][1]+","+warmRows[2][2]+"\n\n"+matrix2_whitepoint+"\n\n"+str(round(matrix['Rr'],4))+","+str(round(matrix['Rg'],4))+","+str(round(matrix['Rb'],4))+",\n"+str(round(matrix['Gr'],4))+","+str(round(matrix['Gg'],4))+","+str(round(matrix['Gb'],4))+",\n"+str(round(matrix['Br'],4))+","+str(round(matrix['Bg'],4))+","+str(round(matrix['Bb'],4))
			fp=open(saveToWhere,'w')
			fp.write(content)
			fp.close()
	

	
def normalizeByVectors(matrix):
	wholeSum=getMatrixSum(matrix)
	newVectorSum=wholeSum/3
	vectorRedSum=getMatrixSum(matrix,"vector_red")
	vectorGreenSum=getMatrixSum(matrix,"vector_green")
	vectorBlueSum=getMatrixSum(matrix,"vector_blue")
	newMatrix={
		'Rr' : ((newVectorSum-vectorRedSum)/3)+matrix['Rr'],
		'Rg' : ((newVectorSum-vectorGreenSum)/3)+matrix['Rg'],
		'Rb' : ((newVectorSum-vectorBlueSum)/3)+matrix['Rb'],
		'Gr' : ((newVectorSum-vectorRedSum)/3)+matrix['Gr'],
		'Gg' : ((newVectorSum-vectorGreenSum)/3)+matrix['Gg'],
		'Gb' : ((newVectorSum-vectorBlueSum)/3)+matrix['Gb'],
		'Br' : ((newVectorSum-vectorRedSum)/3)+matrix['Br'],
		'Bg' : ((newVectorSum-vectorGreenSum)/3)+matrix['Bg'],
		'Bb' : ((newVectorSum-vectorBlueSum)/3)+matrix['Bb']
		}
	return newMatrix

def saturate(matrix,color="all", mod="+"):
	amount=getMatrixSum(matrix,"whole")/30
	if(mod=="-"):
		amount=-amount
	if(color=="all"):
		matrix['Rr']=matrix['Rr']+amount
		matrix['Gg']=matrix['Gg']+amount
		matrix['Bb']=matrix['Bb']+amount
		matrix['Rg']=matrix['Rg']-amount/2
		matrix['Rb']=matrix['Rb']-amount/2
		matrix['Gr']=matrix['Gr']-amount/2
		matrix['Gb']=matrix['Gb']-amount/2
		matrix['Br']=matrix['Br']-amount/2
		matrix['Bg']=matrix['Bg']-amount/2
	elif(color=="red"):
		matrix['Rr']=matrix['Rr']+amount
		matrix['Gr']=matrix['Gr']-amount/2
		matrix['Br']=matrix['Br']-amount/2
		matrix['Rg']=matrix['Rg']-amount/2
		matrix['Rb']=matrix['Rb']-amount/2
		matrix['Gg']=matrix['Gg']+amount/4
		matrix['Gb']=matrix['Gb']+amount/4
		matrix['Bg']=matrix['Bg']+amount/4
		matrix['Bb']=matrix['Bb']+amount/4
	elif(color=="green"):
		matrix['Gg']=matrix['Gg']+amount
		matrix['Rg']=matrix['Rg']-amount/2
		matrix['Bg']=matrix['Bg']-amount/2
		matrix['Gr']=matrix['Gr']-amount/2
		matrix['Gb']=matrix['Gb']-amount/2
		matrix['Rr']=matrix['Rr']+amount/4
		matrix['Rb']=matrix['Rb']+amount/4
		matrix['Br']=matrix['Br']+amount/4
		matrix['Bb']=matrix['Bb']+amount/4
	elif(color=="blue"):
		matrix['Bb']=matrix['Bb']+amount
		matrix['Rb']=matrix['Rb']-amount/2
		matrix['Gb']=matrix['Gb']-amount/2
		matrix['Br']=matrix['Br']-amount/2
		matrix['Bg']=matrix['Bg']-amount/2
		matrix['Rr']=matrix['Rr']+amount/4
		matrix['Rg']=matrix['Rg']+amount/4
		matrix['Gr']=matrix['Gr']+amount/4
		matrix['Gg']=matrix['Gg']+amount/4
	return matrix
	
def correctWB(matrix,color,mod="+"):
	amount=getMatrixSum(matrix,color)/100
	if(mod=="-"):
		amount=-amount
	if(color=="red"):
		matrix['Rr'] = matrix['Rr']+amount
		matrix['Rg'] = matrix['Rg']+amount
		matrix['Rb'] = matrix['Rb']+amount
	elif(color=="green"):
		matrix['Gr'] = matrix['Gr']+amount
		matrix['Gg'] = matrix['Gg']+amount
		matrix['Gb'] = matrix['Gb']+amount
	elif(color=="blue"):
		matrix['Br'] = matrix['Br']+amount
		matrix['Bg'] = matrix['Bg']+amount
		matrix['Bb'] = matrix['Bb']+amount
	return matrix

def correctColor(matrix, color, inColor, mod="+"):
	amount=getMatrixSum(matrix,color)/10
	if(mod=="-"):
		amount=-amount
	matrixIndex=color[0].upper()+inColor[0]
	template="rgb"
	otherColors=template.replace(inColor[0],'')
	otherColorIndex1=color[0].upper()+otherColors[0]
	otherColorIndex2=color[0].upper()+otherColors[1]
	matrix[matrixIndex]=matrix[matrixIndex]+amount
	matrix[otherColorIndex1]=matrix[otherColorIndex1]-amount/2
	matrix[otherColorIndex2]=matrix[otherColorIndex2]-amount/2
	return normalizeByVectors(matrix)
	
	
def getMatrixSum(matrix,type="whole"):
	if (type=="whole"):
		sum=float(matrix['Rr'])+float(matrix['Rg'])+float(matrix['Rb'])+float(matrix['Gr'])+float(matrix['Gg'])+float(matrix['Gb'])+float(matrix['Br'])+float(matrix['Bg'])+float(matrix['Bb'])
	elif(type=="red"):
		sum=float(matrix['Rr'])+float(matrix['Rg'])+float(matrix['Rb'])
	elif(type=="green"):
		sum=float(matrix['Gr'])+float(matrix['Gg'])+float(matrix['Gb'])
	elif(type=="blue"):
		sum=float(matrix['Br'])+float(matrix['Bg'])+float(matrix['Bb'])
	elif(type=="vector_red"):
		sum=float(matrix['Rr'])+float(matrix['Gr'])+float(matrix['Br'])
	elif(type=="vector_green"):
		sum=float(matrix['Rg'])+float(matrix['Gg'])+float(matrix['Bg'])
	elif(type=="vector_blue"):
		sum=float(matrix['Rb'])+float(matrix['Gb'])+float(matrix['Bb'])
	return sum

def drawMatrix(matrix):
	print(str(round(matrix['Rr'],4))+", "+str(round(matrix['Rg'],4))+", "+str(round(matrix['Rb'],4))+",")
	if(twoMatrixes):
		addon=("\b    (теплая)" if matrixTemperature=="warm" else "    (холодная)")
	else:
		addon=""
	print(str(round(matrix['Gr'],4))+", "+str(round(matrix['Gg'],4))+", "+str(round(matrix['Gb'],4))+","+addon)
	print(str(round(matrix['Br'],4))+", "+str(round(matrix['Bg'],4))+", "+str(round(matrix['Bb'],4)))
	
def returnMatrixFromRows(rRow,gRow,bRow):
			matrix={
			"Rr" : float(rRow[0]),
			"Rg" : float(rRow[1]),
			"Rb" : float(rRow[2]),
			"Gr" : float(gRow[0]),
			"Gg" : float(gRow[1]),
			"Gb" : float(gRow[2]),
			"Br" : float(bRow[0]),
			"Bg" : float(bRow[1]),
			"Bb" : float(bRow[2])
			}
			return matrix


def readMatrix(filename):
	matrix=[]
	global oneMatrix
	oneMatrix=False
	global twoMatrixes
	twoMatrixes=False
	if(exists(filename)):
		fp=open(filename)
		#file_contents=fp.read().split("\n")
		line=fp.readline().strip()
		if(line=="MATRIX"):
			
			oneMatrix=True
		elif(line=="MATRIXES"):
			
			twoMatrixes=True
		else:
			print(wrongFormat)
			exit()
		line=fp.readline().strip()
		if(oneMatrix):
			line=fp.readline().strip() #skipping the empty line
			rRow=line.strip().split(",")
			gRow=fp.readline().strip().split(",")
			bRow=fp.readline().strip().split(",")
			m=returnMatrixFromRows(rRow,gRow,bRow)
			matrix.append(m)
			return matrix
		elif(twoMatrixes):
			global matrix1_whitepoint
			matrix1_whitepoint=fp.readline().strip()
			line=fp.readline().strip()
			line=fp.readline().strip() #skipping empty lines and white point line
			rRow=line.strip().split(",")
			gRow=fp.readline().strip().split(",")
			bRow=fp.readline().strip().split(",")
			global warmRows
			warmRows=[rRow,gRow,bRow]
			m1=returnMatrixFromRows(rRow,gRow,bRow)
			matrix.append(m1)
			line=fp.readline().strip()
			global matrix2_whitepoint
			matrix2_whitepoint=fp.readline().strip()
			line=fp.readline().strip()
			line=fp.readline().strip()
			rRow=line.strip().split(",")
			gRow=fp.readline().strip().split(",")
			bRow=fp.readline().strip().split(",")
			global coolRows
			coolRows=[rRow,gRow,bRow]
			global matrix2
			m2=returnMatrixFromRows(rRow,gRow,bRow)
			matrix.append(m2)
			return matrix
		fp.close()
	else:
	   print("Cannot find the matrix file! Exitting...")
	   exit(0);
	   
main()