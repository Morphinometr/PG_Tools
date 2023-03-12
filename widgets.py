import bpy
import math
from mathutils import Vector, Quaternion


def create_wgt_square(name : str, size : float = 1.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    radius = size/5
    coord = size/2 - radius
    verts_num = 10
    angle = math.pi/2/verts_num

    vertices = []
    # define centers and create vertices for arcs of each corner of the rounded square 
    center = (coord, 0, -coord)
    for v in range(verts_num):
        vert = (center[0] + math.sin(angle * v) * radius, 0, center[2] - math.cos(angle * v) * radius)
        vertices.append(vert)
        
    center = (coord, 0, coord)
    for v in range(verts_num):
        vert = (center[0] + math.cos(angle * v) * radius, 0, center[2] + math.sin(angle * v) * radius)
        vertices.append(vert)
        
    center = (-coord, 0, coord)
    for v in range(verts_num):
        vert = (center[0] + math.sin(-angle * v) * radius, 0, center[2] + math.cos(angle * v) * radius)
        vertices.append(vert)
        
    center = (-coord, 0, -coord)
    for v in range(verts_num):
        vert = (center[0] - math.cos(angle * v) * radius, 0, center[2] - math.sin(angle * v) * radius)
        vertices.append(vert)

    # create edges 
    edges = [(i, (i + 1) % len(vertices)) for i in range(len(vertices))]

    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    return obj


def create_wgt_cube(name : str, size : float = 1.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    coords = [-size/2, size/2]

    vertices = [(x, y, z) for x in coords for y in coords for z in coords]
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]

    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    return obj


def create_wgt_circle(name : str, size : float = 1.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    radius = size/2
    num_vertices = 32
    angle = 2 * math.pi / num_vertices
    
    vertices = []
    for i in range(num_vertices):
        x = math.cos(angle * i) * radius
        y = 0
        z = math.sin(angle * i) * radius
        vertices.append((x, y, z))
    
    edges = [(i, (i + 1) % num_vertices) for i in range(num_vertices)]

    # Create the mesh from the vertices and edges
    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    return obj


def create_wgt_sphere(name : str, size : float = 1.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    radius = size/2
    num_vertices = 32

    # define orientations of the circles
    orientations = [Quaternion((1.0, 0.0, 0.0), math.pi/2), Quaternion((0.0, 1.0, 0.0), math.pi/2), Quaternion((0.0, 0.0, 1.0), math.pi/2)]

    # create the vertices and edges for each circle
    vertices = []
    edges = []
    for i, orientation in enumerate(orientations):
        for j in range(num_vertices):
            angle = j / float(num_vertices) * 2.0 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vert = Vector((x, y, 0.0))
            vert.rotate(orientation)
            vertices.append(vert)

            # create edges between the vertices
            if j == num_vertices-1:
                edges.append((j+i*num_vertices, i*num_vertices))
            else:
                edges.append((j+i*num_vertices, j+1+i*num_vertices))

    # create the mesh using the vertices and edges lists
    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    return obj