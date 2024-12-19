import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from matplotlib import pyplot as plt  # plotting
from photutils.aperture import CircularAperture 
from photutils.aperture import EllipticalAperture
from photutils.aperture import aperture_photometry
from scipy.optimize import curve_fit
import re

def sersic_profile(r,I_e,k,n,r_e):
	return I_e * np.exp(-k*((r/r_e)**(1/n)-1))
	

name_calib='.\\data_folder_calib_2'
final=[]
final=os.listdir(name_calib) #imagenes restadas de bias flat dark, cielo y calibradas

list_mag=[]
list_flux=[]
for i in final:
	if i.find('Mag') != -1:
		list_mag.append(i)
	else:
		list_flux.append(i)

map_Flux={re.findall('.\.', list_flux[i])[0][0] : list_flux[i] for i in range(0,len(list_flux)) } 
map_Mag={re.findall('.\.', list_mag[i])[0][0] : list_mag[i] for i in range(0,len(list_mag)) } 

#zero de filtros (sistema de vega) (erg/cm2/s/A)*FWHM(A) asi nos queda en unidades de flujo
zeroG=[5.45476e-9 * 1175.63,'g'] 
zeroR=[2.49767e-9 * 1130.56,'r']
zeroI=[1.38589e-9 * 1253.30,'i']   
zero_fileters=[zeroG,zeroR,zeroI] 
map_zeros={zero_fileters[i][-1] : zero_fileters[i] for i in range(0,len(zero_fileters)) } 

filtros=['g','r','i']

r=300 #radio de la apertura
#coordenadas del centro de la galaxia
x_center=870
y_center=830
a_radius = 480  # Semi-eje mayor
epsilon=0.8
b_radius=np.sqrt(a_radius**2-epsilon**2*a_radius**2)
print('Exccentricity Orbit '+ str(epsilon))
angulo=-18
theta = angulo*np.pi / 180  # Ángulo de rotación (en radianes)

d=19000000 #luminosity distance in light years
arc=0.53 #arc seg for each pixel in CAFOS
c=0.000277778*np.pi/180 #constant to arc seg to radianes

for band in filtros:
	Image=(fits.open(os.path.join(name_calib,map_Flux[band])))[0].data
	mask = EllipticalAperture((x_center, y_center), a_radius, b_radius, theta) #creamos la mascara
	sum = aperture_photometry(Image,mask) #suma en los píxeles indicados
	

	y=np.array(Image[x_center,y_center:])
	x=np.linspace(0, y.shape[0], y.shape[0]) #distance to the centre in pixels
	x=x*arc*c*d #distance to the centre in ly

	params, covariance = curve_fit(sersic_profile, x, y,[1e-15,0.3,2,1])
	print(params)
	I_e,k,n,r_e=params

	plt.plot(x,y, label='Data')
	plt.plot(x,sersic_profile(x,I_e,k,n,r_e), label='Sersic Fit')
	plt.title('Flux Profile in function of Distance')
	plt.ylabel('Flux (erg s^-1 cm^-2 A^-1)')
	plt.xlabel('Distance (ly)')
	plt.legend()
	plt.show()

	Mag=-2.5*np.log10(y/map_zeros[band][0])
	plt.axhline(y=25, color='red', linestyle='--')
	plt.plot(x,Mag)
	plt.title('Magnitude Profile in function of Distance')
	plt.ylabel('Magnitude (Mag)')
	plt.xlabel('Distance (pixels)')
	#plt.xlim(0,500)
	plt.show()

	plt.imshow(Image, origin='lower', vmin=np.nanpercentile(Image, 40), vmax=np.nanpercentile(Image, 99))
	plt.title('Image Flux Calib in '+ band +' band aperture mask')
	plt.colorbar()
	mask.plot(color='r',lw=1.5)
	plt.show()

	#print(sum) #printea una tabla de pixeles y cuentas/s
	MagInte=-2.5*np.log10(sum[0][3]/map_zeros[band][0])
	print('La magnitud integrada en la banda ' + str(band)+ ' es ' + str(MagInte))



