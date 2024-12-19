import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from matplotlib import pyplot as plt  # plotting

#importante que la carpeta del observatorio este en el mismo directrio que este scrip
nombre =input('Escribe el nombre de la Carpeta sacada de la CCD(nombre/)   ')#'TFG_EXP_Practica' 
path = nombre +'/' 

arr = os.listdir(nombre) #array creado con la lista de los archivos de la carpeta
	
	#hdu.info() #nos da toda la info del archivo .fit
	#hdu[0].header #header, descripcion del archivo 
	#hdu[0].header['OBJECT'] informacion del archivo escogiendo el apartado OBJECT
	#hdu[0].data muestra matrices de fichero, al final es con lo que trabajamos
	

for i in np.arange(len(arr)): #loop en la longitud del array
	hdu = fits.open(path+arr[i]+'') #abrimos los archivos
	print(i,hdu[0].header['OBJECT']) 
	hdu.close()
	
Nbias = int(input('¿Cuantas imagenes de Calibracion de BIAS has tomado?   ')) #pedimos el numero de imagenes en numero entero
bias=[] #inicializamos el array donde vamos a guardar las imagenes del bias

#bias
pathbias='raw_data_folder_bias' #carpeta donde guardaremos todo lo relacionado con el BIAS
if not os.path.exists(pathbias):  #si no hay carpeta creada, la crea
	os.mkdir(os.path.join('.',pathbias))

y = 0
texp = 1
	
while y != 'si': #simplemente preguntará si los archivos seleccionados son los que queremos, por si nos hubieramos equivocado	
	for i in range(Nbias):
		while texp != 0:
			x = int(input('Dime los BIAS de la lista mostrada que vayas a utilizar (numero del array):   '))
			hdub=fits.open(path+arr[x]) #los hdu del bias
			print(i,hdub[0].header['OBJECT']) #mostramos el fichero escogido
			texp=hdub[0].header['EXPTIME'] #obtenemos el tiempo de exposicion de la imagen del fichero escogido
			if  texp != 0: #comprueba que el tiempo de exposicion sea 0, la manera en la que se toman los bias
				print('t_exp = '+str(texp)+'  no es una imagen de BIAS')	
		bias.append(arr[x]) #append introduce el elemento al final del array
		texp=1
		
	y = input('¿Guardamos esos ficheros? (si/no)   ') #preguntamos si estamos conformes con lo escogido

	if y == 'si': #si los archivos escogidos son los correctos comenzamos con el proceso de guardado
		for i in range(len(bias)):
			output_name = os.path.join('.',pathbias,'bias_' + str(i) + '.fits') #donde lo queremos guardar y con que nombre
			hdu1=fits.open(path+bias[i]) #obtenemos los hdu escogidos
			hdu=fits.PrimaryHDU(hdu1[0].data) #sacamos las matrices como ficheros tipo fits
			hdu.writeto(output_name, overwrite= True) #guardamos
		print('BIAS guardados en ' + pathbias) 
		
	if y !='si': #si no queremos guardarlo inicializamos el proceso
		texp=1
		bias=[]

#comenzamos proceso para obtener master bias
bias=[]
arr1 = os.listdir(pathbias) #cremos array con todos los bias escogidos
	
for i in range(len(arr1)):
	hdu=fits.open(pathbias+'/'+arr1[i])
	bias.append(hdu[0].data) #guardamos solo las matrices 
	
bias_map = np.nanmedian(bias, axis=0) #devuelve la mediana del array 

if Nbias == 1:
	print("WARNING: only one bias file was found.") #si solo hay un fichero no podremos operar con la mediana o media, solo mostraremos un fit
else:
	noise_map = np.nanvar(bias, axis=0) #devuelve la varianza del array (medida de la dispersión) 
	# Test whether the median bias map is uniform
	map_median = np.nanmedian(bias_map)  #genera la mediana de la imagen entera (es un valor)
	map_variance = np.nanvar(bias_map)  # map_variance = signal_variance + noise_variance, genera la varianza del mapa (un valor)
	noise_variance = np.nanmedian(noise_map)  # estimator of the typical noise variance (un valor)
	signal_variance = map_variance - noise_variance
	if signal_variance <= 0.:
		probability_uniform = 1.
	else:
		probability_uniform = np.exp(-signal_variance/noise_variance)
	uniform = map_median*np.ones_like(bias_map) #np.ones_like devuelve un array de 1s de la misma forma y tipo que el input)
	#print(f'median bias={map_median}, probability_uniform={probability_uniform}, (signal_variance={signal_variance:.2f}, noise_variance={noise_variance:.2f}')
        
bias_map = probability_uniform*uniform + (1-probability_uniform)  # weighted average
		
#plot del masterbias
plt.imshow(bias_map, origin='lower', vmin=np.nanpercentile(bias_map, 5), vmax=np.nanpercentile(bias_map, 95), cmap='inferno') #mostramos el maximo y minimo en porcentaje
plt.title('Master bias')
plt.colorbar()
plt.show()

hdu.close()
hdu = fits.PrimaryHDU(bias_map.astype(np.float32)) #lo guardamos como un fichero .fit
output_filename = os.path.join('.',pathbias, 'master_bias.fits') 
hdu.writeto(output_filename, overwrite=True) #guardamos el fichero
print("Master bias saved to", output_filename)


#flats
flats=[] #array donde vamos a guardar los flats
Nflats=[]
Nfiltro = int(input('¿Cuantos FILTROS diferentes has tomado para FLAT?   '))
filtros=[]

