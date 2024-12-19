import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from astropy.visualization import make_lupton_rgb
from matplotlib import pyplot as plt  # plotting
import re

name_color='.\\data_folder_stacked_2' #imagenes reducidas de bias, dark flat y apiladas

final=[] 
final=os.listdir(name_color) #imagenes crudas

map_color={re.findall('.\.', final[i])[0][0] : final[i] for i in range(0,len(final)) } #keys creadas 'R' 'G' 'B'

R=(fits.open(os.path.join(name_color,map_color['R'])))[0].data
G=(fits.open(os.path.join(name_color,map_color['G'])))[0].data
B=(fits.open(os.path.join(name_color,map_color['B'])))[0].data

#parametros
p_R=1.36
p_G=1.95
p_B=3.9
rgb = make_lupton_rgb(2*R*p_R,2*G*p_G,2*B*p_B, stretch=70,Q=5)

#recorte imagen
dim1=1150 #dimension a la que lo queremos recortar
dim=int(rgb.shape[0])
n=(dim-dim1)/2
n=int(np.floor(n))
#centrado del recorte
centre=np.array([rgb.shape[0],rgb.shape[1]])
nx= 65 #desplazo de pixeles en el eje x
ny= 40 #desplazo de pixeles en el eje y
rgb=rgb[n+1+ny:dim-n+ny,n+1+nx:dim-n+nx]

print(rgb.shape)

plt.imshow(rgb,origin='lower',vmin=np.nanpercentile(rgb, 0.1), vmax=np.nanpercentile(rgb, 99.9))
plt.title('P_R = ' + str(p_R) + '  P_G = ' + str(p_G) + '  P_B = ' + str(p_B))
plt.show()


