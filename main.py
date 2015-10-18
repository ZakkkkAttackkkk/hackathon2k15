#!/usr/bin/env python
import pyglet
from random import randint as rand
from math import ceil
from pyglet import resource
from pyglet.window import key as K
from pyglet.gl import *
from pyglet.graphics import *
from pyglet.sprite import Sprite

resource.path += ["Sprites"]
resource.reindex()

###############################################################################
# 
# Define the Player Classes
# 
###############################################################################

class Character:
	def __init__(self,*a):
		pass
	def update(self,*a):
		pass
	def draw(self,*a):
		pass
	def move(self,*a):
		pass
	def act(self,*a):
		pass

class Player(Character):
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.mode = '_'
		self.texes = [resource.image("MC/"+fn+".png") for fn in "idle;back;back1;back2;front;front1;front2;run1;run2;run3".split(';')] \
				+ [resource.image("MC/"+fn+".png",flip_x=True) for fn in "run1;run2;run3".split(";")]
		for _ in  self.texes:
			_.anchor_x = _.width//2
			_.anchor_y = _.height//2
		self.texes = [[self.texes[0]],self.texes[1:4],self.texes[4:7],self.texes[7:10],self.texes[10:]]
		self.texnum = 0.0
	def update(self,dt):
		self.texnum=(self.texnum+dt*5)%3
		if self.mode!='_':
			X = self.x + dt*100*(-1 if self.mode=='l' else (self.mode=='r'))
			Y = self.y + dt*100*(-1 if self.mode=='d' else (self.mode=='u'))
			if not(X<28 or ((32<=X<124 or 132<=X<224) and (28<=Y<200)) or 228<=X):
				self.x = int(X)
			if not(Y<16 or ((32<=X<124 or 132<=X<224) and (28<=Y<200)) or 216<=Y):
				self.y = int(Y)
			write(self.x,self.y)
	def draw(self):
		ind = "_udrl".index(self.mode)
		self.texes[ind][int(ind and self.texnum)].blit(self.x,self.y)
	def move(self,d):
		self.mode = d

class Voter(Character):
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.mode = 0
		self.texes = [resource.image("voters/"+fn+".png") for fn in "sitblack;sitwhite".split(';')]
		for _ in  self.texes:
			_.anchor_x = _.width//2
			_.anchor_y = _.height//2
		self.life = 10.0
	def update(self,dt):
		if self.mode and self.life>0: self.life -= dt*10*(1,2,3,5,10)[self.mode]
		else: self.life += dt*5
	def draw(self):
		self.texes[self.life>0].blit(self.x,self.y)
	def act(self,a):
		self.mode = a

class Buyer(Character):
	def __init__(self,x,y,c,l):
		self.gx = x
		self.gy = y
		self.x = x//2 if x!=1 else rand(0,1)
		self.y = 240
		self.mode = -3
		self.texes = [resource.image("sellers/"+"bry"[c]+fn+".png") for fn in "cry;front;frontwalk1;frontwalk2;hit;walk1;walk2;".split(';')]\
				+ [resource.image("sellers/"+"bry"[c]+fn+".png",flip_x=True) for fn in "walk1;walk2;".split(';')]
		for _ in  self.texes:
			_.anchor_x = _.width//2
			_.anchor_y = _.height//2
		self.life = (1,2,3,5,10)[l]
		self.texnum = 0.0
	def update(self,dt):
		self.texnum = (self.texnum+dt*5)%2
		if self.mode==-3 and self.y<=200:
			self.mode = -2
			self.texes[1].blit(self.x,self.y)
		elif self.mode==-2:
			if self.x==self.gx: self.mode==-1
			else: self.x += dt*5*cmp(self.gx,self.x)
		elif self.mode==-1:
			if self.y==self.gy: self.mode==0
			else: self.y -= dt*5
		elif self.mode and self.life>0: self.life -= dt*10*(1,2,3,5,10)[self.mode]
		else: self.life += dt*5
	def draw(self):
		if self.mode in (-3,-1):
			self.texes[2+int(self.texnum)].blit(self.x,self.y)
		elif self.mode < 0:
			self.texes[5+int(self.texnum)+3*(self.gx<self.x)].blit(self.x,self.y)
		elif self.mode==0:
			self.texes[(1,7,10)[self.gx]].blit(self.x,self.y)
		elif self.mode==1:
			self.texes[4 if self.life>0 else 0].blit(self.x,self.y)
	def act(self,a):
		self.mode = a


###############################################################################
# 
# Define the Screen Classes
# 
###############################################################################

class Screen:
	def __init__(*a):
		pass
	def update(*a):
		pass
	def draw(*a):
		pass
	def mdrag(*a):
		pass
	def mdown(*a):
		pass
	def mup(*a):
		pass
	def kdown(*a):
		pass
	def kup(*a):
		pass

