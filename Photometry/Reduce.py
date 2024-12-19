import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from matplotlib import pyplot as plt  # plotting
import re

#inicilizamos nombres,paths y arrays que utilizaremos
namebias='raw_data_folder_bias' #path
namemasterbias='master_bias.fits' #name file
nameflat='raw_data_folder_flats'
namescience='raw_data_folder_science' #donde guardaremos las imagenes sin reducir de ciencia
name_reduced='data_folder_reduced' #donde guardaremos las imagenes reducidas
masterbias=[]
master_flats=[]
raw=[]

def reduce(raw, bias, flat, time): #funcion de reduci?n de la imagen cruda restando bias y flat
	#por si el bias tiene diferente dimensión que el flat
	dim_bias=int(bias.shape[0])  #numero columnas
	dim_flat=int(flat.shape[0]) #numero columnas
	if dim_bias>dim_flat:
		n=(dim_bias-dim_flat)/2
		n=int(np.floor(n))
		bias=bias[n+1:dim_bias-n,n+1:dim_bias-n]
	
	print('time', time,'\n')
	print('bias', bias,'\n')
	print('flat', flat,'\n')
	print('raw', raw,'\n')

	R=((raw - bias)/flat)/time #raw, bias, flat: matrices, y tiempo: numero
	return R

nombre ='archivos2' #input('Escribe el nombre de la Carpeta sacada de la CCD(nombre/)   ')
path = nombre +'/'

Nfiltros=int(input('Numero de filtros utilizados:   ')) 
filtros=[]
for i in range(Nfiltros):
	x=input('Filtro utilizado (U,I,R...):   ')
	filtros.append(x) #creamos array para cada filtro

master_bias=fits.open(os.path.join(namebias, namemasterbias))#abrimos el masterbias
bias_data=master_bias[0].data #matriz del master_bias

arr=os.listdir(nameflat)
for filename in arr:
	if '.fits' in filename: 
		master_flats.append(filename) #guardamos en un array todos los masterflats
		
#guardamos las imagenes raw de ciencia	
if not os.path.exists(namescience): 
	os.mkdir(os.path.join('.',namescience)) #creamos carpeta donde vamos a guardar
	
arr=os.listdir(nombre)
for i in np.arange(len(arr)): #loop en la longitud del array
	hdu = fits.open(path+arr[i]+'') #abrimos los archivos
	print(i,hdu[0].header['OBJECT']) 
	hdu.close()

y = 0

Nscience = int(input('¿Cuantas imagenes de Ciencia has tomado?   ')) #pedimos el numero de imagenes en numero entero
Science=[]
	
while y != 'si': #simplemente preguntará si los archivos seleccionados son los que queremos, por si nos hubieramos equivocado	
	for i in range(Nscience):
		x = int(input('Dime los Science de la lista mostrada que vayas a utilizar (numero del array):   '))
		hdub=fits.open(path+arr[x]) #los hdu de science
		print(i,hdub[0].header['OBJECT']) #mostramos el fichero escogido
		Science.append(arr[x]) #append introduce el elemento al final del array
		
	y = input('¿Guardamos esos ficheros? (si/no)   ') #preguntamos si estamos conformes con lo escogido

	if y == 'si': #si los archivos escogidos son los correctos comenzamos con el proceso de guardado
		for i in range(len(Science)):
			hdu1=fits.open(path+Science[i]) #obtenemos los hdu escogidos
			output_name=os.path.join('.',namescience, str(i)+ hdu1[0].header['OBJECT'] +'.fits') #donde lo queremos guardar y con que nombre
			hdu1.writeto(output_name, overwrite= True) #guardamos
		print('Science guardados en ' + namescience) 
		
	if y !='si': #si no queremos guardarlo inicializamos el proceso
		Science=[]

raw=os.listdir(namescience) #array de raw gaurdados en una carpeta a parte

#creamos mapeado con key de cada filtro
map_raw={re.findall('.\.', raw[i])[0][0] : raw[i] for i in range(0,len(raw)) }
map_flats={re.findall('.\.', master_flats[i])[0][0] : master_flats[i] for i in range(0,len(master_flats)) }

if not os.path.exists(name_reduced): 
	os.mkdir(os.path.join('.',name_reduced)) #creamos carpeta donde vamos a guardar

#lista de keys de los flats 
z=list(map_flats.keys())

for element in filtros:
	raw=(fits.open(os.path.join(namescience,map_raw[element])))[0].data
	if element in z:
		flat=(fits.open(os.path.join(nameflat,map_flats[element])))[0].data
	else:
		flat=np.ones_like(raw)
	time=(fits.open(os.path.join(namescience, map_raw[element])))[0].header['EXPTIME']
	R=reduce(raw,bias_data,flat,time) #obtenemos el mapeado en adu/s
	
	plt.imshow(R, origin='lower', vmin=np.nanpercentile(R, 5), vmax=np.nanpercentile(R, 95))
	plt.title('Raw reduced from bias, dark and flat, filter '+ element)
	plt.colorbar()
	plt.show()	
	
	output_name=os.path.join('.',name_reduced,'reduced_' + element + '.fits') #guardamos las imagenes reducidas
	R1=fits.PrimaryHDU(R)
	R1.writeto(output_name, overwrite= True)
		
