#!/usr/bin/python

#import rlcompleter
#import readline
from optparse import OptionParser
import ConfigParser

#readline.parse_and_bind("tab: complete")
from pysvg.turtle import Turtle, Vector
from pysvg.structure import svg
from pysvg.structure import * 
from pysvg.text import *
from pysvg.linking import *

global opt

class construct:
	pass

style = ''


class box:
	def __init__(self,opt):
		self.faces = []
		self.opt = opt
		w = opt.width * opt.mult
		d = opt.depth * opt.mult
		l = opt.length * opt.mult
		print 'Make box'
		self.faces.append(face('TOP',opt,w,d))
		self.faces.append(face('LEFT',opt,l,d))
		self.faces.append(face('BOTTOM',opt,w,d))
		self.faces.append(face('RIGHT',opt,l,d))
		self.faces.append(face('BACK',opt,w,l))
		self.faces.append(face('FRONT',opt,w,l))
		self.inset()
		self.edge_type()	
		self.layout()

	def inset(self):
		t = self.opt.thickness * self.opt.mult
		i = [t,t,t,t,0,0,0]
		self.faces[0].inset(i[4],i[6],i[5],i[6]) #TOP
		self.faces[1].inset(i[4],i[2],i[5],i[0]) #LEFT
		self.faces[2].inset(i[6],i[6],i[5],i[6]) #BOTTOM
		self.faces[3].inset(i[4],i[0],i[5],i[2]) #RIGHT
		self.faces[4].inset(i[0],i[3],i[2],i[1]) #BACK
		self.faces[5].inset(i[2],i[3],i[0],i[1]) #FRONT

        def slot_length(self,h,w,l):
                pass
        
	def edge_type(self):
                self.faces[0].edge_type(2,2,2,2) #TOP
		self.faces[1].edge_type(2,1,2,1) #LEFT
		self.faces[2].edge_type(2,2,2,2) #BOTTOM
		self.faces[3].edge_type(2,1,2,1) #RIGHT
		self.faces[4].edge_type(1,1,1,1) #BACK
		self.faces[5].edge_type(1,1,1,1) #FRONT

	def __str__(self):
		txt = 'Box \n' 
		for i in self.faces:
			txt = txt + i.__str__()
		return txt
	
	def gen(self,svg):
		for i in self.faces:
			i.gen(svg)

	def layout(self):
		m = opt.mult
		width = self.opt.width * m 
		length = self.opt.length * m 
		depth = self.opt.depth * m 
		clearance = self.opt.clearance * m 
		# layout the sections in an unfolded cube
		sx = 40
		sy = 40
		x = 0 
		for i in range(4):
			self.faces[i].sx = sx + x
			self.faces[i].sy = sy +  2 * clearance + length 
			x = x + self.faces[i].width + 2*clearance
		self.faces[4].sx = sx + length + width + 4 * clearance
		self.faces[4].sy = sy  
		self.faces[5].sx = sx + length + width + 4 * clearance
		self.faces[5].sy = sy + length + 4*clearance + depth #+ + depth + width +  4 * clearance 


			
class face:
	def __init__(self,name,opt,width,length):
		self.x = 0 
		self.y = 0 
		self.sx = 0 
		self.sy = 0 
		self.opt = opt
		self.name = name
		self.length = length
		self.width = width
		self.edges = []
		self.add_edges(opt,width,length)
		self.path_data = []
		#self.turtle = Turtle(fill="lightgrey")

	def inset(self,a,b,c,d):
		self.edges[0].inset = a
		self.edges[1].inset = b
		self.edges[2].inset = c
		self.edges[3].inset = d

	def edge_type(self,a,b,c,d):
		self.edges[0].edge_type = a
		self.edges[1].edge_type = b
		self.edges[2].edge_type = c
		self.edges[3].edge_type = d

	def add_edges(self,opt,width,length):
		self.edges.append(edge(opt,width))
		self.edges.append(edge(opt,length))
		self.edges.append(edge(opt,width))
		self.edges.append(edge(opt,length))

	def __str__(self):
		txt = self.name + ' : ' + str(self.length)+'x'+str(self.width) + '\n'
		for i in self.edges:
			txt = txt + i.__str__()	
		txt = txt + str(self.path_data)
		return txt
	
	def gen(self,svg):
		# outlines 
		if self.opt.outline:
			t = Turtle(fill="lightgrey") 
			t.moveTo(Vector(self.sx,self.sy))
			t.penDown()
			for i in self.edges:
				p = i.basic(t)
				t.right(90)	
			t.finish()
			
			for i in t.getSVGElements():
				svg.addElement(i)

		## fill
		# bodge up the insets 
		self.edges[0].length = self.edges[0].length - self.edges[1].inset -  self.edges[3].inset
		self.edges[1].length = self.edges[1].length - self.edges[0].inset -  self.edges[2].inset
		self.edges[2].length = self.edges[2].length - self.edges[3].inset -  self.edges[1].inset
		self.edges[3].length = self.edges[3].length - self.edges[2].inset -  self.edges[0].inset
		#gr = g()
		gr = a()
