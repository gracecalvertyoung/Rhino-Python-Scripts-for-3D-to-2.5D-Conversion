# ASSUMPTION: Document units set to METERS
# NOTE: Rhino function Heightfield should be able to display this img.
# NOTE: Assumes rectangular image, but not nessesarily square.
# NOTE: Can't be any holes in mesh (run fill mesh holes).
# NOTE: Points must fit squarly on the grid ?? (1 cm apart)

import rhinoscriptsyntax as rs
import math

# -----  Initalize Variables -----
unit = 0.015 # the distance between two points/pixels

# ----- Function Definitions -----
def RoundPts(unrounded_pts):
    # round x and y to eliminate sorting errors
    # create list ptsXYZ with rounded x, y values, full z value
    # create list ptsXY with only rounded x, y values
    
    ptsXYZ = []
    ptsXY = []
    for pt in unrounded_pts:
        ptXYZ = []
        ptXY = []
        i = 0
        for coord in pt:
            if i < 2:
                coordNew = round(coord, 2)
                ptXYZ.append(coordNew)
                ptXY.append(coordNew)
                i += 1
            else:
                ptXYZ.append(coord)               
        ptsXYZ.append(ptXYZ)
        ptsXY.append(ptXY)

    # sort list of points 
    ptsXYZ.sort()
    ptsXY.sort()

    # return rounded pts
    return [ptsXYZ, ptsXY]

def TakeTopZ(ptsXY, ptsXYZ):
    # get rid of lower point(s) if >1 point with same x, y
    # assumes sorted list (like that returned from rounded_pts)
    
    counter = 0
    ptsXYZ_clean = []
    ptsXY_clean = []
    for [x, y, z] in ptsXYZ:
        i = ptsXY.index([x, y])
        if i == counter:
            ptsXYZ_clean.append([x, y, z])
            ptsXY_clean.append([x, y])
        counter += 1
    
    return [ptsXY_clean, ptsXYZ_clean]

def scaleZ(ptsXYZ):   
    # re-scale Z coordinates so that the lowest Z value equals zero

    # find the minimum Z value
    min_z = min_xy_or_z(ptsXYZ, 'z')
    print("Min Z is: " + str(min_z)) 

    # minimum turns to zero and rest are relitive to that 
    ptsXYZ_scaled = [] 
    for pt in ptsXYZ:
        z_scaled = pt[2] - min_z
        pt_scaled = [pt[0], pt[1], z_scaled]
        ptsXYZ_scaled.append(pt_scaled) 

    return ptsXYZ_scaled 

def max_x_or_y(ptsList, x_or_y):
    # find the maximum of set of points
    
    if x_or_y == "x":
        x_or_y = 0
    elif x_or_y == "y":
        x_or_y = 1

    max_x_or_y = ptsList[0][x_or_y] 
    for pt in ptsList:
        if pt[x_or_y] > max_x_or_y:
            max_x_or_y = pt[x_or_y]
        
    result = max_x_or_y
    return result

def min_xy_or_z(ptsList, xy_or_z):
    # find the minimum of set of points
    
    if xy_or_z == "x":
        xy_or_z = 0
    if xy_or_z == "y":
        xy_or_z = 1
    elif xy_or_z == "z":
        xy_or_z = 2

    min_pt = ptsList[0][xy_or_z] 
    for pt in ptsList:
        if pt[xy_or_z] < min_pt:
            min_pt = pt[xy_or_z]
        
    result = min_pt
    return result 

# -----        Main          -----

# ask user to select reef mesh
mesh_id = rs.GetObject(message="Select the reef mesh",
                           filter = 32, # mesh
                           preselect = False, 
                           select = False)

# ask user to select point cloud (copied from 3d2d_helper.3dm) 
cloud_ids = rs.GetObjects(message="Select Point Cloud",
                       filter = 2, 
                       preselect = True, 
                       select = True)

# project point cloud onto grid, forming a new point cloud
cloud_ptsList = rs.PointCloudPoints(cloud_ids[0])
proj_ptsList = rs.ProjectPointToMesh(cloud_ptsList, mesh_id, [0, 0, -10])
proj_cloud_id = rs.AddPointCloud(proj_ptsList)

# clean up points (round and take highest Z-points) 
[ptsXYZ, ptsXY] = RoundPts(proj_ptsList) 
[ptsXY_clean, ptsXYZ_clean] = TakeTopZ(ptsXY, ptsXYZ)

# re-scale Z coordinates so that the lowest Z value equals zero
# and each 4 cm above that equals 1 color change (highest possible Z = 64)
ptsXYZ_scaled = scaleZ(ptsXYZ_clean)

# determine number of rows and columns of image (incl. y and x min/max) 
y_max = max_x_or_y(ptsXYZ_scaled, "y")
y_min = min_xy_or_z(ptsXYZ_scaled, "y")
x_max = max_x_or_y(ptsXYZ_scaled, "x")
x_min = min_xy_or_z(ptsXYZ_scaled, "x")
n_rows = int(round((x_max - x_min)/unit))
n_col = int(round((y_max - y_min)/unit)) 

print("This makes a " + str(n_rows + 1) + " x " + str(n_col + 1) + " image.")

# make first, second, third, etc. until rows of image matrix
# note: all points are already sorted from RountPts/TakeTopZ functions
i_row = n_rows + 1
i_col = n_col + 1

img = []
for i in range(i_row): 
    row = ptsXYZ_scaled[i * i_col : (i+1) * i_col]
    img.append(row)

# Save as image matrix that can go into MATLAB.
str_all_rows = "[ "
for row in img:
    str_this_row = ""        
    for pt in row:
        str_this_row = str_this_row + " " + str(pt[2]*100)

    str_this_row = str_this_row + " ; " 
    str_all_rows = str_all_rows + str_this_row

str_all_rows = str_all_rows + " ]"

file = open("testfile.txt","w") 
file.write(str_all_rows) 
file.close() 

# Can't be any holes in mesh; unless I code that if a point is missing, use neighbor. 


   
# extra random notes: 
# actually can i just save this as a DEM file?
# perhaps from PhotoScan, but it's not an option in Rhino.

# I'm going to need more than 4 cm resolution ... 
# Work through layers? 10 Quadrats at a time?
# I need to keep track of the filename of each quadrat

# there might be a way in MATLAB to work directly with the 3D files. 