class MainMenu(Screen):
	def __init__(self):
		self.batch = Batch()
		self.play = pyglet.text.Label("[play]",height=16,width=200,x=128,y=96,anchor_x="center",anchor_y="top",align="center",font_size=12.0,color=(0,0,0,255),batch=self.batch)
		self.exit = pyglet.text.Label("[exit]",height=16,width=200,x=128,y=48,anchor_x="center",anchor_y="top",align="center",font_size=12.0,color=(0,0,0,255),batch=self.batch)
		self.curbut = '_'
		self.bgimg = pyglet.image.load("./Sprites/sample.png")
		self.bgimg.anchor_x=128
		self.bgimg.anchor_y=128
		self.texgrp = TextureGroup(self.bgimg.get_texture(True,True))
		self.batch.add(4,GL_QUADS,self.texgrp,
			('v2f/static',(0,0, 255,0, 255,255, 0,255)),
			('t2f/static',(0,0, 255,0, 255,255, 0,255)))
	def update(self,dt):
		self.play.text = "["+("PLAY" if self.curbut=="p" else "play")+"]"
		self.play.color = (0,255,0,255) if self.curbut =="p" else (0,0,0,255)
		self.exit.text = "["+("EXIT" if self.curbut=="x" else "exit")+"]"
		self.exit.color = (255,0,0,255) if self.curbut =="x" else (0,0,0,255)
	def draw(self):
		glLoadIdentity()
		self.batch.draw()
	def mdrag(self,x,y,dx,dy,but,mod):
		x+=dx;y+=dy
		write(x,y)
		if but and 156<=x<=356:
			if self.curbut.lower()=='x':
				if 64<=y<=128: self.curbut='x'
				else: self.curbut='X'
			elif self.curbut.lower()=='p':
				if 160<=y<=224: self.curbut='p'
				else: self.curbut='P'
		else:
			self.curbut = self.curbut.upper()
	def mdown(self,x,y,but,mod):
		if but and 156<=x<=356:
			self.curbut = 'x' if 64<=y<=128 else 'p' if 160<=y<=224 else '_'
		else:
			self.curbut = '_'
	def mup(self,x,y,but,mod):
		if self.curbut!="_":
			global screens
			if self.curbut=="x": screens.pop()
			elif self.curbut=="p": screens+=[MainGame()]
			self.curbut = "_"

class MainGame(Screen):
	def __init__(self):
		self.batch = Batch()
		self.voters = [Voter(42+16*(_%5)+106*((_%10)>4),48+28*(_/10)) for _ in xrange(50)]
		self.buyers = []
		self.player = Player(128,16)
		self.time = 63.0
		self.clock = pyglet.text.Label("00",height=50,width=70,x=128,y=240,anchor_x="center",anchor_y="center",align="center",font_size=40.0,color=(0,0,0,255))
		self.countdown = pyglet.text.Label("3",height=230,width=230,x=128,y=128,anchor_x="center",anchor_y="center",align="center",font_size=150.0,color=(0,0,0,255))
		self.bgimg = pyglet.image.load("./Sprites/background.png")
		self.bgimg.anchor_x=128
		self.bgimg.anchor_y=128
		self.texgrp = TextureGroup(self.bgimg.get_texture(True,True))
		self.batch.add(4,GL_QUADS,self.texgrp,
			('v2f/static',(0,0, 255,0, 255,255, 0,255)),
			('t2f/static',(0,0, 511,0, 511,511, 0,511)))
		self.confirm = False
		self.labcnfm = pyglet.text.Label("Quit? \n[Enter to confirm]",height=100,width=200,x=128,y=128,anchor_x="center",anchor_y="center",align="center",font_size=25.0,color=(0,0,0,255),multiline=True)
	def update(self,dt):
		if not self.confirm:
			self.time-=dt
			if self.time>60:
				self.countdown.text = str(int(ceil(self.time)%10))
			elif self.time>0:
				self.clock.text = str(int(ceil(self.time)))
				self.player.update(dt)
				for v in self.voters:
					v.update(dt)
			else:
				global screens
				screens.pop()
				screens+=[Win()]
	def draw(self):
		self.batch.draw()
		for v in self.voters:
			v.draw()
		if self.confirm:
			self.labcnfm.draw()
		elif self.time>60:
			self.countdown.draw()
		else:
			self.clock.draw()
		self.player.draw()
	def kdown(self,ch,mod):
		if not self.confirm:
			if ch==K.P:
				global screens
				screens+=[Paused()]
			elif ch==K.Q and self.time<=60:
				self.confirm = True
			else:
				try:
					ind = [K.UP,K.DOWN,K.LEFT,K.RIGHT].index(ch)
					self.player.move("udlr"[ind])
				except ValueError:
					pass
		else:
			if ch==K.ENTER:
				global screens
				screens.pop()
			else:
				self.confirm = False
	def kup(self,ch,mod):
		if not self.confirm:
			if ch in (K.UP,K.DOWN,K.LEFT,K.RIGHT):
				self.player.move('_')

