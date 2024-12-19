import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from matplotlib import pyplot as plt  # plotting
from photutils.aperture import CircularAperture 
from photutils.aperture import aperture_photometry
import re
from scipy import stats

#calibracion en flujo
name_final='.\\data_folder_final_2'
name_calib='.\\data_folder_calib_2' #donde guardaremos las imagnes calibradas en flujo y magnitud
final=[]
final=os.listdir(name_final) #imagenes restadas de bias flat dark y cielo

if not os.path.exists(name_calib):  #creamos carpeta donde guardaremos las imagenes clibradas
	os.mkdir(os.path.join('.',name_calib))

filtros=['r','i','g'] #'R','U','I','V','B'
#flujo para las estrellas ejemplo, podemos mirar las estrellas en simbad strasburg
magsG=[15.37 , 16.95 , 17.82 , 15.59 ,'g'] #magnitud 3 estrellas ejemplo
magsR=[14.98 , 16.52 , 17.22 , 15.12 ,'r']
magsI=[14.85 , 16.38 , 17.02 , 14.97 ,'i']

mags=[magsG,magsR,magsI]
map_mags={mags[i][-1] : mags[i] for i in range(0,len(mags)) } 

#zero de filtros (sistema de vega) (erg/cm2/s/A)*FWHM(A) asi nos queda en unidades de flujo
zeroG=[5.45476e-9 * 1175.63,'g'] 
zeroR=[2.49767e-9 * 1130.56,'r']
zeroI=[1.38589e-9 * 1253.30,'i']  
zero_fileters=[zeroG,zeroR,zeroI] 
map_zeros={zero_fileters[i][-1] : zero_fileters[i] for i in range(0,len(zero_fileters)) } 

NCalib=int(input('Cuantas estrellas de calibracion has tomado:   '))

map_final={re.findall('.\.', final[i])[0][0] : final[i] for i in range(0,len(final)) } 

r=10#int(input('Radio en pixeles para apertura:   '))

list_sum_adu=[]
list_flux=[]

#para cortar las estrellas
for element in filtros:
	print('Filtro ',element)
	for i in range(NCalib):
		print('Estrella',str(i+1))
		#tenemos que plotear para cada banda porque la posicion de la estrella puede cambiar
		matrix=(fits.open(os.path.join(name_final,map_final[element])))[0].data
		plt.imshow(matrix, origin='lower', vmin=np.nanpercentile(matrix, 5), vmax=np.nanpercentile(matrix, 95))
		plt.title('Final Image '+ element +' band')
		plt.colorbar()
		plt.show(block = False)
		
		#clicamos en la estrella que queremos coger para hacer zoom
		points=plt.ginput(1)
		plt.close()
		
		#corta haciendo zoom donde hemos clickado
		matrix=fits.open(os.path.join(name_final,map_final[element]))[0].data
		#hacemos 0 pixeles erroneos
		matrix[np.isnan(matrix)]=0
		matrix[np.isinf(matrix)]=0
		matrix1=matrix[int(points[0][1])-50:int(points[0][1])+50,int(points[0][0])-50:int(points[0][0])+50]
		
		#mostramos el corte
		plt.imshow(matrix1, origin='lower', vmin=np.nanpercentile(matrix1, 5), vmax=np.nanpercentile(matrix1, 95))
		plt.title('Final Image '+ element +' band')
		plt.colorbar()
		plt.show(block = False)
		
		#clicamos el centro exacto de la estrella
		points=plt.ginput(1)
		
		#creamos apertura circular
		x=points[0][0]
		y=points[0][1]
		mask = CircularAperture((x, y), r)
		
		#introducimos las mascaras y las matrices cortadas en una lista
		sum = aperture_photometry(matrix1,mask)
		print(sum) #printea una tabla de pixeles y cuentas/s
		#print(sum[0][3]) #printea solo el valor de cuentas/s
		list_sum_adu.append(sum[0][3]) #flujo en adu/s para las estrellas de calib en la misma banda
		
		flux=10**(-0.4*(map_mags[element][i]))*map_zeros[element][0]
		list_flux.append(flux)	
		
		plt.close()
		
	list_sum_adu=np.array(list_sum_adu)
	list_flux=np.array(list_flux)
	calib_flux=list_flux/list_sum_adu #array flujo/(adu/s)
	print('Constante de calibración:', calib_flux)
	calib_flux_median=np.nanmedian(calib_flux) #mediana de los valores obtenidos
	
	Image_flux_calib=fits.open(os.path.join(name_final,map_final[element]))[0].data*calib_flux_median #imagen calibrada en flujo
	
	#print(Image_flux_calib)
	Image_flux_calib[np.isnan(Image_flux_calib)]=10**-19
	Image_flux_calib[np.isinf(Image_flux_calib)]=10**-19
	Image_flux_calib[Image_flux_calib==0]=10**-19
	
	plt.imshow(Image_flux_calib, origin='lower', vmin=np.nanpercentile(Image_flux_calib, 5), vmax=np.nanpercentile(Image_flux_calib, 95))
	plt.title('Final Image Flux Calib in '+ element +' band (erg/s)')
	plt.colorbar()
	plt.show()
	
	output_name=os.path.join('.',name_calib,'FluxCalib_' + element + '.fits') #guardamos imagenes
	R=fits.PrimaryHDU(Image_flux_calib)
	R.writeto(output_name, overwrite= True)
	print('Imagen '+'FluxCalib_' + element + '.fits en '+ name_calib)

	Image_mags=-2.5*np.log10(Image_flux_calib/map_zeros[element][0]) #imagen calibrada en magnitudes
	
	Image_mags[np.isnan(Image_mags)]=28
	Image_mags[np.isinf(Image_mags)]=28
	Image_mags[Image_mags==0]=28
	
	#print(Image_mags)
	
	plt.imshow(Image_mags, origin='lower', vmin=np.nanpercentile(Image_mags, 5), vmax=np.nanpercentile(Image_mags, 95))
	plt.title('Final Image Mag in '+ element +' band')
	plt.colorbar()
	plt.show()
	
	output_name=os.path.join('.',name_calib,'FluxMag_' + element + '.fits') #guardamos imagenes
	R=fits.PrimaryHDU(Image_mags)
	R.writeto(output_name, overwrite= True)
	print('Imagen '+'MagCalib_' + element + '.fits en '+ name_calib)
	
	list_sum_adu=[]
	list_flux=[]
	

