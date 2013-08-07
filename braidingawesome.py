import bpy  
from mathutils import Vector 
from math import sin, cos, pi 

def clear():
    for obj in bpy.data.objects:
        obj.select = True
    bpy.ops.object.delete()

def nurbs_circle(name, w, h):
    pts = [(-w/2, 0, 0), (0, -h/2, 0), (w/2, 0, 0), (0, h/2, 0)]
    return MakePolyLine(name, name + '_curve', pts)

def angle_point(center, angle, distance):
    cx, cy = center
    x = cos(angle) * distance
    y = sin(angle) * distance
    return x + cx, y + cy

def zzero(pos):
    return pos + (0,)

def poly_line(curve, points, join=True, type='NURBS'):
    polyline = curve.splines.new(type)
    polyline.points.add(len(points)-1)  
    for num in range(len(points)):
        polyline.points[num].co = (points[num])+(1,)  
  
    polyline.order_u = len(polyline.points)-1
    if join:
        polyline.use_cyclic_u = True

def poly_lines(objname, curvename, lines, bevel=None, joins=False):
    curve = bpy.data.curves.new(name=curvename, type='CURVE')
    curve.dimensions = '3D'
  
    obj = bpy.data.objects.new(objname, curve)  
    obj.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(obj)
    
    for i, line in enumerate(lines):
        poly_line(curve, line, joins if type(joins)==bool else joins[i])
    
    if bevel:
        curve.bevel_object = bpy.data.objects[bevel]
    return obj

def MakePolyLine(objname, curvename, cList, bevel=None, join=True, type='NURBS'):
    curve = bpy.data.curves.new(name=curvename, type='CURVE')  
    curve.dimensions = '3D'
  
    obj = bpy.data.objects.new(objname, curve)  
    obj.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(obj)
  
    poly_line(curve, cList, join, type=type)

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

def braid_strand(length, strands, strandnum, width=1, x0=0, y0=None, ym=.5, xm=1, zm=1, taper=False, ds = None):
    '''Calculate the points for a single strand of a braid.
    Lots of variables here, feel free to fiddle.
    '''
    if y0 is None:
        y0 = -length * strands / 2
    if ds is None:
        ds = strands * 2
    steps = (strands - 1)*2

    a = pi/steps
    b = pi/2
    
    dy = 2 * pi / strands / a
    y0 += strandnum * dy * ym
    i0 = 0 if not taper else - strandnum * (strands + ds) / 4
    for y in range(length * steps * 2):
        y *= .5
        y += i0
        x = cos(a*y)*xm
        z = sin(b*y)*zm
        yield mul(width, (x + x0, y * ym + y0, z))



def make_braid(name, strands=3, length=5, bevel='circle', **kwds):
    '''Make a braid object'''
    lines = []
    for i in range(strands):
        lines.append(tuple(braid_strand(length, strands, i, **kwds)))
    return poly_lines(name, name + '_curve', lines, bevel, False)

# 3-5: 2
# 6 :  1
# 7 :  0
# 8 : -1
# 9 : -2
# 10: -3

def star_pts(r=1, ir=None, points=5, center = (0, 0)):
    '''Create points for a star. They are 2d - z is always zero
    
    r: the outer radius
    ir: the inner radius
    '''
    if not ir: ir = r/5
    pts = []
    dt = pi * 2 / points
    for i in range(points):
        t = i * dt
        ti = (i + .5) * dt
        pts.append(angle_point(center, t, r))
        pts.append(angle_point(center, ti, ir))
    return map(zzero, pts)

clear()
circle = nurbs_circle('circle', 1, 1)
circle.hide = True

star = MakePolyLine('star', 'staz', tuple(star_pts(points=5, r=.5, ir=.05)), type='NURBS')
star.hide = True

# change bevel to "circle" 
make_braid('Braid', 4, length=3, xm=1, zm=.5, ym=1, taper=True, bevel='star')