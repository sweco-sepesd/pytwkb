from cStringIO import StringIO
def zz(n): return (n << 1) ^ (n >> 63)
def varint(write, value):
  bits = value & 0x7f
  value >>= 7
  while value:
    write(chr(0x80|bits))
    bits = value & 0x7f
    value >>= 7
  return write(chr(bits))

class Geometry(object):
  def __init__(self, precision=3, z=0, m=0, anchestor=None):
    self.gtype = 0
    self.hasz = z
    self.hasm = m
    self.precision = precision
    self.pointarray = StringIO()
    self.hassize = 0
    self.hasbbox = 0
    self.hasids = 0
    self.hasextendedprecision = 0
    self.isemptygeom = 1
    self.bbox = None
    self.extended_precision = None
    self._prevcoord = None
    if anchestor: 
      #print type(self).__name__, 'anchestor:', type(anchestor).__name__, anchestor._prevcoord
      self._prevcoord = anchestor._prevcoord
  def appendCoord(self, xyzm):
    val = xyzm
    if self._prevcoord: 
      val = map(lambda i: xyzm[i] - self._prevcoord[i], range(len(xyzm)))
    map(lambda d: varint( self.pointarray.write, zz(self._to_int(d))) , val)
    self._prevcoord = xyzm
    
  def as_twkb(self):
    buf = StringIO()
    buf.write(chr(zz(self.precision) << 4 | self.gtype))
    meta = self.isemptygeom << 4 | self.hasextendedprecision << 3 | self.hasids << 2 | self.hassize << 1 | self.hasbbox
    buf.write(chr(meta))
    if self.hasextendedprecision:
      buf.write(self.extended_precision.as_twkb())
    if self.hassize:
      varint(buf.write, self.size)
    if self.hasbbox:
      buf.write(self.bbox.as_twkb())
    self._write_geom(buf.write)
    return buf.getvalue()
  def _write_geom(self, write):
    pass
  def _to_int(self, d):
    return int(round(d*10**self.precision))
  def __str__(self):
    return '%s %s %s %s \n%s' % (self.gtype, self.precision, self.hasz, self.hasm, self.pointarray.getvalue())

class Point(Geometry):
  def __init__(self, xyzm, precision=3, anchestor = None):
    super(Point, self).__init__(precision, len(xyzm) > 2, len(xyzm) > 3, anchestor)
    self.gtype = 1
    self.isemptygeom = 0
    self.appendCoord(xyzm)
  def _write_geom(self, write):
    write(self.pointarray.getvalue())

class LineString(Geometry):
  def __init__(self, pts, precision=3, anchestor = None):
    super(LineString, self).__init__(precision, len(pts[0]) > 2, len(pts[0]) > 3, anchestor)
    self.gtype = 2
    self.isemptygeom = 0
    self.npoints = len(pts)
    #print pts[0], pts[-1]
    for xyzm in pts:
      self.appendCoord(xyzm)
  def _write_geom(self, write):
    varint(write, self.npoints)
    write(self.pointarray.getvalue())

class Polygon(Geometry):
  def __init__(self, rings, precision=3, anchestor = None):
    super(Polygon, self).__init__(precision, len(rings[0][0]) > 2, len(rings[0][0]) > 3, anchestor)
    self.gtype = 3
    self.isemptygeom = 0
    self.nrings = len(rings)
    self.rings = [LineString(rings[0], precision, anchestor)]
    for i in range(1, len(rings), 1):
      self.rings.append(LineString(rings[i], precision, self.rings[i-1]))
  def _write_geom(self, write):
    varint(write, self.nrings)
    for ring in self.rings:
      ring._write_geom(write)

class MultiPoint(Geometry):
  def __init__(self, pts, precision=3, anchestor = None):
    super(MultiPoint, self).__init__(precision, len(pts[0]) > 2, len(pts[0]) > 3, anchestor)
    self.gtype = 4
    self.isemptygeom = 0
    self.npoints = len(pts)
    for xyzm in pts:
      self.appendCoord(xyzm)
  def _write_geom(self, write):
    varint(write, self.npoints)
    write(self.pointarray.getvalue())
'''
p = Point([-1073741825,5899.134599], 0)
s = p.as_twkb()
print len(s)

fout = open('pl.twkb', 'wb')
fout.write(s)

l = LineString([[12.5,55.8],[12.6,55.9]], 1)
s = l.as_twkb()
print len(s)
fout.write(s)

bdy = LineString([[12.5,55.8],[12.6,55.9],[12.7,55.9]], 1)
poly = Polygon([bdy], 1)

s = poly.as_twkb()
print len(s)
fout.write(s)

mp = MultiPoint([[12.5,55.8],[12.6,55.9]], 1)
s = mp.as_twkb()
print len(s)
fout.write(s)

fout.close()
'''

