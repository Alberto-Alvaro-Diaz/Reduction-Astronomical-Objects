import os  # to manipulate files and directories
import numpy as np  # mathematics
from astropy.io import fits  # FITS files
from matplotlib import pyplot as plt  # plotting
from astropy.visualization import make_lupton_rgb
import re

def rotate_matrix(matrix, angle):
    angle_rad = angle 
    
    # Rotation Matrix conter clockwise 
    rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                                 [np.sin(angle_rad), np.cos(angle_rad)]])
    # Matrix shape
    rows, cols = matrix.shape
    
    # Matrix center
    center = np.array([rows // 2, cols // 2])
    
    # New matrix where save the rotated one 
    rotated_matrix = np.zeros_like(matrix)
    
    for i in range(rows):
        for j in range(cols):
            # Calculate the new position for each element after rotation
            rotated_pos = np.dot(rotation_matrix, np.array([i, j]) - center) + center
            
            rotated_i, rotated_j = np.round(rotated_pos).astype(int)
            
            # Verify if the new position is inside the limits
            if 0 <= rotated_i < rows and 0 <= rotated_j < cols:
                # Asignar el valor de la matriz original a la posición rotada
                rotated_matrix[rotated_i, rotated_j] = matrix[i, j]
    
    return rotated_matrix

def rotate_vec(vec, angle):
    centre=1601/2 # particular case of matrix 1601x1601
    angle_rad = angle 
    x1=vec[0]-centre
    y1=vec[1]-centre
    x=(np.cos(angle_rad)*x1 + np.sin(angle_rad)*y1)+centre
    y=(np.cos(angle_rad)*y1 - np.sin(angle_rad)*x1)+centre
    rotated_vec=np.array([x,y])
    return rotated_vec

# To load the files .fits
name_color='.\\data_folder_final_2' # Raw images inputs
name_stacked='.\\data_folder_stacked_2' # Stacked images output

if not os.path.exists(name_stacked):  # Folder flats
	os.mkdir(os.path.join('.',name_stacked))

final=[] 
final=os.listdir(name_color) # Raw images

map_color={re.findall('.\.', final[i])[0][0] : final[i] for i in range(0,len(final)) } # keys created 'i' 'r' 'g'

# Generating the 3 colour bands RGB
R=(fits.open(os.path.join(name_color,map_color['i'])))[0].data
G=(fits.open(os.path.join(name_color,map_color['r'])))[0].data
B=(fits.open(os.path.join(name_color,map_color['g'])))[0].data

# List of matrices that will be used
color=[R,G,B]
band=['R','G','B']
coordinates1=[] #coordenadas estrella 1
coordinates2=[] #coordenadas estrella 2

print('The same star should be cliked for all bands')
for i in range(len(color)):
    x=0 
    while x != 'yes':
        print('Band ' + band[i])
        print('A star in the lower left panel should be selected')
        plt.imshow(color[i],origin='lower',vmin=np.nanpercentile(color[i], 2), vmax=np.nanpercentile(color[i], 98))
        plt.colorbar()
        plt.title('Raw image in ' + band[i] + ' band')
        plt.show(block = False)

        points_1=plt.ginput(1)
        plt.close()
        # A zoom is applied where it was cliked
        cut=color[i][int(points_1[0][1])-50:int(points_1[0][1])+50,int(points_1[0][0])-50:int(points_1[0][0])+50]
        plt.imshow(cut,origin='lower',vmin=np.nanpercentile(cut, 2), vmax=np.nanpercentile(cut, 98))
        plt.colorbar()
        plt.title('Raw image in R band')
        plt.show(block = False)

        points_11=plt.ginput(1)
        plt.close()
        # Calculating the coordinates
        centre=np.array(cut.shape)/2
        coordinates1.append(np.array(points_1[0])+np.array(points_11[0])-centre)
    

        print('A star in the upper right panel should be selected')
        plt.imshow(color[i],origin='lower',vmin=np.nanpercentile(color[i], 2), vmax=np.nanpercentile(color[i], 98))
        plt.colorbar()
        plt.title('Raw image in R band')
        plt.show(block = False)

        points_2=plt.ginput(1)
        plt.close()
        # A zoom is applied
        cut=color[i][int(points_2[0][1])-50:int(points_2[0][1])+50,int(points_2[0][0])-50:int(points_2[0][0])+50]
        plt.imshow(cut,origin='lower',vmin=np.nanpercentile(cut, 2), vmax=np.nanpercentile(cut, 98))
        plt.colorbar()
        plt.title('Raw image in '+ band[i] +' band')
        plt.show(block = False)

        points_22=plt.ginput(1)
        plt.close()
        # Calculating coordinates
        centre=np.array(cut.shape)/2
        coordinates2.append(np.array(points_2[0])+np.array(points_22[0])-centre)

        print('The pixel coordinates of both stars are: ')
        print(coordinates1[i], coordinates2[i])
        x=input('¿Are you agree with the choice? (yes/no)')


# star coordinates (lower left y upper right) 
# band R
n1_r=np.array([coordinates1[0][0],coordinates1[0][1]]) #np.array([595.5 , 418.4])
n2_r=np.array([coordinates2[0][0],coordinates2[0][1]]) #np.array([1354.0 , 1172.6])

# band G
n1_g=np.array([coordinates1[1][0],coordinates1[1][1]]) #np.array([594.6 , 418.4])
n2_g=np.array([coordinates2[1][0],coordinates2[1][1]]) #np.array([1353.2 , 1172.4])

# band B
n1_b=np.array([coordinates1[2][0],coordinates1[2][1]]) #np.array([621.8 , 403.3])
n2_b=np.array([coordinates2[2][0],coordinates2[2][1]]) #np.array([1337.1 , 1198.7])

# vector calculation
vec_r=n2_r-n1_r
vec_g=n2_g-n1_g
vec_b=n2_b-n1_b

# angle calculation (rad)
theta_r=np.arctan(vec_r[1]/vec_r[0]) # reference
theta_g=np.arctan(vec_g[1]/vec_g[0])
theta_b=np.arctan(vec_b[1]/vec_b[0])

theta_1=theta_g-theta_r # rotation angle for matrix g
theta_2=theta_b-theta_r # rotation angle for matrix b

# Lets rotate the matrices, R matrix is chosen as reference
rotated_g = rotate_matrix(G, theta_1)
rotated_b = rotate_matrix(B, theta_2)

# Lets boost the axis x and y
# badn G
n1_g_rotated=rotate_vec(n1_g, theta_1)
n2_g_rotated=rotate_vec(n2_g, theta_1)

# band B
n1_b_rotated=rotate_vec(n1_b, theta_2)
n2_b_rotated=rotate_vec(n2_b, theta_2)


# Calculating boost, R matrix is chosen as reference
shift_g1=n1_g_rotated-n1_r
shift_g2=n2_g_rotated-n2_r
shift_b1=n1_b_rotated-n1_r
shift_b2=n2_b_rotated-n2_r

# Boost mean
shift_g=(shift_g1+shift_g2)/2
shift_b=(shift_b1+shift_b2)/2

# band g
for i in range(rotated_g.shape[0]):
    rotated_g[i, :] = np.roll(rotated_g[i, :], -round(shift_g[0]))
for i in range(rotated_g.shape[1]):
    rotated_g[:, i] = np.roll(rotated_g[:, i], -round(shift_g[1]))

# band b
for i in range(rotated_b.shape[0]):
    rotated_b[i, :] = np.roll(rotated_b[i, :], -round(shift_b[0]))
for i in range(rotated_b.shape[1]):
    rotated_b[:, i] = np.roll(rotated_b[:, i], -round(shift_b[1]))

R=R.astype(np.int64)
rotated_g=rotated_g.astype(np.int64)
rotated_b=rotated_b.astype(np.int64)

R[np.isnan(R)]=0
R[np.isinf(R)]=0
R[R<=0]=0

rotated_g[np.isnan(rotated_g)]=0
rotated_g[np.isinf(rotated_g)]=0
rotated_g[rotated_g<=0]=0

rotated_b[np.isnan(rotated_b)]=0
rotated_b[np.isinf(rotated_b)]=0
rotated_b[rotated_b<=0]=0

matrix=np.array([R,rotated_g, rotated_b])
band=['R','G','B']
for i in range(len(matrix)):
    output_filename = os.path.join(name_stacked, 'stacked_'+ band[i] +'.fits')
    hdu = fits.PrimaryHDU(matrix[i])
    hdu.writeto(output_filename, overwrite=True) # Saved it in the same folder
    print("Stacked image saved to", output_filename)

