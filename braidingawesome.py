import bpy  
from mathutils import Vector 
from math import sin, cos, pi 


def clear():
    for obj in bpy.data.objects:
        if obj.type not in ('CAMERA', 'LAMP'):
            obj.select = True
        else:
            obj.select = False
    bpy.ops.object.delete()

def nurbs_circle(name, w, h):
    pts = [(-w/2, 0, 0), (0, -h/2, 0), (w/2, 0, 0), (0, h/2, 0)]
    return MakePolyLine(name, name + '_curve', pts)

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

def poly_lines(objname, curvename, lines, bevel=None, joins=False, ctype='NURBS'):
    curve = bpy.data.curves.new(name=curvename, type='CURVE')
    curve.dimensions = '3D'
  
    obj = bpy.data.objects.new(objname, curve)  
    obj.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(obj)
    
    for i, line in enumerate(lines):
        poly_line(curve, line, joins if type(joins)==bool else joins[i], type=ctype)
    
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


def braid_strand(length, strands, strandnum, width=1, x0=0, y0=None, ym=.5, xm=1, zm=1, taper=False, ds = None, resolution=2):
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
    for y in range(length * steps * resolution):
        y /= resolution
        y += i0
        x = cos(a*y)*xm
        z = sin(b*y)*zm
        yield mul(width, (x + x0, y * ym + y0, z))



def make_braid(name, strands=3, length=5, bevel='circle', circle=False, **kwds):
    '''Make a braid object'''
    lines = []
    for i in range(strands):
        strand = tuple(braid_strand(length, strands, i, **kwds))
        if circle:
            strand = tuple(circlify(strand))
        lines.append(strand)
    return poly_lines(name, name + '_curve', lines, bevel, circle)

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


def circlify(points, gap = None, circles=1):
    zavg = sum(p[2] for p in points) / len(points)
    # yavg = sum(p[1] for p in points) / len(points)
    x,y,z = points[0]
    ylast = points[-1][1]
    w = (ylast - y) / circles
    radius = w / 2 / pi
    center = 0, 0
    if gap is None:
        gap = (ylast - y) / len(points)
    for a,b,c in points:
        down = (ylast - b) / (w + gap) * 2 * pi
        r = radius + (c - zavg)
        ny, nz = angle_point(center, down, r)
        yield a, ny, nz

def defaultCircle(w=.6):
    circle = nurbs_circle('circle', w, w)
    circle.hide = True
    return circle

def defaultStar():
    star = MakePolyLine('star', 'staz', tuple(star_pts(points=5, r=.5, ir=.05)), type='NURBS')
    star.hide = True
    return star

def example1():
    '''A 4 strand braid'''
    clear()
    defaultStar()
    make_braid('Braid', 4, length=3, xm=1, zm=.5, ym=1, taper=True, bevel='star')

def example2():
    '''A tube wrapped into a band'''
    clear()
    defaultStar()
    tube = [(0, y, 0) for y in range(-5, 5)]
    otube = MakePolyLine('t', 't', tube, bevel='star')
    otube = MakePolyLine('t', 't', list(circlify(tube)), bevel='star', join=True)

def example3():
    '''A braided bracelet'''
    clear()
    defaultCircle()
    make_braid('Braid', 4, length=3, xm=1, zm=.2, ym=1, taper=True, bevel='circle', circle=True)

def braid_bracelet(sides=7, order=3, bevel='circle', pointy=False, **kwds):
    length = sides * 2
    strand = tuple(braid_strand(length, order, 0, **kwds))
    strand = tuple(circlify(strand, circles=order, gap = 0))
    type = {True: 'POLY', False: 'NURBS'}[pointy]
    if not pointy:
        strand = strand[:-1]
    else:
        strand = (strand[-1],) + strand
    MakePolyLine('Braid', 'Braid_c', strand, bevel=bevel, join=True, type=type)


