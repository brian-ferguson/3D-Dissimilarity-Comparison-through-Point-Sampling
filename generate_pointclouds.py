#take a input and convert all the faces in the meshes facelist to triangles
import Rhino, scriptcontext, math, random, sys, itertools
import rhinoscriptsyntax as rs
import rhinoscript.utility as rhutil
from functools import reduce

#meshing parameter list
jaggedAndFaster = Rhino.Geometry.MeshingParameters.Coarse
smoothAndSlower = Rhino.Geometry.MeshingParameters.Smooth
defaultMeshParams = Rhino.Geometry.MeshingParameters.Default
minimal = Rhino.Geometry.MeshingParameters.Minimal

#object type enumeration list
poly_type = 16;
extrusion_type = 1073741824;
surface_type = 8;

#prompts the user to select a layer in the layer table
#return: the specified layername
def SelectLayer():
    layername = rs.ListBox(rs.LayerNames(), "Select a layer")
    return layername

#prompts the user to select as many layers as comparison requires
#takes: user input (prompt layer panel selection)
#returns: the layer names as a list
def SelectLayers(layer_count):
    layers_selected = 0
    selected_layers = []
    while(layers_selected < layer_count):
        #prompt the user to select a layer
        layer_name = SelectLayer()
        if(layer_name and layer_name not in selected_layers):
            #add the selected layer to the selected layers list
            selected_layers.append(layer_name)
            #increment the layers_selected count
            layers_selected += 1
        elif(layer_name and layer_name in selected_layers):
            #display an error message stating that the layer has already been selected
            rs.MessageBox("This layer has already been selected!", title="Duplicate Layer Selection")
    #if the required layers have been selected return the list of selected layers
    if(len(selected_layers) == layer_count):
        #return the list of selected layers
        return selected_layers

#takes: a list of layer names
#returns: a list of the guid of the objects on that layer
def GetLayerObjects(layer_name):
    #create a list to hold the layers objects
    layer_objects =rs.ObjectsByLayer(layer_name, select=False)
    #if the layer returned layer objects
    if(layer_objects):
        #return those objects
        return layer_objects

#takes: a list of layer names
#returns: a list of lists containing all objects of a specified type on those layers
def GetLayersObjects(layer_name_list):
    #create a list to hold the lists of layer objects
    layers_objects = []
    #for each layer in the layer name list
    for layer_name in layer_name_list:
        #get the list of the layers guids
        layer_objects = GetLayerObjects(layer_name)
        #if the layer_objects returned
        if(layer_objects):
            #add the list to the list of layers_objects
            layers_objects.append(layer_objects)
    #if the list of returned layers_objects is equal to the length of layer names
    if(len(layers_objects) == len(layer_name_list)):
        #return the list of layer guid lists
        return layers_objects
    #if the list of returned layers_objects is not equal to the length of layer names
    else:
        #return false as a error status
        return False

#takes: a list of lists containing guids
#returns: triangulated mesh objects
def GetTriangulatedMeshes(layers_objects):
    #list to hold the list of layer object guids
    layers_objects_brep = []
    #for each layers list of lists
    for layer_objects in layers_objects:
        #create a new list to hold the layers list of guids represented as objrefs
        layer_objects_brep = []
        for layer_object in layer_objects:
            #convert the guid to a brep
            layer_brep = rs.coercebrep(layer_object)            
            #if the obj ref for the object was returned
            if(layer_brep):
                #convert the brep into a mesh
                mesh = Rhino.Geometry.Mesh.CreateFromBrep(layer_brep, smoothAndSlower)
                #if the mesh is not null
                if(mesh):
                    #create a new empty mesh objref
                    new_mesh = Rhino.Geometry.Mesh()
                    #for each face in the mesh list [of type array]
                    for m in mesh:
                        #add the mesh face to the new_mesh objref
                        new_mesh.Append(m)                        
                    #check if the new mesh contains any quad faces
                    #if(new_mesh and new_mesh.Faces.QuadCount > 0):
                    if(new_mesh):                        
                        #convert the facelist of the new_mesh objref
                        new_mesh_triangulated = new_mesh.Faces.ConvertQuadsToTriangles()                        
                        #if the new_mesh_triangulated was returned
                        if(new_mesh_triangulated):
                            #coerce the guid from the objref of the triangulate mesh [layer_object describes the guid that the objref was generated from]
                            id = rhutil.coerceguid(layer_object, True)
                            #add the guid of the triangulated mesh to the active document
                            added_mesh = scriptcontext.doc.Objects.AddMesh(new_mesh)                            
                            #move the mesh to the layer of its source guid that generated the objref
                            rs.ObjectLayer(added_mesh, rs.ObjectLayer(layer_object))                            
                            #add the guid of the triangulated mesh to the layer_objects list
                            layer_objects_brep.append(added_mesh)                            
        #compare the length of the layer_objects_brep and the length of the layer_objects
        if(len(layer_objects_brep) == len(layer_objects)):
            #append the layer_objects_brep to the layers_objects_brep
            layers_objects_brep.append(layer_objects_brep)
    #if the length of the layers_objects_brep is equal to the length of layers_objects then return the layers_objects_brep list
    if(len(layers_objects_brep) == len(layers_objects)):
        return layers_objects_brep        
    else:
        return False