class Paused(Screen):
	def __init__(self):
		self.text = pyglet.text.Label("PAUSED",height=50,width=150,x=128,y=128,anchor_x="center",anchor_y="center",align="center",font_size=45.0,color=(255,255,255,255))
	def draw(self):
		self.text.draw()
	def kdown(self,ch,mod):
		if ch==K.P:
			global screens
			screens.pop()

class Win(Screen):
	def __init__(self):
		self.text = pyglet.text.Label("You Win!",height=50,width=150,x=128,y=128,anchor_x="center",anchor_y="center",align="center",font_size=25.0,color=(255,255,255,255))
	def draw(self):
		self.text.draw()
	def kdown(self,ch,mod):
		global screens
		screens.pop()

class Lose(Screen):
	def __init__(self):
		self.text = pyglet.text.Label("You Lose :(",height=50,width=150,x=128,y=128,anchor_x="center",anchor_y="center",align="center",font_size=25.0,color=(255,255,255,255))
	def draw(self):
		self.text.draw()
	def kdown(self,ch,mod):
		global screens
		screens.pop()
		screens.pop()

class FixedResolutionViewport(object):
	def __init__(self, window, width, height, filtered=False):
		self.window = window
		self.width = width
		self.height = height
		self.texture = pyglet.image.Texture.create(width, height, 
			rectangle=True)

		if not filtered:
			# By default the texture will be bilinear filtered when scaled
			# up.  If requested, turn filtering off.  This makes the image
			# aliased, but is more suitable for pixel art.
			glTexParameteri(self.texture.target, 
				GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(self.texture.target, 
				GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	
	def begin(self):
		glViewport(0, 0, self.width, self.height)
		self.set_fixed_projection()

	def end(self):
		buffer = pyglet.image.get_buffer_manager().get_color_buffer()
		self.texture.blit_into(buffer, 0, 0, 0)

		glViewport(0, 0, self.window.width, self.window.height)
		self.set_window_projection()

		aspect_width = self.window.width / float(self.width)
		aspect_height = self.window.height / float(self.height)
		if aspect_width > aspect_height:
			scale_width = aspect_height * self.width
			scale_height = aspect_height * self.height
		else:
			scale_width = aspect_width * self.width
			scale_height = aspect_width * self.height
		x = (self.window.width - scale_width) / 2
		y = (self.window.height - scale_height) / 2
		
		glClearColor(0, 0, 0, 1)
		glClear(GL_COLOR_BUFFER_BIT)
		glLoadIdentity()
		glColor3f(1, 1, 1)
		self.texture.blit(x, y, width=scale_width, height=scale_height)
	
	def set_fixed_projection(self):
		# Override this method if you need to change the projection of the
		# fixed resolution viewport.
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)
		glMatrixMode(GL_MODELVIEW)

	def set_window_projection(self):
		# This is the same as the default window projection, reprinted here
		# for clarity.
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
		glMatrixMode(GL_MODELVIEW)

class Window(pyglet.window.Window):
	def __init__(self,*args,**kwargs):
		super(Window, self).__init__(*args, **kwargs)
		self.texgrp = TextureGroup("texture.png")
	def on_draw(self):
		viewport.begin()
		self.clear()
		global screens
		if screens: screens[-1].draw()
		viewport.end()
	def on_mouse_press(self,*a):
		if screens: screens[-1].mdown(*a)
	def on_mouse_release(self,*a):
		if screens: screens[-1].mup(*a)
	def on_mouse_drag(self,*a):
		if screens: screens[-1].mdrag(*a)
	def on_key_press(self,*a):
		if screens: screens[-1].kdown(*a)
	def on_key_release(self,*a):
		if screens: screens[-1].kup(*a)

###############################################################################
# 
# Create the window and define the updating function
# 
###############################################################################

window = Window(512,512,"Bribe Watch");

viewport = FixedResolutionViewport(window, 
	256, 256, filtered=False)

screens = [MainMenu()]

so=sn=""
def write(*s):
	global so,sn,out
	sn = " ".join(str(_) for _ in s)
	if so!=sn:
		print sn
		so=sn


def update(dt):
	if screens:
		screens[-1].update(dt)
	else:
		pyglet.app.exit()

pyglet.clock.schedule_interval(update, 1/60.)

pyglet.app.run()