def example4():
    '''One continuous strand bracelet'''
    clear()
    defaultCircle()
    braid_bracelet(sides=13, order=3, xm=1, zm=.3, ym=1)

def example5():
    '''Pointy Star bracelet'''
    clear()
    defaultStar()
    braid_bracelet(sides=5, order=3, xm=1, zm=1.3, ym=1, bevel='star', resolution=1, pointy=True)


def example6():
    '''Ring'''
    clear()
    defaultCircle()
    defaultStar()
    braid_bracelet(sides=16, order=3, xm=1, zm=.4, ym=.5, bevel='circle', resolution=1, pointy=False)

def braid_line4(center, radius, strands, sides, spacing=.4, thickness=.2, resolution=1):
    cx, cy = center

    numpoints = strands * (sides * 4) * resolution
    dtheta = 2 * pi / (sides * resolution * 3)
    steps = (strands - 1) * 2
#    dz = dtheta * pi
    
    a = pi / steps
    b = pi / 2
    for i in range(0, numpoints - sides * strands):
        i /= resolution
        r = sin(b * i) * thickness
        x, y = angle_point(center, i * dtheta, radius + r)
        #x = r
        #y = i/3
        z = cos(i * a)
        yield x, y, z


def braid_line3(center, radius, strands, sides, spacing=.4, thickness=.2, resolution=1):
    cx, cy = center

    numpoints = strands * (sides * strands) * resolution - (sides - strands - 1)
    dtheta = 2 * pi / (sides * resolution * 8/strands)
    steps = (strands - 1) * 2
#    dz = dtheta * pi
    
    a = pi / steps
    b = pi / 2
    # 5 sides, 1
    # 8 sides, 4
    # 7 sides, 3
    for i in range(0, int(numpoints)):
        i /= resolution
        r = sin(b * i) * thickness
        x, y = angle_point(center, i * dtheta, radius + r)
        #x = r
        #y = i/3
        z = cos(i * a)
        yield x, y, z

# 5
def braid_line(center, radius, strands, sides, spacing=.4, thickness=.2, resolution=1):
    cx, cy = center
    # sides = 6
    numpoints = strands * (sides * strands + 1) * resolution / 2 - 6
    dtheta = 2 * pi / (sides * resolution * 12/5)
    steps = (strands - 1) * 2
#    dz = dtheta * pi
    
    a = pi / steps
    b = pi / 2
    # 5 sides, 1
    # 8 sides, 4
    # 7 sides, 3
    for i in range(0, int(numpoints)):
        i /= resolution
        r = sin(b * i) * thickness
        x, y = angle_point(center, i * dtheta, radius + r)
        #x = r
        #y = i/3
        z = cos(i * a) * spacing
        yield x, y, z


def real_braid(strands=3, sides=5, bevel='circle', pointy=False, **kwds):
    line = tuple(braid_line((0, 0), 2, strands, sides, **kwds))
    type = {True: 'POLY', False: 'NURBS'}[pointy]
    MakePolyLine('Braid', 'Braid_c', line, bevel=bevel, join=True, type=type)

def example7():
    '''Ring'''
    clear()
    defaultCircle(.4)
    defaultStar()
    real_braid(strands=5, sides=8, thickness=.4, spacing=.4)


import sys
sys.path.append('/Users/jared/clone/blender')
import imp
import braid
from braid import angle_point
imp.reload(braid)
def awesome_braid(strands=3, sides=5, bevel='circle', pointy=False, **kwds):
    lines = braid.strands(strands, sides, **kwds)
    type = {True: 'POLY', False: 'NURBS'}[pointy]
    # MakePolyLine('Braid', 'Braid_c', line, bevel=bevel, join=True, type=type)
    poly_lines('ABraid', 'ABraid_c', lines, bevel=bevel, joins=True, ctype=type)

def example8():
    '''Good solid ring'''
    clear()
    defaultCircle(.4)
    defaultStar()
    awesome_braid()

example8()