#		gr.set_xlink_href('./?face='+self.name)
#		gr.set_target('_parent')
		t = Turtle()
		t.moveTo(Vector(self.sx+self.edges[3].inset,self.sy+self.edges[0].inset))
		t.penDown()
		for i in self.edges:
			p = i.gen(t)
			t.right(90)
		t.penUp()
		t.finish()
		for i in t.getSVGElements():
			gr.addElement(i)
		if self.opt.show_labels:
			te = text(self.name,self.sx+self.width/2,self.sy+self.length/2)
			te.setAttribute("text-anchor","middle")
			gr.addElement(te)
		svg.addElement(gr)
class edge:
	def __init__(self,opt,length):
		self.opt = opt
		self.length = length
		self.slot_length = length * 0.9
		self.edge_type = 0
		self.edge_func = self.basic
		self.count = self.opt.count
	
	def __str__(self):
		return str('\t'+str(self.length)+'\n')

	def basic(self,t):
		t.forward(self.length)

	def d_inset(self,t):
		t.forward(self.length - self.inset)

	def gen(self,t):
		et = self.edge_type
		if et == 0:
			self.edge_func = self.basic
		if et == 1:
			#self.edge_func = self.basic_tab
			self.edge_func = self.castle_tab
		if et == 2:
			#self.edge_func = self.basic_slot
                        self.edge_func = self.castle_slot
		if et == 3:
			self.edge_func = self.castle_slot
		if et == 4:
			self.edge_func = self.castle_tab
		self.edge_func(t)
		
	def basic_tab(self,t):
		k = self.opt.kerf * self.opt.mult
		slot_length  = self.opt.slot_length * self.opt.mult
		hl = (self.length/2) - (slot_length/2.0)
		thickness = self.opt.thickness  * self.opt.mult
		t.forward(hl+k)
		t.left(90)
		t.forward(thickness)
		t.right(90)
		t.forward(slot_length-2*k)
		t.right(90)
		t.forward(thickness)
		t.left(90)
		t.forward(hl+k)
		
	def basic_slot(self,t):
		slot_length  = self.opt.slot_length * self.opt.mult 
		thickness = self.opt.thickness  * self.opt.mult
		hl = (self.length/2) - (slot_length/2.0)
		t.forward(hl)
		t.right(90)
		t.forward(thickness)
		t.left(90)
		t.forward(slot_length)
		t.left(90)
		t.forward(thickness)
		t.right(90)
		t.forward(hl)
		#t.penUp()

	def castle_slot(self,t):
		count = self.opt.count
		slot_length  = self.slot_length #self.opt.slot_length * self.opt.mult #* self.length
                hk = (self.opt.kerf * self.opt.mult)/2.0
		tl = (slot_length)/(count*2+1)
                hl = (self.length/2) - (slot_length/2.0)
		thickness = self.opt.thickness  * self.opt.mult
		#t.penDown()
                t.forward(hl)
		#t.right(90)
                #t.forward(1)
		#t.right(90)
                t.left(90)
                #t.forward(thickness)
                t.right(90)
		t.forward(tl)
		for i in range(count):
                        t.right(90)
                        t.forward(thickness)
                        t.left(90)
                        t.forward(tl)
                        t.left(90)
                        t.forward(thickness)
                        t.right(90)
                        t.forward(tl)
                #t.right(90)
                #t.forward(thickness)
                #t.left(90)
                t.forward(hl)

        def castle_tab(self,t):
            count = self.opt.count
            slot_length  = self.slot_length #self.opt.slot_length * self.opt.mult #* self.length
            hk = (self.opt.kerf * self.opt.mult)/2.0
            tl = (slot_length)/(count*2+1)
            hl = (self.length/2) - (slot_length/2.0)
            thickness = self.opt.thickness  * self.opt.mult
            #t.penDown()
            #t.forward(self.length)
            t.forward(hl)
            #t.right(90)
            #t.forward(thickness)
            #t.left(90)
            t.forward(tl)
            for i in range(count):
                    t.left(90)
                    t.forward(thickness)
                    t.right(90)
                    t.forward(tl)
                    t.right(90)
                    t.forward(thickness)
                    t.left(90)
                    t.forward(tl)
            #t.left(90)
            #t.forward(thickness)
            #t.right(90)
            t.forward(hl)  
                
	
		
 
