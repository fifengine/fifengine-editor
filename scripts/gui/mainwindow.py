# -*- coding: utf-8 -*-

# ####################################################################
#  Copyright (C) 2005-2013 by the FIFE team
#  http://www.fifengine.net
#  This file is part of FIFE.
#
#  FIFE is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# ####################################################################

from fife.extensions import pychan
from menubar import MenuBar, Menu
from panel import Panel
from dockarea import DockArea
import toolbar
from toolbar import ToolBar
from statusbar import StatusBar
from fife import fife, fifechan

DOCKAREA = {
	'left'	: 'left',
	'right' : 'right',
	'top'	: 'top',
	'bottom': 'bottom'
}

class MainWindow(object):

	def __init__(self, *args, **kwargs):
		self._toolbar = None
		self._menubar = None
		self._statusbar = None
	
		self._rootwidget = None
		self._centralwidget = None
		self._dockareas = {
				DOCKAREA['left']:None, 
				DOCKAREA['right']:None, 
				DOCKAREA['top']:None, 
				DOCKAREA['bottom']:None
			}
			
		self._toolbarareas = {
				DOCKAREA['left']:None, 
				DOCKAREA['right']:None, 
				DOCKAREA['top']:None, 
				DOCKAREA['bottom']:None
			}
			
		self.dockareamarker = None
			
	def initGui(self, screen_width, screen_height):
		bar_height = 30

		self._dockareas[DOCKAREA['left']] = DockArea("left")
		self._dockareas[DOCKAREA['right']] = DockArea("right")
		self._dockareas[DOCKAREA['top']] = DockArea("top")
		self._dockareas[DOCKAREA['bottom']] = DockArea("bottom")

		self._toolbarareas[DOCKAREA['left']] = pychan.widgets.VBox(margins=(0,0,0,0))
		self._toolbarareas[DOCKAREA['right']] = pychan.widgets.VBox(margins=(0,0,0,0))
		self._toolbarareas[DOCKAREA['top']] = pychan.widgets.HBox(margins=(0,0,0,0))
		self._toolbarareas[DOCKAREA['bottom']] = pychan.widgets.HBox(margins=(0,0,0,0))
		
		self._statusbar = StatusBar(text=u"", panel_size=bar_height)
		self._toolbar = ToolBar(title=u"Toolbar", button_style=0)
		self._menubar = MenuBar(min_size=(screen_width, bar_height), position=(0, 0))
		
		# Set up root widget
		self._rootwidget = pychan.widgets.VBox(vexpand=True, hexpand=True)
		self._rootwidget.min_size = \
		self._rootwidget.max_size = (screen_width, screen_height)
		self._rootwidget.opaque = False
		
		# This is where the map will be displayed
		self._centralwidget = pychan.widgets.VBox(vexpand=True, hexpand=True)
		self._centralwidget.opaque = False
		
		middle = pychan.widgets.HBox(vexpand=True, hexpand=True)
		middle.opaque = False
		
		# Pychan bug? Adding a spacer instead of a container creates
		# a gap after the right dockarea
		middle.addChild(self._toolbarareas['left'])
		middle.addChild(self._dockareas['left'])
		middle.addChild(self._centralwidget)
		#middle.addSpacer(pychan.widgets.Spacer())
		middle.addChild(self._dockareas['right'])
		middle.addChild(self._toolbarareas['right'])
		
		self._rootwidget.addChild(self._menubar)
		#self._rootwidget.addChild(self._toolbar)
		self._rootwidget.addChild(self._toolbarareas['top'])
		self._rootwidget.addChild(self._dockareas['top'])
		self._rootwidget.addChild(middle)
		self._rootwidget.addChild(self._dockareas['bottom'])
		self._rootwidget.addChild(self._toolbarareas['bottom'])
		self._rootwidget.addChild(self._statusbar)

		self._toolbar.setDocked(True)
		self.dockWidgetTo(self._toolbar, "top")
		
		self._rootwidget.show()
		
	def getCentralWidget(self):
		return self._centralwidget
	
	def getStatusBar(self): 
		return self._statusbar
		
	def getMenuBar(self):
		return self._menubar
	
	def getToolBar(self): 
		return self._toolbar
	
	def dockWidgetTo(self, widget, dockarea, x=-1, y=-1):
		""" docks a B{Panel} widget to the given dock area
		
		@note:	
			- ToolBar needs special treatment, given x, y coordinates
			  have no effect on this Panel
			- x, y are cursor coordinates, without giving them the
			  widgets are added beneath the already existing ones
			  nice feature, but also makes problems on editor startup
			  (e.g. if a user docked 2 widgets left, on startup they
			   are added in a col instead of a grouped tab)
				
		@todo:	turn x,y documentation into something more useful
		
		@type	widget:	Panel
		@param	widget:	a panel widget instance
		@type	dockarea:	str
		@param	dockarea:	id of the target dock area
		@type	x:	int
		@param	x:	x coordinate
		@type	y:	int
		@param	y:	y coordinate
		"""
		if isinstance(widget, pychan.widgets.Widget) is False:
			print "Argument is not a valid widget"
			return
			
		if widget.parent:
			widgetParent = widget.parent
			widgetParent.removeChild(widget)
			widgetParent.adaptLayout()
			
		# We must hide the widget before adding it to the dockarea,
		# or we will get a duplicate copy of the widget in the top left corner
		# of screen.
		#widget.hide() 
		dockareas = self._dockareas
		
		# Panel widgets which provide an implementation for set_orientation()
		# should check if they need to re-align themselves
		if hasattr(widget, 'set_orientation'):
			key = ''
			if dockarea == DOCKAREA['left'] or dockarea == DOCKAREA['right']:
				key = 'Vertical'
			elif dockarea == DOCKAREA['top'] or dockarea == DOCKAREA['bottom']:
				key = 'Horizontal'
			widget.set_orientation(key=key)
	
		if isinstance(widget, ToolBar):
			dockareas = self._toolbarareas
			docked = False
			if dockarea == DOCKAREA['left']:
				docked = True
				dockareas[DOCKAREA['left']].addChild(widget)
				dockareas[DOCKAREA['left']].adaptLayout()
				
			elif dockarea == DOCKAREA['right']:
				docked = True
				dockareas[DOCKAREA['right']].addChild(widget)
				dockareas[DOCKAREA['right']].adaptLayout()
				
			elif dockarea == DOCKAREA['top']:
				docked = True
				dockareas[DOCKAREA['top']].addChild(widget)
				dockareas[DOCKAREA['top']].adaptLayout()
				
			elif dockarea == DOCKAREA['bottom']:
				docked = True
				dockareas[DOCKAREA['bottom']].addChild(widget)
				dockareas[DOCKAREA['bottom']].adaptLayout()
				
			else:
				print "Invalid dockarea"
			
			widget.dockareaname = dockarea
			widget.setDocked(docked)
				
		else:
			if dockarea == DOCKAREA['left']:
				dockareas[DOCKAREA['left']].dockChild(widget, x, y)
				
			elif dockarea == DOCKAREA['right']:
				dockareas[DOCKAREA['right']].dockChild(widget, x, y)
				
			elif dockarea == DOCKAREA['top']:
				dockareas[DOCKAREA['top']].dockChild(widget, x, y)
				
			elif dockarea == DOCKAREA['bottom']:
				dockareas[DOCKAREA['bottom']].dockChild(widget, x, y)
				
			else:
				print "Invalid dockarea"

	def getToolbarAreaAt(self, x, y, mark=False):
		if self.dockareamarker is None:
			self.dockareamarker = pychan.widgets.Container()
			self.dockareamarker.base_color = fifechan.Color(200, 0, 0, 100)
		if mark is False:
			self.dockareamarker.hide()
	
		# Mouse wasn't over any dockwidgets. See if it is near any edge of the screen instead
		if x <= self._toolbarareas["left"].getAbsolutePos()[0]+10:
			if mark:
				self.dockareamarker.position = self._toolbarareas["left"].getAbsolutePos()
				self.dockareamarker.size = (10, self._toolbarareas["left"].height)
				self.dockareamarker.show()
			return DOCKAREA["left"]
			
		elif x >= self._toolbarareas["right"].getAbsolutePos()[0]-10:
			if mark:
				self.dockareamarker.position = self._toolbarareas["right"].getAbsolutePos()
				self.dockareamarker.size = (10, self._toolbarareas["right"].height)
				self.dockareamarker.x -= 10
				self.dockareamarker.show()
			return DOCKAREA["right"]
			
		elif y <= self._toolbarareas["top"].getAbsolutePos()[1]+10:
			if mark:
				self.dockareamarker.position = self._toolbarareas["top"].getAbsolutePos()
				self.dockareamarker.size = (self._toolbarareas["top"].width, 10)
				self.dockareamarker.show()
			return DOCKAREA["top"]
			
		elif y >= self._toolbarareas["bottom"].getAbsolutePos()[1]-10:
			if mark:
				self.dockareamarker.position = self._toolbarareas["bottom"].getAbsolutePos()
				self.dockareamarker.y -= 10
				self.dockareamarker.size = (self._toolbarareas["bottom"].width, 10)
				self.dockareamarker.show()
			return DOCKAREA["bottom"]

		if mark is True:
			self.dockareamarker.hide()
		return None
			
	def getDockAreaAt(self, x, y, mark=False):
		""" returns the dock area at the given cursor coordinates (if possible)
		
			also used for highlighting the dock area (this method is used
			on drag mouse events of a B{Panel} widget)
		
		@type	x:	int
		@param	x:	cursor x coordinates
		@type	y:	int
		@param	y:	cursor y coordinates
		@type	mark:	bool
		@param	mark:	flag to wether show the dock area marker (red area indicator) or not
		@rtype	side:	str
		@return	side:	dockarea id (e.g. 'right', 'left' ...)
		"""
		side = None
		
		if self.dockareamarker is None:
			self.dockareamarker = pychan.widgets.Container()
			self.dockareamarker.base_color = fifechan.Color(200, 0, 0, 100)
		if mark is False:
			self.dockareamarker.hide()
	
		for key in DOCKAREA:
			side = DOCKAREA[key]
			
			dockarea = self._dockareas[side]
			#absX, absY = dockarea.getAbsolutePos()
			#if absX <= x and absY <= y \
			#		and absX+dockarea.width >= x and absX+dockarea.height >= y:
			#	return side
			placeIn, placeBefore, placeAfter = dockarea.getDockLocation(x, y)
			if placeIn or placeBefore or placeAfter:
				if mark is True:
					if placeIn:
						self.dockareamarker.position = placeIn.getAbsolutePos()
						self.dockareamarker.size = placeIn.size
					elif placeBefore:
						self.dockareamarker.position = placeBefore.getAbsolutePos()
						if side == "left" or side == "right":
							self.dockareamarker.size = (placeBefore.width, 10)
						else:
							self.dockareamarker.size = (10, placeBefore.height)
					elif placeAfter:
						self.dockareamarker.position = placeAfter.getAbsolutePos()
						
						if side == "left" or side == "right":
							self.dockareamarker.size = (placeAfter.width, 10)
							self.dockareamarker.y += placeAfter.height-10
						else:
							self.dockareamarker.size = (10, placeAfter.height)
							self.dockareamarker.x += placeAfter.width-10
						
					self.dockareamarker.show()
				return side

		# reset side, next attempt to find a new home
		side = None

		# Mouse wasn't over any dockwidgets. See if it is near any edge of the screen instead
		if x <= self._dockareas["left"].getAbsolutePos()[0]+10:
			if mark:
				self.dockareamarker.position = self._dockareas["left"].getAbsolutePos()
				self.dockareamarker.size = (10, self._dockareas["left"].height)
				self.dockareamarker.show()
			side = DOCKAREA["left"]
			return side
			
		elif x >= self._dockareas["right"].getAbsolutePos()[0]-10:
			if mark:
				self.dockareamarker.position = self._dockareas["right"].getAbsolutePos()
				self.dockareamarker.size = (10, self._dockareas["right"].height)
				self.dockareamarker.x -= 10
				self.dockareamarker.show()
			side = DOCKAREA["right"]
			return side
			
		elif y <= self._dockareas["top"].getAbsolutePos()[1]+10:
			if mark:
				self.dockareamarker.position = self._dockareas["top"].getAbsolutePos()
				self.dockareamarker.size = (self._dockareas["top"].width, 10)
				self.dockareamarker.show()
			side = DOCKAREA["top"]
			return side
			
		elif y >= self._dockareas["bottom"].getAbsolutePos()[1]-10:
			if mark:
				self.dockareamarker.position = self._dockareas["bottom"].getAbsolutePos()
				self.dockareamarker.y -= 10
				self.dockareamarker.size = (self._dockareas["bottom"].width, 10)
				self.dockareamarker.show()
			side = DOCKAREA["bottom"]
			return side

		if mark is True:
			self.dockareamarker.hide()
			
		return side
