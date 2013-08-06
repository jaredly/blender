import bpy  
from mathutils import Vector 
from math import sin, cos, pi 

# weight  
w = 1 

def clear():
    for obj in bpy.data.objects:
        obj.select = True
    bpy.ops.object.delete()

listOfVectors = [(0,0,0),(1,0,0),(2,0,0),(2,3,0),(0,2,1)]  

def nurbs_circle(name, w, h):
    pts = [(-w/2, 0, 0), (0, -h/2, 0), (w/2, 0, 0), (0, h/2, 0)]
    return MakePolyLine(name, name + '_curve', pts)
    
def MakePolyLine(objname, curvename, cList, bevel=None, join=True):
    curve = bpy.data.curves.new(name=curvename, type='CURVE')  
    curve.dimensions = '3D'
  
    obj = bpy.data.objects.new(objname, curve)  
    obj.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(obj)
  
    polyline = curve.splines.new('NURBS')  
    polyline.points.add(len(cList)-1)  
    for num in range(len(cList)):  
        print('Things', cList[num])
        polyline.points[num].co = (cList[num])+(w,)  
  
    polyline.order_u = len(polyline.points)-1
    if join:
        polyline.use_cyclic_u = True

    if bevel:
        curve.bevel_object = bpy.data.objects[bevel]
    return obj

def torous(t, a, b):
    return cos(a*t) + .2 * cos((a-b)*t), sin(a*t) + .2 * sin((a-b)*t), sin(b*t)

def mul(x, items):
    return tuple(x*b for b in items)

def trefoil3(t, width):
    xyz = sin(t) + 2 * sin(2 * t), cos(t) - 2 * cos(2 * t), -sin(3 * t)
    return tuple(p*width for p in xyz)

def trefoil(width, segs, a=1, b=3):
    angle = pi * 2.0 / segs
    for i in range(0, segs):
        print(i, angle*i)
        yield mul(width, torous(angle * i, a, b))

# MakePolyLine("co1", "c1", tuple(trefoil(3, 12, 3, 5)), bevel='NurbsCircle')

def braid_strand_old(times, strands=3, width=2, yby=None, ix=0, iy=0):
    if not yby: yby = strands - 1
    for y in range(times * strands):
        x = sin(pi/3 * y)
        z = sin(2*pi/3 * y)
        print(x,y,z)
        yield mul(width, (x + ix, y/yby + iy, z))

def braid_strand(length, strands=3, width=2, ymul=0, strandnum=0, x0=0, y0=0):
    if not ymul:
        ymul = strands - 1
    steps = (strands - 1)*2
    # FIXME this actually needs to be relative to PI
    y0 += strandnum * (strands + 8)/4 / ymul
#    3 -> 11 / 4
#    4 -> 12 / 4
#    6/3
    a = pi/steps
    b = pi/2
    for y in range(length * steps * 2):
        y *= .5
        x = cos(a*y)*10
        z = sin(b*y)
        yield mul(width, (x + x0, y / ymul + y0, z))

#def braid(length, width, strands=3, ix=0, iy=0):
#    for i in range(strands

clear()
nurbs_circle('circle', 2, 2)

doot = 3
for i in range(doot):
    MakePolyLine("co2", "c2", tuple(braid_strand(5, doot, 1, 1, i, y0=-15)), bevel='circle', join=False)