#takes: the number of coordinates to generate
#returns: point 3d for the randomly generated coordinate to n specification
def GenerateCoordinates(point_count):
    #count the generated ordinates
    generated_points = 0
    #list to hold the generated ordinates
    point_list = []
    while(generated_points < point_count):
        random_point = GenerateCoordinate(3)
        #verify the ordinate value has not been generated already
        if not(random_point in point_list):
            #add the new point to the point list
            point_list.append(random_point)
            #increment the generate_points count
            generated_points += 1
      #return the point_list it is equal to the
    if(len(point_list) == point_count):
        return point_list
       
#takes: the number of coordinates to generate
#returns: point 3d for the randomly generated coordinate to n specification
def GenerateCoordinate(coordinate_count):
    #list to hold the random points generated
    random_coordinates = []
    random_coordinate = []
    random_normal_coordinate = []
    #generate 3 random values from 0 - 1
    for i in range(coordinate_count):
        r = random.uniform(0,1)
        random_coordinate.append(r)
    #if the correct amount of ordinates have been generated
    if(len(random_coordinate) == coordinate_count):
        #calculate the sum of the random_coordinate
        s = sum(random_coordinate)
        for coordinate in random_coordinate:
            #normalize the coordinate value by dividing by the sum
            normalized = coordinate / s
            random_normal_coordinate.append(normalized)
        #if the length of the normal coordinate list is full
        if(len(random_normal_coordinate) == coordinate_count):
            #create a point object from the normalized random coordinate
            normal_point = rs.CreatePoint(random_normal_coordinate[0],random_normal_coordinate[1],random_normal_coordinate[2])
    return normal_point

#takes: a mesh guid
#returns: a list the meshes faces (by index) and the vertices of that face
def GetMeshVertices(mesh_guid):
    #coerce the mesh_guid
    mesh_objref = rs.coercemesh(mesh_guid)
    #create a list to hold a list of vertices per face
    mesh_faces = []
    #get the faces of the mesh
    for index in range(mesh_objref.Faces.Count):
        #get the vertices of the face at the current index
        face_vertices = mesh_objref.Faces.GetFaceVertices(index)
        #if the vertices of the face were returned > the element at the first index will be a True boolean
        if(face_vertices[0] and face_vertices[3] == face_vertices[4]):
            mesh_faces.append([face_vertices[1],face_vertices[2],face_vertices[3]])
    #if the mesh_faces has elements equal to the faces of the mesh
    if(len(mesh_faces) == mesh_objref.Faces.Count):
        #return the list of mesh faces
        return mesh_faces