nameflats='raw_data_folder_flats' #donde guardaremos todo los relacionado con las imagenes de calibracion flats
pathflats=nameflats +'/'

if not os.path.exists(nameflats):  #carpeta para los flats
	os.mkdir(os.path.join('.',nameflats))
	
for i in range(Nfiltro): #ordenamos todos los .fits en carpetas con sus filtros correspondientes
	filtro = input('Indica los filtros utilizados (B,V,I...):   ')
	Nflat = int(input('¿Cuantas imagenes de Calibracion de FLAT has tomado para el filtro '+filtro+'?   '))
	Nflats.append(Nflat)
	filtros.append(filtro)  #array de los filtros usados como str
	if not os.path.exists(pathflats + filtro):
		os.mkdir(os.path.join(nameflats,filtro))

y = 0
for i in range(len(filtros)):	#para cada filtro
		while y != 'si':
			for r in range(Nflats[i]):
				x = int(input('Dime los FLATS del filtro '+ filtros[i] + ' de la lista mostrada que vayas a utilizar (numero del array):   '))
				flats.append(arr[x]) #append introduce el elemento al final del array
				hdub=fits.open(path+flats[r]) #los hdu del flats
				print(i,hdub[0].header['OBJECT']) #mostramos el fichero escogido
	
			y = input('¿Guardamos esos ficheros? (si/no)   ') #preguntamos si estamos conformes con lo escogido
		
			if y == 'si': #si estamos conformes con la elección lo guardamos en la carpeta
				for t in range(len(flats)):
					output_name = os.path.join('.',pathflats + filtros[i],'flats_' + filtros[i] + '_' + str(t) + '.fits') #donde lo queremos guardar y con que nombre
					hdu1=fits.open(path+flats[t]) #obtenemos los hdu escogidos
					hdu=fits.PrimaryHDU(hdu1[0].data) #sacamos las matrices como ficheros tipo fits
					hdu.writeto(output_name, overwrite= True) #guardamos
				print('FLATS guardados en ' + nameflats + ' ' + filtros[i]) 		
		y=0
		flats=[]

#comenzamos proceso para obtener master flat
#recogemos master bias y master dark
filename = os.path.join('.',pathbias, 'master_bias.fits')
if os.path.isfile(filename): #para ver si el master_bias se ha hecho 
	print("Opening", filename)
	hdu = fits.open(filename)
	bias = hdu[0].data	
else:
    print(filename, 'not found: set master bias=0') #if it does not find master bias, sets it as 0
    bias = 0.


pathdark='pathdark'	#no tenemos master dark pero lo dejamos indicado para mayor generalidad
filename = os.path.join('.',pathdark,'master_dark.fits') 
if os.path.isfile(filename):
	print("Opening", filename)
	hdu = fits.open(filename)
	dark = hdu[0].data
else:
    print(filename, 'not found: set master dark=0') #if it does not find master dark, sets it as 0
    dark = 0.

#collect flat images for each band
flat_exposures = {}
	
for foldername in os.listdir(nameflats):  # Loop over all files in the directory (para todas las diferentes bandas)
	if os.path.isdir(os.path.join(nameflats, foldername)):
		print("Reading", foldername, "band flats:") #lee las diferentes carpetas con los flats de cada banda
		flat_exposures[foldername] = []  # Empty list to store the exposures
				
		for filename in os.listdir(os.path.join(nameflats, foldername)):  # Loop over all files in the directory
			if os.path.splitext(filename)[1] == '.fits':  # FITS file extension
				print(" - Opening", filename)
				hdu = fits.open(os.path.join(nameflats, foldername, filename))  # HDU = Header/Data Unit (standard FITS nomenclature)

				#in the case bias and flat are different shape
				dim_bias=int(bias.shape[0])  #columns number
				dim_flat=int(hdu[0].data.shape[0]) 
				if dim_bias>dim_flat:
					n=(dim_bias-dim_flat)/2
					n=int(np.floor(n))
					bias=bias[n+1:dim_bias-n,n+1:dim_bias-n]

				# Add the data, normalized to their median, to the `flat_exposures` list of that band
				exposure = hdu[0].data - bias #- dark*hdu[0].header['EXPTIME'] 
				flat_exposures[foldername].append(exposure/np.nanmedian(exposure))
				
		n_files = len(flat_exposures[foldername])
		print(" -", n_files, "files read for", foldername, "band")

	else:
		print(foldername+" is not a directory")

	
for band in flat_exposures: #plot all the masters flat
    n_files = len(flat_exposures[band])

    if n_files == 0: #ensure the files are saved correctly
        raise FileNotFoundError("No FITS files were found in "+band+" band")

    else:
        flat_map = np.nanmedian(flat_exposures[band], axis=0)
        bad_flat = np.abs(flat_map-1) > 5*np.nanstd(flat_map)  #
        flat_map[bad_flat] = np.nan
        plt.imshow(flat_map, origin='lower', vmin=np.nanpercentile(flat_map, 5), vmax=np.nanpercentile(flat_map, 95))
        plt.title('Master flat in '+band+' band')
        plt.colorbar()
        plt.show()
		
        output_filename = os.path.join(nameflats, 'master_flat_'+band+'.fits')
        hdu = fits.PrimaryHDU(flat_map)
        hdu.writeto(output_filename, overwrite=True) #saving in the same folder
        print("Master flat saved to", output_filename)
		

