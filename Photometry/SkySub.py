import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from matplotlib import pyplot as plt  # plotting
import re
from scipy import stats

#sky subtraction
#inicializamos los nombres y arrays que usaremos
name_reduced='.\\data_folder_reduced_2'
name_final='.\\data_folder_final_2' #donde guardaremos las imagenes restadas de cielo
reduced=[]
reduced=os.listdir(name_reduced)

filtros=['g','r','i']	#filtros que emplearemos ,'U','I','V','B'

map_reduced={re.findall('.\.', reduced[i])[0][0] : reduced[i] for i in range(0,len(reduced)) }

#coordenadas del trozo del cielo que queremos escoger 
x=200 #columna
x1=400
y=350 #fila
y1=550

if not os.path.exists(name_final):  #creamos carpeta donde vamos a guardar las imagenes reducidas de cielo
	os.mkdir(os.path.join('.',name_final))

for element in filtros:
	matrix=fits.open(os.path.join(name_reduced,map_reduced[element]))[0].data
	matrix1=matrix[y:y1,x:x1] #coordenas (filas y columnas) en python van al revés
	matrix1=np.round(matrix1,3)
	mode=stats.mode(matrix1.flatten()) #flatten pasa de matrix a un vector poniendo todas las filas como una unica fila, especie de append
	#mode[0] saca la moda la matriz
	matrix2= matrix-mode[0] #imagen restada de cielo
	print('Le restaremos un valor de cielo de: ', mode[0], 'en adu/s')
	matrix2=np.clip(matrix2,0,None) #coge todos los valores negativos y los hace 0

	plt.imshow(matrix2, origin='lower', vmin=np.nanpercentile(matrix2, 5), vmax=np.nanpercentile(matrix2, 95))
	plt.title('Final Image '+element +' band')
	plt.colorbar()
	plt.show()
	
	output_name=os.path.join('.',name_final,'final_' + element + '.fits') #guardamos imagenes
	R=fits.PrimaryHDU(matrix2)
	R.writeto(output_name, overwrite= True)
	print('Imagen '+'final_' + element + '.fits en '+ name_final)

	#histogramas para ver si hay una buena calibracion restando el flujo y demas
	
	modearray=mode[0]*np.ones_like(matrix1)
	vmin=np.nanpercentile(matrix1, 2)
	vmax=np.nanpercentile(matrix1, 95)
	plt.hist(matrix1.flatten(),bins=np.linspace(vmin,vmax,100)) #nos plotea un histograma de eje x adu/s, eje y numero de pixeles 
	plt.hist(modearray.flatten(),bins=np.linspace(vmin,vmax,100))
	#plt.yscale('log')
	plt.title('Hist in band '+element+' with sky')
	plt.xlabel('adu/s')
	plt.ylabel('pixels')
	plt.show()  
	 
	vmin=np.nanpercentile(matrix2, 5)
	vmax=np.nanpercentile(matrix2, 95)
	plt.hist(matrix2.flatten(),bins=np.linspace(vmin,vmax,100))
	#plt.yscale('log')
	plt.title('Hist in band '+element+' without sky')
	plt.xlabel('adu/s')
	plt.ylabel('pixels')
	plt.show()
	

	