#takes: a list of mesh faces vertices information and a list of random noramlized points
#return a rhino pointcloud object instead of a list of points
def GeneratePoints(mesh_faces, random_coordinates):
    #create a list to hold the points generated
    pointcloud = []
    #extract the value of each vertexs coordinate
    for mesh_face in mesh_faces:
        #get the vertices of the triangular face
        vertex_a = mesh_face[0]
        vertex_b = mesh_face[1]
        vertex_c = mesh_face[2]
        #for each random coordinate in the list of random coordinates
        for random_coordinate in random_coordinates:
            #calculate the 3d point equivalent to the random normalized coordinate
            #determine the r1 and r2 values (should be equal to 2 of (s,r,t))
            r1 = random_coordinate.Y
            r2 = random_coordinate.Z
            #calculate the 3d cartesian equivalent
            point_x = (1- math.sqrt(r1)) * vertex_a.X + math.sqrt(r1) * (1- r2) * vertex_b.X + math.sqrt(r1) * r2 * vertex_c.X
            point_y = (1- math.sqrt(r1)) * vertex_a.Y + math.sqrt(r1) * (1- r2) * vertex_b.Y + math.sqrt(r1) * r2 * vertex_c.Y
            point_z = (1- math.sqrt(r1)) * vertex_a.Z + math.sqrt(r1) * (1- r2) * vertex_b.Z + math.sqrt(r1) * r2 * vertex_c.Z
            #create a new point to hold the 3d point equivalent
            point = rs.CreatePoint(point_x, point_y, point_z)
            #add that point to the point cloud (CHECK IF THE POINT EXISTS ON THE SURFACE OF THE MESHFACE)
            pointcloud.append(point)
            #return the pointcloud as a list of pointcloud lists
    if(len(pointcloud) == len(mesh_faces) * len(random_coordinates)):
        #return the pointcloud (list of points)
        return pointcloud
    else:
        #return false to indicate an error
        return False

#takes a list of mesh guids contained on a specified layer
#returns a one-dimensional list of the points on the mesh faces
def GeneratePointCloud(mesh_objects, random_coordinates):
    #create a list of points for each mesh object on the layer
    point_clouds = []
   
    #for each mesh object in the list of mesh_objects (guid)
    for mesh_object in mesh_objects:
        #get a list of the mesh objects vertices by face
        mesh_vertices = GetMeshVertices(mesh_object)
        #pass the mesh vertices and a list of randomly generated points of equal length to the GeneratePoints method
        point_cloud = GeneratePoints(mesh_vertices,random_coordinates)
        #if the pointcloud is not null append it to the list of point lists (by polysurface)
        if(point_cloud):
            point_clouds.append(point_cloud)
           
    #flatten the multi dimensional list into a one dimensional list
    reduced_pointcloud = reduce(lambda x,y: x+y, point_clouds)
   
    if(reduced_pointcloud):
        return reduced_pointcloud
    else:
        return False

#takes: a list of 3d point objects
#returns:
def DrawPointCloud(point_list, layer_name):
    for point in point_list:
        new_point = rs.AddPoint(point)
        rs.ObjectLayer(new_point, layer_name)

#takes: a list of point lists
#returns: the different points in a color and the other points in white
def MapPointClouds(pointclouds):
    
    #consider just two point clouds
    pointcloud_a = pointclouds[0]
    pointcloud_b = pointclouds[1]
    
    for point_a in pointcloud_a:
        
        #get the closest point in the other pointcloud
        closest_point = rs.PointClosestObject(point_a, pointcloud_b)
        
        #get the distance between point_a and the closest_point
        distance = rs.Distance(point_a, closest_point)
        
        if(distance > 0):
            point_1 = rs.AddPoint(point_a)
            point_2 = rs.AddPoint(closest_point)


if(__name__ == "__main__"):
    #specify the object filters (restricted to types that can be converted to meshes)
    type_list = [poly_type, surface_type, extrusion_type]
   
    #prompt the user to select layers for comparison
    required_layer_count = 2
    selected_layers  = SelectLayers(required_layer_count)
   
    #get the layer objects of each selected layer
    layers_objects = GetLayersObjects(selected_layers)
   
    #convert each object to a mesh > get the face list > triangulate (in the form of a list containing: a list of guids of mesh objects (added to the document))
    triangulated_meshes = GetTriangulatedMeshes(layers_objects)
   
    #prompt the user to specify the number of point samples per mesh face
    required_face_points = 8
   
    #LIST: LAYERS to be compared
    #LIST: POLYSURFACES per layer compared
    #LIST: MESH FACES per polysurface per layer compared
   
    #generate a list of random normalized coordinates equal in length to the length of
    random_coordinates = GenerateCoordinates(required_face_points)
   
    pointclouds = []
   
    #MapPointClouds(pointclouds)
   
    print(len(pointclouds))
   
    """
    for index in range(len(selected_layers)):
        #send a list of polysurface objects converted to triangulated meshes as a list and a list of random normalized coordinates
        pointcloud = GeneratePointCloud(triangulated_meshes[index], random_coordinates)
        #draw the points to the layer of the mesh object
        DrawPointCloud(pointcloud, selected_layers[index])
    """