def conffile(opt,config_file):
	c = ConfigParser.ConfigParser()
	try:
		os.stat(config_file)
		# read the configs
		c.readfp(open(config_file))
		items = c.options('boxotron')
		# scan through the options
		for i in items:
			value = c.get('boxotron',i)
			# cast as float if you can
			try:
				value = float(value)
			except: 
				pass
			vars(opt)[i] = value
	except: 
		# no config file, strip out defaults and write to config.
		print 'no such config , populating default '
		c.add_section('boxotron')
		k = vars(opt).keys()
		for i in k:
			c.set('boxotron',i,vars(opt)[i])
		c.write(open(config_file,'w'))

def parse(parser):
	# parse the command line options
	print 'Options'
	# define the command line variables
	parser.add_option("-l","--length",dest="length",help="Length of box ",type=float,default=100.0)
	parser.add_option("-w","--width",dest="width",help="width of box ",type=float,default=100.0)
	parser.add_option("-d","--depth",dest="depth",help="depth of box ",type=float,default=100.0)
	parser.add_option("-t","--thickness",dest="thickness",help="thickness of material ",type=float,default=3.0)
	parser.add_option("-c","--clearance",dest="clearance",help="clearance between panels of material ",type=float,default=3.0)
#        parser.add_option("-i","--inset",dest="inset",help="inset to middle of slot material ",type=float,default=3.0)
	parser.add_option("-s","--slot_length",dest="slot_length",help="length of slot ",type=float,default=30.0)
	#parser.add_option("-f","--file_name",dest="filename",help="file_name",default="box.dxf")
#        parser.add_option("-j","--join_every",dest="join_every",type=float,help="join every x  ",default=30.0)
	parser.add_option("-o","--outline",dest="outline",help="adds an outline layer to the dxf",default=0)
	#parser.add_option("--type",dest="type",help="box type = slot , bolt ",default="bolt")
	#parser.add_option("-b","--bolt_size",dest="bolt",help="bolt size ",type=float,default=3.0)
	#parser.add_option("--bolt_length",dest="bolt_length",help="bolt length ",type=float,default=15.0)
	#parser.add_option("--bolt_clearance",dest="bolt_tab_clearance",help="clearance between bolt and tab , multiple of bolt size",type=float,default=2.0)
	#parser.add_option("--nut_multiplier",dest="nut_multiplier",help="nut size - multiple of bolt size",type=float,default=1.6)
	#parser.add_option("--nut_depth",dest="nut_depth",help="nut depth - multiple of bolt size",type=float,default=0.5)
	#parser.add_option("--labels",dest="labels",help="labels for faces, 6 strings comma seperated",default='top,bottom,left,front,right,back')
	parser.add_option("--show_labels",dest="show_labels",help="show the labels 0 or 1",default=1)
	parser.add_option("--kerf",dest="kerf",help="kerf inset for tabs",type=float,default=0.05)
#        parser.add_option("--nut_thick_multiplier",dest="nut_thick_multiplier",help="nut thickness multiplier",type=float,default=1.0)
	parser.add_option("--multiplier",dest="mult",help="px multipler ",type=float,default=3.77955)
	parser.add_option("--count",dest="count",help="number of castle tops ",type=float,default=8)

#    *  "1pt" equals "1.25px" (and therefore 1.25 user units)
#    * "1pc" equals "15px" (and therefore 15 user units)
#    * "1mm" would be "3.543307px" (3.543307 user units)
#    * "1cm" equals "35.43307px" (and therefore 35.43307 user units)
#    * "1in" equals "90px" (and therefore 90 user units)
#
#


def config():
	global opt 
	op = OptionParser()
	parse(op)
	(option,args) = op.parse_args()
	if len(args) == 1:
		if args[0][-3:] == 'cfg':
			print "using " + args[0]
			conffile(option,args[0])
		else:   
			print 'config file name must end in .cfg'
	# create the drawing
	opt = option
	# update the lengths with the px to actual dimensions
	return option 

def box_maker():
	global opt
	border = 300
	totalx = 2 * opt.length + 2 * opt.depth + border
	totaly = 2 * opt.depth + opt.length + border
	s=svg(0, 0,2000,2000)
	# generate the box object
	a = box(opt)
	a.gen(s)
	if opt.show_labels:
		pass	
	if opt.outline:
		pass
	return s.getXML()

#if __name__ == '__main__' : main()

