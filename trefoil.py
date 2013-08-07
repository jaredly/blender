import bpy  
from mathutils import Vector  

# weight  
w = 1 

listOfVectors = [(0,0,0),(1,0,0),(2,0,0),(2,3,0),(0,2,1)]  
  
def MakePolyLine(objname, curvename, cList, bevel=None):
    curve = bpy.data.curves.new(name=curvename, type='CURVE')  
    curve.dimensions = '3D'  
  
    obj = bpy.data.objects.new(objname, curve)  
    obj.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(obj)
  
    polyline = curve.splines.new('NURBS')  
    polyline.points.add(len(cList)-1)  
    for num in range(len(cList)):  
        polyline.points[num].co = (cList[num])+(w,)  
  
    polyline.order_u = len(polyline.points)-1
    polyline.use_endpoint_u = True

    if bevel:
        curve.bevel_object = bpy.data.objects[bevel]

def trefoil3(t, width):
    xyz = sin(t) + 2 * sin(2 * t), cos(t) - 2 * cos(2 * t), -sin(3 * t)
    return tuple(p*width for p in xyz)

def trefoil(width, segs):
    angle = math.pi * 2.0 / segs
    for i in range(0, segs):
        yield trefoil3(angle * i, width)
    yield trefoil3(0, width)

MakePolyLine("co1", "c1", tuple(trefoil(1, 6)), bevel='NurbsCircle')
