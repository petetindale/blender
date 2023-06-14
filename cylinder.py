import bpy
import math
import numpy as np

total_height = 5.5
circle_radius = 4.3
row_height = 0.05
angle_inc = 1
pcv = int(360/angle_inc) + 1


def circle(radius, location):
    circle_verticies = []
    (a,b,c) = location

    for angle in range(0, 360, angle_inc):
      angle_radius = math.radians(angle)
      x = a + radius * math.cos(angle_radius)
      y = b + radius * math.sin(angle_radius)
      circle_verticies.append([x,y, c]) 
    circle_verticies.append(circle_verticies[0])
    return circle_verticies


def adjust_radius(zpos, max_height, curr_radius):
    offset = 0.5
    adjust_height = 1.3
    
    half_height = max_height/2
    
    pos_radius = curr_radius
    if zpos < offset : pos_radius = circle_radius
    elif zpos > max_height - offset: pos_radius = circle_radius
    else : pos_radius = circle_radius - adjust_height + ((zpos - half_height) ** 2 / ((half_height+offset)**2 /2))
    return pos_radius

def cylinder(radius, height, adjust, per_circle_verticies):
    cylinder_verticies = []
    for z in np.arange(0, height, row_height):
        if adjust == 1 : pos_radius = adjust_radius(z, height, radius)
        else : pos_radius = radius
        
        verticies = circle(pos_radius, (0,0,z))
        cylinder_verticies += verticies

    cylinder_rows = int(height / row_height)
    faces = []
    for row in range(0, cylinder_rows - 1):
        for index in range(0, pcv -1):
            vertex1 = index + (row * per_circle_verticies)
            vertex2 = vertex1 + 1
            vertex3 = vertex1 + per_circle_verticies
            vertex4 = vertex2 + per_circle_verticies
            faces.append([vertex1,vertex3,vertex4,vertex2])
    return (cylinder_verticies, faces)


# Create two cylinders.
(verts1, faces1) = cylinder(circle_radius, total_height, 1, pcv)
(verts2, faces2) = cylinder(0.6, total_height, 0, pcv)


# Combine two lists of verticies from two cylinders
verts = verts1 + verts2

# Number of verticies for each cylinder
num_verticies = len(verts2)

# Update the faces of the verticies for the second cylinder to the new verticies index
faces2r = list(map(lambda x: list(map(lambda y: y + num_verticies, x)), faces2))

# Combine two lists of faces
faces = faces1 + faces2r

# Create faces for cover bottom
for cov in range(0, pcv -1):
    a = cov
    b = cov + 1 
    c = num_verticies + a
    d = num_verticies + b
    faces.append([a,b,d,c])

# Create faces for cover on  top
for cov in range(len(verts1)-pcv, len(verts1) -1):
    a = cov
    b = cov + 1 
    c = num_verticies + a
    d = num_verticies + b
    faces.append([a,b,d,c])


# Remove existing models
objs = [ob for ob in bpy.context.scene.objects if ob.type in ('MESH')]
bpy.ops.object.delete({"selected_objects": objs})

# Set units to cms
bpy.context.scene.unit_settings.scale_length = 0.01

# Create mesh and add verticies and faces.
new_mesh = bpy.data.meshes.new("new_mesh")
new_mesh.from_pydata(verts, [], faces)
new_mesh.update()

# Mesh in order to get watertight
new_object = bpy.data.objects.new("roller", new_mesh)
remesh = new_object.modifiers.new('Remesh', 'REMESH')
remesh.voxel_size = 0.01

# Smooth to remove any artefacts
corrsmo = new_object.modifiers.new('CorrectiveSmooth', 'CORRECTIVE_SMOOTH')
corrsmo.use_only_smooth = True
corrsmo.iterations = 15

# Set View
view_layer = bpy.context.view_layer
view_layer.active_layer_collection.collection.objects.link(new_object)

