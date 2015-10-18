import pyglet, math
from pyglet.graphics import TextureGroup
# from pyglet.graphics.vertexdomain import VertexList
from pyglet.gl import *
from pyglet.window import key as K

SQ_8 = math.sqrt(8)/10.
SQ_2 = math.sqrt(2)/10.
# print ".8:",SQ_8,".2",SQ_2

so=sn=out=""

def write(*s):
	global so,sn,out
	sn = " ".join(str(_) for _ in s)
	if so!=sn:
		print sn+"\n"
		# out+=sn+"\n\n"
		so=sn

def vertColl(y,h,fl,cl): #(Y-coor, Height, Floor, Ceiling)
	a=fl<y<=cl
	b=fl<y+h<=cl
	c=y<fl<=y+h
	d=y<=cl<=y+h
	e=any([a,b,c,d])
	return e

def vertIn(y,h,fl,cl):
	return fl-h/2.<=y+h/2.<=cl+h/2.+.2

def edge2vert(edges):
	x1,x2,y1,y2,z1,z2 = edges
	return (x1,y1,z1, x2,y1,z1, x2,y1,z2, x1,y1,z2,
			x1,y2,z1, x2,y2,z1, x2,y2,z2, x1,y2,z2,
			x1,y1,z1, x1,y2,z1, x2,y2,z1, x2,y1,z1,
			x1,y1,z2, x1,y2,z2, x2,y2,z2, x2,y1,z2,
			x1,y1,z1, x1,y1,z2, x1,y2,z2, x1,y2,z1,
			x2,y1,z1, x2,y1,z2, x2,y2,z2, x2,y2,z1)

class Window(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(Window, self).__init__(*args, **kwargs)
		self.world = World()
		self.position = self.world.start[:3]
		self.rotation = self.world.start[-1]
		self.motion = [0,0]
		self.fall = False
		self.speed = 3
		self.back = False
		self.front = (0,0)
		self.start = 0
		self.Height = 0.7
		self.info = pyglet.text.Label('0,0,0; 0,0',color=(255,)*4,font_size=20,x=5,y=5)
		self.time = (0,0)
		glClearColor(0.43,0.86,0.96,1)
	
	# def on_close(self):
		# global out
		# f=open(r".\log.txt","w")
		# f.write(out)
		# f.close()
	
	def on_draw(self):
		self.clear()
		
		width,height = self.get_size()
		glEnable(GL_DEPTH_TEST)
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(65.0, width / float(height), 0.1, 50.0)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		x, y = self.rotation
		if self.back:
			x-=self.start[0]
			x/=6.
			x+=self.start[0]+180
			y-=self.start[1]
			y/=6.
			y=360-self.start[1]-y
		glRotatef(x, 0, 1, 0)
		glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
		x, y, z = self.position
		glTranslatef(-x, -(y+0.5), -z)
		
		self.world.batch.draw()
		self.world.itmbt[1].draw()
		self.world.doorbatch.draw()
		
		x, y, z = self.world.AIpos
		glTranslatef(x, y, z)
		y, x= self.world.AIrot
		glRotatef(x, 0, 1, 0)
		glRotatef(y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
		
		self.world.itmbt[0].draw()
		
		
		self.info.text = "%.2f,%.2f,%.2f; %.2f,%.2f; %d fps" % (tuple(self.position)+self.rotation+(pyglet.clock.get_fps(),))
		
		glDisable(GL_DEPTH_TEST)
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		self.info.draw()
		
		w=width/2
		h=height/2
		self.cross = pyglet.graphics.vertex_list(4,
			('v2i',(w-5,h,w+5,h,w,h-5,w,h+5)),
			('c4B',(255,255,255,200)*4))
		self.cross.draw(GL_LINES)
	
	def on_mouse_press(self, x, y, but, mod):
		rx,ry=self.rotation
		x,y,z=self.position
		planes=self.world.planes
		items =self.world.items
		y+=.5
		
		m = math.cos(math.radians(ry))
		dx= math.cos(math.radians(rx-90))*m
		dy= math.sin(math.radians(ry))
		dz= math.sin(math.radians(rx-90))*m
		cx,cy,cz = [cmp(i,0) or 1 for i in (dx,dy,dz)]
		hit=False
		
		x_,y_,z_ = self.world.AIpos
		
		for _ in xrange(10):
			X,Y,Z= x+dx/10,y+dy/10,z+dz/10
			for coor in [i for i in (planes.keys()+items.keys()) if
				cmp(i[0+(cx<0)],x)*cx>0 and 
				cmp(i[2+(cy<0)],y)*cy>0 and 
				cmp(i[4+(cz<0)],z)*cz>0 or True]:
				x1,x2,y1,y2,z1,z2 = coor
				if coor in items:
					x1+=x_
					x2+=x_
					y1+=y_
					y2+=y_
					z1+=z_
					z2+=z_
				# write([round(i,2) for i in (X,x, Y,y, Z,z)])
				# write(y,0,Y,y<=0<=Y)
				if (x<=x1<=X or x<=x2<=X or x1<=X<=x2 or x>x1>X or x>x2>X or x1>X>x2) and \
				   (y<=y1<=Y or y<=y2<=Y or y1<=Y<=y2 or y>y1>Y or y>y2>Y or y1>Y>y2) and \
				   (z<=z1<=Z or z<=z2<=Z or z1<=Z<=z2 or z>z1>Z or z>z2>Z or z1>Z>z2):
					# write(coor,_)
					if coor in items and not items[coor].taken:
						hit=items[coor]
					elif coor in planes and isinstance(planes[coor],Door):
						hit=planes[coor]
					else:
						hit=None
						break
			if hit is not False:
				# write("HIT",hit,coor)
				break
			x,y,z=X,Y,Z
		if hit is not None and hit is not False:
			if isinstance(hit,Door):
				hit.change()
			else:
				hit.delete()
				hit.taken=True
	
	def on_mouse_release(self, x, y, but, mod):
		pass
	
	def on_mouse_motion(self, x, y, dx, dy):
		x, y = self.rotation
		if self.back:
			m = .125
			x, y = x + dx * m, y + dy * m
			x=max(-180,min(180,x))
		else:
			m = .25
			x, y = x + dx * m, y + dy * m
			y = max(-90, min(90, y))
			if x>180:x-=360
			elif x<-180: x+=360
		self.rotation = (x, y)
	
	def on_key_press(self, key, mod):
		if mod & K.MOD_CTRL:
			self.speed = 5
		elif mod & K.MOD_ALT:
			self.speed = 0.75
		elif mod ^ K.MOD_CTRL ^ K.MOD_ALT:
			self.speed = 3
		if key == K.R:
			self.position = self.world.start[:3]
			if mod & K.MOD_SHIFT:
				self.rotation = self.world.start[-1]
			self.speed = 3
			self.world.putverts()
		if key == K.X:
			self.front = self.rotation[:]
			self.start = self.front
			self.back = True
		if key == K.UP:
			self.motion[1]-=1
		if key == K.DOWN:
			self.motion[1]+=1
		if key == K.LEFT:
			self.motion[0]-=1
		if key == K.RIGHT:
			self.motion[0]+=1
		if key == K.SPACE:
			a = self.world.items.keys()
			self.world.items[a[0]].v.delete()
		if key == K.ESCAPE:
			pyglet.app.exit()
		print self.motion+["R"*(key==K.R),"X"*self.back]
		# print "Press:","Shift" if (mod&K.MOD_CTRL) else "     ", "5" if self.speed-2 else " "

	def on_key_release(self, key, mod):
		if mod & K.MOD_CTRL:
			self.speed = 5
		elif mod & K.MOD_ALT:
			self.speed = 0.75
		elif mod ^ K.MOD_CTRL ^ K.MOD_ALT:
			self.speed = 3
		if key == K.X:
			self.rotation = self.front
			self.back = False
		if key == K.UP:
			self.motion[1]+=1
		if key == K.DOWN:
			self.motion[1]-=1
		if key == K.LEFT:
			self.motion[0]+=1
		if key == K.RIGHT:
			self.motion[0]-=1
		print self.motion+["R"*(key==K.R),"X"*self.back]
		# print self.motion+[key==K.R,key==K.X]
		# print "     :","Shift" if (mod&K.MOD_CTRL) else "     ", "5" if self.speed-2 else " "

	def run(self, dt):
		x,y,z = self.position
		rx,ry = self.rotation
		mx,mz = self.motion
		speed = self.speed
		Planes= self.world.planes
		h     = self.Height
		
		global so,sn
		a=b=c=d=""
		
		dx=0
		dy=dt*-2
		dz=0
		
		mdeg = math.degrees(math.atan2(mz,mx))
		mrad = math.radians(mdeg+rx)
		Mx = math.cos(mrad)
		Mz = math.sin(mrad)
		if mx or mz:
			dx=speed*dt*Mx
			dz=speed*dt*Mz
		
		#Collision within horizontal ranges
		walls = {p:Planes[p] for p in Planes
			if vertColl(y,h,*p[2:4]) and 
			(((0<=(p[0+(dx<0)]-x)*(1 if dx>0 else -1)<=0.3) and p[4]<=z<=p[5] and 
				(not Planes[p].x or Planes[p].x and Planes[p].z)) or
			 ((0<=(p[4+(dz<0)]-z)*(1 if dz>0 else -1)<=0.3) and p[0]<=x<=p[1] and 
				(not Planes[p].z or Planes[p].x and Planes[p].z)) or
			 (isinstance(Planes[p],Corner)))}
		a="HCol (%s)"%",".join("%s:%s"%(p,walls[p]) for p in walls) if walls else ""
		for coor in walls:
			# print coor
			dx,dy,dz = walls[coor].collision(dt,x,y,z,dx,dy,dz,coor,walls[coor])
		
		slopes = {p:Planes[p] for p in Planes
			if vertIn(y,h,*p[2:4]) and any((Planes[p].x,Planes[p].y,Planes[p].z)) and 
			p[0]<=x<=p[1] and p[4]<=z<=p[5]}
		b="HIn (%s)"%",".join("%s:%s"%(p,slopes[p]) for p in slopes) if slopes else ""
		for coor in slopes:
			dx,dy,dz = slopes[coor].inside(dt,speed,x,y,z,dx,dy,dz,coor)
		
		# #Collision within vertical range
		# planes = {p:Planes[p] for p in Planes
			# if (vertColl(y,h,*p[2:4]) or 0<y-p[3]<0.4) and 
			# p[2]!=p[3] and (p[0]==p[1] or p[4]==p[5]) and
			# p[0]-.1<=x<=p[1]+.1 and p[4]-.1<=z<=p[5]+.1}
		# c="VIn (%s)"%",".join("%s:%s"%(p,planes[p]) for p in planes) if planes else ""
		# for coor in planes:
			# dx,dy,dz = planes[coor].inside(dt,x,y,z,dx,dy,dz,coor)
		
		#Gravity Check
		_nograv_ = {p:slopes[p] for p in slopes if 
			(slopes[p].y and (not slopes[p].x or not slopes[p].z))
			and not isinstance(slopes[p],Door)}
			# (not all((slopes[p].x,slopes[p].y,slopes[p].z)))}
			# (not slopes[p].y and slopes[p].x and slopes[p].z)}
		if not _nograv_:
			# print _nograv_
			floors = {p:Planes[p] for p in Planes
				if 0<y-p[3]<0.2 and p[0]<x<p[1] and p[4]<z<p[5] and
				(not Planes[p].y or all((Planes[p].x,Planes[p].y,Planes[p].z)))}
		else: floors = {}
		d="VCol %s"%{"(%s)(% .02f,% .02f)"%(",".join(str(i) for i in p),y,y-p[3]):floors[p] for p in floors} if floors else ""
		# c="VIn (%s)"%",".join("%s:%s"%(p,floors[p]) for p in floors) if floors else ""
		for coor in floors:
			dx,dy,dz = floors[coor].collision(dt,x,y,z,dx,dy,dz,coor,floors[coor])
		
		if not (floors or slopes):
			if not self.fall:
				self.fall=0.25,0.25
			elif self.fall and not walls:
				fx,fz=self.fall
				fx=max(fx-dx,0)
				fz=max(fz-dz,0)
				self.fall=fx,fz
				# write(dx,dz)
			else:
				dx=dz=0
			if self.fall==(0.0,0.0):
				dx=dz=0
		else:
			self.fall=False
		
		# write("% .02f % .02f % .02f"%(dx,dy,dz))
		# write(___,"(%.02f,%.02f,%.02f)"%(x,y,z))
		write(("\n").join(i for i in (a,b,c,d,"(%.02f,%.02f,%.02f)"%(x,y,z)) if i.strip()))
		# write("%.01f,%.01f"%(y,z),a,b,c,d)
		
		x+=dx
		y+=dy
		z+=dz
		
		self.position = [x,y,z]
		
		
		
		x,y,z = self.world.AIpos
		rx,ry = self.world.AIrot
		mot   = self.world.AImot
		
		if mot==1:
			if x<3.5:
				x+=0.5*dt
			else:
				mot=2
		elif mot==2:
			if rx<180:
				rx+=90*dt
			else:
				rx=180
				mot=-1
		elif mot==-1:
			if x>0.5:
				x-=0.5*dt
			else:
				mot=-2
		elif mot==-2:
			if rx>0:
				rx-=90*dt
			else:
				rx=0
				mot=1
		
		self.world.AIpos = [x,y,z]
		self.world.AIrot = (rx,ry)
		self.world.AImot = mot
		
		items = self.world.items
		itmcr = [i for i in items.keys() if any([j%1 for j in i])][0]
		item  = items[itmcr]
		
		x1,x2,y1,y2,z1,z2 = itmcr
		x,y,z = self.world.AIpos
		x1+=x
		x2+=x
		y1+=y
		y2+=y
		z1+=z
		z2+=z
		x,y,z = self.position
		if (x1<=x<=x2 and z1<=z<=z2 or x1>x>x2 and z1>z>z2) \
			and vertColl(y,h,y1,y2) and not item.taken:
			self.position = self.world.start[:-1]
		
		# write(*(round(i,2) for i in (x1,x2,y1,y2,z1,z2,x,y,z)))
		
		# self.world.runAI(self,dt)

class Plane:
	def __init__(self,x=0,y=0,z=0):
		self.x=x
		self.y=y
		self.z=z
	
	def __repr__(self):
		return "P(%s,%s,%s)"%(self.x,self.y,self.z)
	
	def collision(self,dt, x,y,z, dx,dy,dz, coor,plane):
		for i in xrange(3):
			if coor[i*2]==coor[i*2+1]: break
		else:
			X,Y,Z=plane.x,plane.y,plane.z
			if Y:
				if dx*X<0 and 0<=(coor[0+(dx<0)]-x)*(1 if dx>0 else -1)<=0.3: dx=0
				if dz*Z<0 and 0<=(coor[4+(dz<0)]-z)*(1 if dz>0 else -1)<=0.3: dz=0
				if Y and 0<=(coor[2+(dy<0)]-y)*(1 if dy>0 else -1)<=0.3:
					z_=z-coor[4+(X!=Z)]
					sign = -1 if X!=Z else 1
					z_*=sign
					num = (coor[1]-coor[0])*z_
					x_ = coor[1]-num/(coor[5]-coor[4])
					if cmp(x,x_)==X: dy=0
					# write(coor,*[round(i,3) for i in (z_,num,x_,x,dx,dy,dz)])
				# write(coor,X,Y,Z,*[round(i,3) for i in (dx,dy,dz)])
			if X==Z:
				pass
			return [dx,dy,dz]
		if i==0 and 0<=(coor[0+(dx>0)]-x)*(1 if dx>0 else -1)<=0.3: dx=0
		if i==2 and 0<=(coor[4+(dz>0)]-z)*(1 if dz>0 else -1)<=0.3: dz=0
		if i==1: dy=0
		# write(coor,*[round(i,3) for i in (dx,dy,dz)])
		return [dx,dy,dz]
	
	def inside(self,dt,v, x,y,z, mx,my,mz, coor):
		x1,x2,y1,y2,z1,z2 = coor
		X,Y,Z = self.x,self.y,self.z
		dx = x2-x1
		dy = y2-y1
		dz = z2-z1
		
		if X and Z:
			pass
			# x_ = x-x1
			# z_ = z-z1
			
			# ang = math.atan2(mz,mx)+math.atan2(dz,dx)
			# X_ = math.cos(ang)
			# Z_ = math.sin(ang)
			
			# if X!=Z:
				
			
			
			# x_ = x-x1
			# z_ = z-z1
			
			# # rad = math.atan2(dz,dx)
			# # X_ = math.cos(rad)
			# # Z_ = math.sin(rad)
			
			# X_ = 0.+dx/dz
			# Z_ = 0.+dz/dx
			
			# if X==Z:
				# m = 0.-Z/X
			# else:
				# m = 0.+Z/X
			# y = m*x_
			
			# if mx or mz:
				# if X==Z:
					# if y-SQ_2<=z_<=y and (mx>=0 or mz>=0):
						# mx-=X_*dt*v
						# mz-=Z_*dt*v
					# elif y<=z_<=y+SQ_2 and (mx<0 or mz<0):
						# mx+=X_*dt*v
						# mz+=Z_*dt*v
				# else:
					# if y-SQ_2<=z_<=y and (mx>=0 or mz<0):
						# mx+=X_*dt*v
						# mz-=Z_*dt*v
					# elif y<=z_<=y+SQ_2 and (mx<0 or mz>=0):
						# mx-=X_*dt*v
						# mz+=Z_*dt*v
			# write(coor,tuple(round(i,2) for i in (mx,mz,x_,z_,x,z,X_,Z_,X,Z,y,SQ_2,SQ_8)))
			
			
			# z_ = (z-z1-SQ_2)/dz
			# x_ = (x-x1-SQ_2)/dx
			# deg= math.degrees(math.atan2(dx,dz))
			# rad= math.radians(deg)
			# X_ = math.cos(rad)
			# Z_ = math.sin(rad)
			# cx = cmp(mx,0)
			# cz = cmp(mz,0)
			# if X==Z: D = 1-x_-z_
			# else:    D = x_-z_
			# if -SQ_8<=D<=SQ_8 and (mx or mz):
				# mx-=X_*dt*v*cx*(cx*X>0)
				# mz-=Z_*dt*v*cz*(cz*Z>0)
			
			# write(coor,tuple(round(i,2) for i in (mx,mz,cx,cz,x_,z_,x,z,X_,Z_,D)))
		
		elif X and Y:
			if X!=Y: x_=x2-x
			else:    x_=x-x1
			num = dy*x_
			y_ = num/dx+y1
			D = y-y_
			if not(-.3<=D<=.3):
				my = dt*-2.
			elif mx: 
				sign = -1 if X!=Y else 1
				my = sign*mx/dx*dy
				# write(Y,X,sign,mx,dx,dy,my)
			elif 0<=D: 
				my = y_+.3-y
			# elif -.2<D<0: 
				# my = y_-.2-y
			else:
				my=0
		
		elif Y and Z:
			if Z!=Y: z_=z2-z
			else:    z_=z-z1
			num = dy*z_
			y_ = y2-num/dz
			D = y-y_
			if not(-.3<=D<=.3):
				mz=mx=0
				my = dt*-2.
			elif mz: 
				sign = 1 if Z!=Y else -1
				my = sign*mz/dz*dy
				# write(Y,Z,sign,mz,dz,dy,my)
			elif 0<=D:
				my = y_+.3-y
			# elif -2.<D<0: 
				# my = y-y_+.2
			else:
				my=0
			# write("% .3f % .3f % .3f % .3f % .3f % .3f" % (y,z,y_,z_,D,my))
		
		return [mx,my,mz]

class Door:
	def __init__(self,closed,open,isOpen=False):
		self.x=self.z=0
		self.y=1
		self.closedAt=closed
		self.openAt=open
		self.open=isOpen
	
	def __repr__(self):
		return "Door(%s,%s,%s)" % (self.closedAt,self.openAt,self.open)
	
	def collision(self,dt, x,y,z, mx,my,mz, coor,plane):
		x1,x2,y1,y2,z1,z2 = coor
		isO = self.open
		cls = self.closedAt
		opn = self.openAt
		if "X1"==(opn if isO else cls) and mx>0 and x+mx>x1-.2:
			mx=x1-x-.2
		elif "X2"==(opn if isO else cls) and mx<0 and x+mx<x2+.2:
			mx=x2-x+.2
		if "Z1"==(opn if isO else cls) and mz>0 and z+mz>z1-.2:
			mz=z1-z-.2
		elif "Z2"==(opn if isO else cls) and mz<0 and z+mz<z2+.2:
			mz=z2-z+.2
		return [mx,my,mz]
	
	def inside(self,dt,v, x,y,z, mx,my,mz, coor):
		x1,x2,y1,y2,z1,z2 = coor
		isO = self.open
		cls = self.closedAt
		opn = self.openAt
		if "X1"==(opn if isO else cls) and mx<0 and x+mx<x1+.2:
			mx=x1-x+.2
		elif "X2"==(opn if isO else cls) and mx>0 and x+mx>x2-.2:
			mx=x2-x-.2
		if "Z1"==(opn if isO else cls) and mz<0 and z+mz<z1+.2:
			mz=z1-z+.2
		elif "Z2"==(opn if isO else cls) and mz>0 and z+mz>z2-.2:
			mz=z2-z-.2
		return [mx,my,mz]
	
	def change(self):
		self.open = not self.open
		
		global window
		window.world.door.delete()
		doorcoords=((2,2,0, 2,2,1, 2,3,1, 2,3,0),
					(2,2,1, 3,2,1, 3,3,1, 2,3,1))
		window.world.doorbatch.add(4, GL_QUADS, window.world.texgrp,
			('v3f',doorcoords[window.world.planes[(2,3,2,3,0,1)].open]),
			('t2f',(0,0,50,0,50,50,0,50)))

class Corner:
	def __init__(self,r=SQ_8):
		self.r=r
		self.x=self.y=self.z=0
	
	def __repr__(self):
		return "Corner(%.02f)"%self.r
	
	def collision(self,dt, x,y,z, dx,dy,dz, coor,plane):
		X=coor[0]
		Z=coor[5]
		r = self.r
		if (dx>0 and (x<=X-r<=x+dx or x<=X+r<=x+dx or x>X-r>x+dx or x>X+r>x+dx) or
		    dx<0 and (x+dx<=X+r<=x or x+dx<=X-r<=x or x+dx>X+r>x or x+dx>X-r>x)) and\
				(X-r<=x+dx<=X+r or X-r<=x<=X+r) and\
		   (dz>0 and (z<=Z-r<=z+dz or z<=Z+r<=z+dz or z>Z-r>z+dz or z>Z+r>z+dz) or
		    dz<0 and (z+dz<=Z+r<=z or z+dz<=Z-r<=z or z+dz>Z+r>z or z+dz>Z-r>z)) and\
				(Z-r<=z+dz<=Z+r or Z-r<=z<=Z+r):
			dx=0
			dz=0
			# write(coor,*(round(i,2) for i in (x,y,z,dx,dy,dz)))
		return [dx,dy,dz]

class Item:
	def __init__(self,ID,edges,texes,grp,batch,isitem=True):
		self.ID=ID
		self.taken=False
		self.edges=edges
		verts=edge2vert(edges)
		if isitem:
			self.verts=((.1,.25,-.2, .2,.25,-.1, .2,.25,.1, .1,.25,.2, -.1,.25,.2, -.2,.25,.1, -.2,.25,-.1, -.1,.25,-.2),
						(-.1,.25,-.2, .1,.25,-.2, -.1,-.25,-.2, .1,-.25,-.2))
			self.texes=((51,51, 51,75, 51,100, 75,100, 100,100, 100,75, 100,51, 75,51),
						(51,51, 51,100, 100,100, 100,51))
			self.modes=(GL_POLYGON,GL_QUADS)
		else:
			self.verts=[verts]
			self.texes=[texes]
			self.modes=(GL_QUADS,)
		self.batch=batch
		self.group=grp
		
		self.v=[self.batch.add(len(self.verts[i])/3,self.modes[i],self.group,
			('v3f/static',self.verts[i]),
			('t2f/static',self.texes[i])) for i in xrange(len(self.verts))]
	
	def delete(self):
		l = len(self.v)
		for i in xrange(l):
			self.v[i].delete()

class World:
	def __init__(self):
		self.batch = pyglet.graphics.Batch()
		self.itmbt = [pyglet.graphics.Batch() for _ in xrange(2)]
		self.AIpos = [0.5,.25,0.5]
		self.AIrot = (0.,0.)
		self.AImot = -1
		self.texgrp = TextureGroup(pyglet.image.load('texture.png').get_texture(True))
		self.putverts()
		self.start = [1,-.5,2,(0.,0)]
		# self.start = [3.75,1.1,0.55,(0.,-90.)]
	
	def putverts(self):
		self.planes = {(0,3,0,0,0,3):Plane(),
					(0,3,-1,-1,0,3):Plane(),
					(3,4,-1,-1,1,3):Plane(),
					(4,6,-1,-1,0,3):Plane(),
					(0,3,1,1,0,3):Plane(),
					(4,5,1,1,2,3):Plane(),
					(3,5,1,1,1,2):Plane(),
					(0,0,-1,3,0,3):Plane(),
					(0,5,-1,2,0,0):Plane(),
					(0,2,2,3,0,0):Plane(),
					(0,5,-1,3,3,3):Plane(),
					(1,3,0,1,1,1):Plane(),
					(1,3,0,1,2,2):Plane(),
					(1,1,0,1,1,2):Plane(),
					(3,3,0,1,1,2):Plane(),
					(0,1,2,2,2,3):Plane(),
					(1,2,2,2,2.5,3):Plane(),
					(0,4,2,2,0,1):Plane(),
					(2,4,2,2,1,3):Plane(),
					(2,5,2,2,-1,0):Plane(),
					# (2,3,2,3,0,1):Plane(0,-1,1),
					(3,4,2,3,1,2):Plane(1,0,-1),
					(3,4,2,3,2,3):Plane(1,0,1),
					(4,5,1,2,0,1):Plane(0,1,1),
					(4,4,1,2,0,1):Plane(),
					# (1,2,1,1.2,1,1):Plane(),
					(2,2,1,2,1,2):Plane(),
					# (0,1,1,1.2,2,2):Plane(),
					(1,1,1,2,1,2):Plane(),
					(0,1,1,2,1,2):Plane(0,-1,1),
					(1,2,1,2,1,2):Plane(0,1,1),
					(3,4,-1,0,0,1):Plane(1,-1,0),
					(3,4,-1,0,1,1):Plane(),
					(3,3,-1,-.8,0,1):Plane(),
					(3,4,0,1,2,3):Plane(1,1,0),
					(1.01,1.01,0,1,1.01,1.01):Corner(),
					(1.01,1.01,0,1,1.99,1.99):Corner(),
					(2,3,2,3,0,1):Door("X1","Z2")
					}
		verts = (0,0,0, 0,0,3, 3,0,3, 3,0,0, #bottom
			 0,-1,0, 0,-1,3, 6,-1,3, 6,-1,0,
			 
			 0,1,0, 0,1,3, 3,1,3, 3,1,0, #top
			 4,1,2, 4,1,3, 5,1,3, 5,1,2,
			 4,1,1, 4,1,2, 5,1,2, 5,1,1,
			 3,1,1, 3,1,2, 4,1,2, 4,1,1,
			 0,2,2, 1,2,2, 1,2,3, 0,2,3,
			 1,2,2.5, 2,2,2.5, 2,2,3, 1,2,3,
			 0,2,0, 1,2,0, 1,2,1, 0,2,1,
			 1,2,0, 2,2,0, 2,2,1, 1,2,1,
			 2,2,0, 3,2,0, 3,2,1, 2,2,1,
			 3,2,0, 4,2,0, 4,2,1, 3,2,1,
			 2,2,1, 4,2,1, 4,2,3, 2,2,3,
			 2,2,0, 3,2,0, 3,2,-1,2,2,-1,
			 3,2,0, 4,2,0, 4,2,-1,3,2,-1,
			 4,2,0, 5,2,0, 5,2,-1,4,2,-1,
			 
			 5,-1,0, 0,-1,0, 0,0,0, 5,0,0,
			 5,0,0, 0,0,0, 0,1,0, 5,1,0,
			 5,1,0, 0,1,0, 0,2,0, 5,2,0,
			 0,0,0, 0,0,3, 0,1,3, 0,1,0,
			 0,1,0, 0,1,3, 0,2,3, 0,2,0,
			 0,0,3, 5,0,3, 5,1,3, 0,1,3,
			 0,1,3, 5,1,3, 5,2,3, 0,2,3,
			 3,0,3, 3,0,2, 4,1,2, 4,1,3,
			 3,0,2, 1,0,2, 1,1,2, 3,1,2,
			 1,0,2, 1,0,1, 1,1,1, 1,1,2,
			 1,0,1, 3,0,1, 3,1,1, 1,1,1,
			 0,1,1, 1,1,1, 1,2,2, 0,2,2,
			 4,1,1, 5,1,1, 5,2,0, 4,2,0,
			 1,1,2, 2,1,2, 2,2,1, 1,2,1,
			 3,0,1, 3,0,0, 4,-1,0, 4,-1,1,
			 3,0,1, 3,0,2, 3,1,2, 3,1,1)
		texes = (50,0,50,50,100,50,100,0)*2+(0,50,50,50,50,100,0,100)*14+\
			(0,0,50,0,50,50,0,50)*16
		self.batch.add(len(verts)/3,GL_QUADS,self.texgrp,
			('v3f/static',verts),
			('t2f/static',texes))
		# print edge2vert((3,3,2,3,0,1))
		red = (51,51,51,100,100,100,100,51)
		itemedges=[(-.25,.25,-.125,.125,-.25,.25)]
		itemtexes=[red]*2
		self.items={}
		for i in xrange(len(itemedges)):
			self.items[itemedges[i]]=Item(i,itemedges[i],itemtexes[i]*6,self.texgrp,self.itmbt[i],False)
		
		self.doorcoords=((2,2,0, 2,2,1, 2,3,1, 2,3,0),
					(2,2,1, 3,2,1, 3,3,1, 2,3,1))
		self.doorbatch=pyglet.graphics.Batch()
		self.door=self.doorbatch.add(4, GL_QUADS, self.texgrp,
			('v3f',self.doorcoords[self.planes[(2,3,2,3,0,1)].open]),
			('t2f',(0,0,50,0,50,50,0,50)))
		
		# aiedges=[
		
		# self.AI = 
		
	
	def runAI(self, win, dt):
		pass
		# x,y,z= self.AIpos
		# rot  = self.AIrot
		# mot  = self.AImot
		
		# if mot==-1:
			# if x>1.5:
				# x-=0.5*dt
			# else:
				# mot=0
		# elif mot==1:
			# if x<3.5:
				# x+=0.5*dt
			# else:
				# mot=0
		
		# if mot==0:
			# if -180<=rot<=180:
				# rot+=180*dt
			# else:
				# rot=180*(cmp(rot,0))
		
		# self.AIpos = x,y,z
		# self.AIrot = rot
		# self.AImot = mot



# class before:
	# def __init__(self,win):
		# self.batch=pyglet.graphics.Batch()
		# self.time=0
		# self.clock=pyglet.text.Label('--:--:--', 
			# font_name='Consolas', 
			# font_size=50,
			# x=win.width//2, y=win.height//2,
			# anchor_x='center', anchor_y='center')
	
	# def run(self,dt):
		# self.time+=dt
		# if self.time>=5: self.end()
		# else:
			# str = "5:59:5%d" % (5+self.time//1)
			# self.clock.text=str
	
	# def end(self):
		# pass

# def run(self, dt):
	# window.run(dt)

glEnable(GL_CULL_FACE)
window = Window(800,600,"THE SEARCH")
window.set_exclusive_mouse(True)
window.set_location(7*window.screen.width/24 - window.width/2, window.screen.height/2 - window.height/2)
# b=window.world.batch
# gm=b.__dict__['group_map']
# gm[gm.keys()[0]][(('v3f/static','t2f/static'),7,False)]
pyglet.clock.schedule_interval(window.run,1./60)
pyglet.app.run()