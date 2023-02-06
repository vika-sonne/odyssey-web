
from base64 import b64encode
from builtins import property as _property, tuple as _tuple
from operator import itemgetter as _itemgetter
from random import randbytes
from math import copysign, sqrt
from enum import Enum, auto
from typing import NamedTuple, Type
# Brython imports
from browser import html, document
# Odyssey Web imports
from bs import create_svg_tag, Pos, ActionBase, Inputbase


VERSION = (0, 4)


class OdysseyDrawExample(Inputbase):

	# Document

	class Layers(Enum):
		Electric = auto()
		Stamp = auto()
		Draw = auto()
		Notes = auto()


	class Multiline:

		DEFAULT_WIDTH = 2

		def __init__(self, id: str, layer: OdysseyDrawExample.Layers, closed: bool, points: iterable, width=DEFAULT_WIDTH):
			self.id, self.layer = id, layer
			self.closed, self.width = closed, width
			self.points: list[Pos] = list(points)

		def serialize(self, offset=0) -> str:
			offset = '\t' * offset
			ret = f'{offset}multiline:\n'
			offset += '\t'
			ret += f'{offset}id:{self.id}\n'
			ret += f'{offset}layer:{self.layer.name}\n'
			if self.closed:
				ret += f'{offset}closed:1\n'
			for p in self.points:
				ret += f'{offset}- {repr(p)}\n'
			return ret

	# UI

	class Style:

		@classmethod
		def set_attributes(cls, tag, style: dict):
			for k, v in style.items():
				tag.attrs[k] = v


	class UiBase:

		DEFAULT_TEMP_COLOR = 'yellow'
		DEFAULT_COLOR = 'green'

		def __init__(self, id: str | None = None) -> None:
			'id - if specified - set root_tag to existing SVG tag with this id'
			# set container: root SVG tag to positioning children tags
			if id:
				# set container to existing SVG tag with id
				self.root_tag = document.getElementById(id)
				# print(f'GET BY ID {id}: {self.root_tag=}')
			else:
				# set container to new SVG tag
				self.root_tag = create_svg_tag('g', id='i' + self.new_id())
				if(ui := self.get_ui_contaiter()):
					ui <= self.root_tag  # add tag to SVG document

		def clear_svg(self):
			'Clear SVG tags'
			if hasattr(self, 'root_tag') and self.root_tag:
				self.root_tag.innerHTML = ''
				self.root_tag.remove()
				self.root_tag = None

		def is_dark(self) -> bool:
			return True

		def get_first_child(self):
			return self.root_tag.firstElementChild

		def get_last_child(self):
			return self.root_tag.lastElementChild

		def get_childs_count(self) -> int:
			return self.root_tag.childElementCount

		def childs_iter(self):
			for t in self.root_tag.children:
				yield t

		@classmethod
		def get_ui_contaiter(cls) -> object | None:
			return document['scheme_ui']

		@classmethod
		def new_id(cls) -> str:
			'Returns new ID. Used for tag'
			return b64encode(randbytes(3), b'-_').decode()


	class Pointer(UiBase):
		'Document pointer UI - mouse'

		def __init__(self):
			super().__init__()
			self.pos: Pos = Pos()  # position
			self.update_pos()

		def update_pos(self):
			'Update UI panel'
			document['PointerCoord'].innerText = f'({self.pos.x}, {self.pos.y})'

		def add(self) -> Pointer:
			'Adds SVG elements according to pointer UI'
			p = create_svg_tag('path')  # figure holder tag
			p.setAttribute('d', 'M 0,30 h 60 M 30,0 v 60')
			p.style.stroke = 'lime'
			p.setAttribute('stroke-width', 2)
			self.root_tag <= p
			return self

		def set_pos(self, pos: Pos) -> bool:
			'return True if pos changed'
			if self.root_tag and self.pos != pos:
				# pos changed
				self.pos = pos
				self.root_tag.style.transform = f'translate({pos.x - 30}px, {pos.y - 30}px)'
				self.update_pos()
				return True
			return False  # pos not changed


	class Sheet:

		DEFAULT_WIDTH = 8000
		DEFAULT_HEIGHT = 6000

		def __init__(self):
			self.width, self.height = self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT

		def refresh(self) -> Sheet:
			document['Background'].style.width = self.width
			document['Background'].style.height = self.height
			document['SheetStatus'].innerText = f'({self.width}, {self.height})'
			return self


	class Grid:

		DEFAULT_PARAMETERS = { 'cell_size': 20, 'fill': 'none', 'stroke': '#dddddd', 'opacity': 0.25, 'stroke-width': 1, }

		def get_image(self):
			params = self.DEFAULT_PARAMETERS
			return f'''<svg width="{params["cell_size"] * 4}" height="{params["cell_size"] * 4}" xmlns="http://www.w3.org/2000/svg">
<defs>
	<pattern id="grid" width="{params["cell_size"] * 4}" height="{params["cell_size"] * 4}" patternUnits="userSpaceOnUse">
		<path d="M 0 {params["cell_size"]} L {params["cell_size"] * 4} {params["cell_size"]} M {params["cell_size"]} 0 L {params["cell_size"]} {params["cell_size"] * 4} M 0 {params["cell_size"] * 2} L {params["cell_size"] * 4} {params["cell_size"] * 2} M {params["cell_size"] * 2} 0 L {params["cell_size"] * 2} {params["cell_size"] * 4} M 0 {params["cell_size"] * 3} L {params["cell_size"] * 4} {params["cell_size"] * 3} M {params["cell_size"] * 3} 0 L {params["cell_size"] * 3} {params["cell_size"] * 4}" fill="{params["fill"]}" stroke="{params["stroke"]}" opacity="{params["opacity"]}" stroke-width="1"/><path d="M {params["cell_size"] * 4} 0 L 0 0 0 {params["cell_size"] * 4}" fill="{params["fill"]}" stroke="{params["stroke"]}" stroke-width="{params["stroke-width"]}"/>
	</pattern>
</defs>
<rect width="100%" height="100%" fill="url(#grid)"/></svg>'''

		def refresh(self) -> Grid:
			img = b64encode(bytes(self.get_image(), 'utf-8'))
			img = f'url("data:image/svg+xml;base64,{img.decode()}")'
			document['Background'].style.backgroundImage = img
			params = self.DEFAULT_PARAMETERS
			document['GridStatus'].innerText = f'{params["cell_size"]}'
			return self


	class DocumentTool:

		def __init__(self) -> None:
			self.action: 'ToolAction' | None = None

		def set_action(self, action: 'ToolAction'):
			self.action = action
			if(odg := self.odg()):
				odg.on_action_changed(action)

		def commit(self):
			'Document commit for action data'
			pass

		def cancel(self):
			'Document cancel for action data'
			pass

		# Input

		def pointer_move(self, pars: ActionBase.Parameters):
			pass

		def pointer_down(self, pars: ActionBase.Parameters):
			pass

		def pointer_up(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			return ActionBase.Result.Cancel

		def key_down(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			return ActionBase.Result.Cancel

		@classmethod
		def document_iter(cls, type_: Type):
			for x in (x for x in cls.odg().document if type(x) == type_):
				yield x

		@classmethod
		def odg(self) -> 'OdysseyDrawExample':
			'Return OdysseyDrawExample class instance'
			return OdysseyDrawExample.get_odg()

		@classmethod
		def title(cls):
			'Tool UI title'
			return ''


	class ToolAction(ActionBase):
		'OdysseyDrawExample document action. Contains data according to document action'

		def __init__(self, tool: object) -> None:
			super().__init__()
			self.tool = tool

		@classmethod
		def title(cls):
			'Action UI title'
			return ''


	class SelectionTool(DocumentTool, UiBase):

		DEFAULT_PARAMETERS = {'fill': 'rgba(0,0,255,0.25)', 'stroke': 'rgba(0,0,255,0.5)', 'stroke-dasharray': '4 2',}
		DEFAULT_PARAMETERS_DARK = {'fill': 'rgba(0,255,255,0.25)', 'stroke': 'rgba(0,255,255,0.5)', 'stroke-dasharray': '4 2',}

		def __init__(self, pars: ActionBase.Parameters):
			OdysseyDrawExample.DocumentTool.__init__(self)
			OdysseyDrawExample.UiBase.__init__(self)
			self.ref_pos = pars.pos  # reference position for resize
			self.p = None  # selection square SVG tag
			self.add(pars.pos)

		def add(self, pos: Pos):
			'Adds SVG elements according to pointer UI'
			params = self.DEFAULT_PARAMETERS_DARK if self.is_dark() else self.DEFAULT_PARAMETERS
			self.p = p = create_svg_tag('rect')
			p.attrs['x'], p.attrs['y'] = self.ref_pos.x, self.ref_pos.y
			p.width, p.height = 1, 1
			p.attrs['rx'], p.attrs['ry'] = 2, 2
			p.style.fill = params['fill']
			p.style.stroke = params['stroke']
			p.attrs['stroke-dasharray'] = params['stroke-dasharray']
			self.root_tag <= p

		def resize(self, pos: Pos):
			'Resizes UI according to current and reference positions'
			p = self.p  # get SVG square tag
			size = (pos - self.ref_pos).get_with_min(2)
			# resize square
			if size.x < 0:
				p.attrs['x'] = pos.x
				p.width = -size.x
			else:
				p.attrs['x'] = self.ref_pos.x
				p.width = size.x
			if size.y < 0:
				p.attrs['y'] = pos.y
				p.height = -size.y
			else:
				p.attrs['y'] = self.ref_pos.y
				p.height = size.y

		def pointer_move(self, pars: ActionBase.Parameters):
			self.resize(pars.pos)

		def pointer_up(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			'return Done for remove action'
			self.clear_svg()
			return ActionBase.Result.Done

		@classmethod
		def title(cls):
			return 'Select'


	class PointSelection(UiBase):
		'Point selection UI: show & edit points'

		DEFAULT_PARAMS = {'width': 20, 'height': 20, 'r': 10, 'stroke': 'orange', 'stroke-width': 4, 'rx': 3, 'fill': 'rgba(64,64,128,0.5)'}
		DEFAULT_PARAMS_DARK = {'width': 20, 'height': 20, 'r': 10, 'stroke': 'orange', 'stroke-width': 4, 'rx': 3, 'fill': 'rgba(128,128,255,0.5)'}

		def __init__(self, pos: Pos, is_end=False):
			super().__init__()
			self.pos = pos  # point position
			params = self.DEFAULT_PARAMS_DARK if self.is_dark() else self.DEFAULT_PARAMS
			if is_end:
				t = create_svg_tag('rect')
				OdysseyDrawExample.Style.set_attributes(t, params)
				t.attrs['x'], t.attrs['y'] = pos - Pos(self.DEFAULT_PARAMS['width'] / 2, self.DEFAULT_PARAMS['height'] / 2)
			else:
				t = create_svg_tag('circle')
				OdysseyDrawExample.Style.set_attributes(t, params)
				t.attrs['cx'], t.attrs['cy'] = pos# + Pos(self.DEFAULT_PARAMS['r'] / 4, self.DEFAULT_PARAMS['r'] / 2)
			self.root_tag <= t


	def __init__(self):
		Inputbase.__init__(self, 'odGraphContainer')
		self.document = []  # schematic objects
		self.sheet = self.Sheet().refresh()
		self.grid = self.Grid().refresh()
		self.pointer = self.Pointer().add()
		self.pointer_snap_to_grid = True
		self.select = None
		self.tool: DocumentTool | None = None

	def document_add(self, item: object):
		self.document.append(item)
		print(f'COMMIT\n{self.serialize()}')

	def document_get(self, id: str) -> object | None:
		for i in self.document:
			if i.id == id:
				return i
		return None

	def document_iter(self, type_: Type | None) -> object | None:
		'iterate document objects with type filter if scecified'
		if type_:
			for do in (x for x in self.document if type(x) == type_):
				yield do
		else:
			for i in self.document:
				yield i

	def document_del(self, id: str | object):
		if type(id) == str:
			for i in self.document:
				if i.id == id:
					self.document.remove(i)
					break
		else:
			self.document.remove(id)
		print(f'COMMIT\n{self.serialize()}')

	def serialize(self, offset=0) -> str:
		ret = ''
		for item in self.document:
			ret += '- ' + item.serialize()
		return ret

	def get_cell_size(self) -> int | None:
		return self.grid.DEFAULT_PARAMETERS['cell_size']

	def pointer_move(self, pars: ActionBase.Parameters):
		pos = pars.pos
		if not self.pointer_snap_to_grid:
			self.pointer.set_pos(pos)
			if(t := self.tool):
				t.pointer_move(pars)
		elif (cell_size := self.get_odg().get_cell_size()) and (pos - self.pointer.pos).abs_max() >= cell_size / 2:
			# pointer about to move to athother grid cell
			pos = Pos(cell_size * round(pos.x / cell_size), cell_size * round(pos.y / cell_size))
			if self.pointer.set_pos(pos):
				# pos changed to new grid cell
				if(t := self.tool):
					pars.pos = pos  # update pos to grid cell
					t.pointer_move(pars)

	def start_draw(self, draw_tool: Type, pars: ActionBase.Parameters):
		'start draw by tool'
		if(t := self.tool):
			t.cancel()
		self.tool = draw_tool()
		self.on_tool_changed()

	def process_action_result(self, result: ActionBase.Result):
		match result:
			case None:
				pass
			case result.Cancel:
				if(t := self.tool):
					t.cancel()
					self.tool = None
					self.on_tool_changed()
			case result.Done:
				if(t := self.tool):
					t.commit()
					self.tool = None
					self.on_tool_changed()

	def on_tool_changed(self):
		document['ToolStatus'].innerText = self.tool.title() if self.tool else ''
		if not self.tool:
			self.on_action_changed()

	def on_action_changed(self, action: ToolAction | None = None):
		document['ActionStatus'].innerText = action.title() if action else ''

	# Inputbase

	def on_mouse_move(self, pars: ActionBase.PointerParameters):
		odg = OdysseyDrawExample.get_odg()
		if not odg.tool and pars.buttons == 1:
			# no tool in progress # mouse button pressed # start selection tool
			odg.tool = odg.SelectionTool(pars)
			self.on_tool_changed()
		else:
			# pointer move # input calback
			odg.pointer_move(pars)

	def on_pointer_down(self, pars: ActionBase.PointerParameters):
		odg = OdysseyDrawExample.get_odg()
		if(t := odg.tool):
			# tool in progress # input  callback
			pars.pos = odg.pointer.pos
			t.pointer_down(pars)

	def on_pointer_up(self, pars: ActionBase.PointerParameters):
		odg = OdysseyDrawExample.get_odg()
		if(t := odg.tool):
			# tool in progress # input callback
			pars.pos = odg.pointer.pos
			odg.process_action_result(t.pointer_up(pars))

	def on_key_down(self, pars: ActionBase.KeyParameters):
		# print(f'KEY DOWN {pars.key=}')
		odg = OdysseyDrawExample.get_odg()
		if(t := odg.tool):
			# tool in progress # input callback
			odg.process_action_result(t.key_down(pars))
		else:
			# document hotkey
			match pars.key:
				case 'l':
					odg.start_draw(LineTool, pars)
				case 's':
					print(odg.serialize())

	@classmethod
	def init(cls):
		global odg
		odg = OdysseyDrawExample()

	@classmethod
	def open_file():
		from browser import window
		fi = document.querySelector('input[type=file]')
		def load_file(e):
			if(files := fi.files) and (f := files[0]):
				fr = window.FileReader.new()
				fr.readAsText(f)
				fr.bind('load', lambda e: print(e.target.result))
		fi.addEventListener('change', load_file)

	@classmethod
	def get_odg(cls) -> 'OdysseyDrawExample':
		global odg
		return odg


class LineTool(OdysseyDrawExample.DocumentTool):


	class AddAction(OdysseyDrawExample.ToolAction, OdysseyDrawExample.UiBase):

		def __init__(self, tool: 'LineTool', pars: ActionBase.Parameters):
			OdysseyDrawExample.ToolAction.__init__(self, tool)
			OdysseyDrawExample.UiBase.__init__(self)  # create new contaiter tag
			self.closed = False  # is closed line # used by commit
			# add first segment
			self.add_segment(pars.pos, pars.pos)

		def commit(self):
			if(odg := self.tool.odg()):
				odg.document_add(
					OdysseyDrawExample.Multiline(self.root_tag.id, OdysseyDrawExample.Layers.Draw, self.closed, self.tool.svg_points_iter()))

		def cancel(self):
			self.clear_svg()

		def add_segment(self, pos1: Pos, pos2: Pos, temporary=True):
			l = create_svg_tag('line')
			l.attrs['x1'], l.attrs['y1'] = pos1
			l.attrs['x2'], l.attrs['y2'] = pos2
			l.attrs['stroke'] = self.DEFAULT_TEMP_COLOR if temporary else self.DEFAULT_COLOR
			l.attrs['stroke-width'] = 2
			self.root_tag <= l

		def pointer_move(self, pars: ActionBase.Parameters):
			# sync last line segment with pointer position
			if(l := self.get_last_child()):
				l.attrs['x2'], l.attrs['y2'] = pars.pos

		def pointer_down(self, pars: ActionBase.Parameters):
			# print(f'DOWN {self.root_tag.children=} {[x for x in self.childs_iter()]=}')
			# add segment
			if self.get_childs_count():
				# add temporary line for next edit segment
				if(l := self.get_last_child()):
					l.attrs['stroke'] = self.DEFAULT_COLOR
					self.add_segment(Pos(l.attrs['x2'], l.attrs['y2']), pars.pos)
			else:
				# add first segment
				self.add_segment(pars.pos, pars.pos)

		def pointer_up(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			if(l := self.get_last_child()):
				if self.calc_line_lenght(l) > 1:  # if dont reuse last line
					# pointer was moved between last down & up # no reuse
					l.attrs['stroke'] = self.DEFAULT_COLOR
					self.add_segment(pars.pos, pars.pos)
			return ActionBase.Result.Continue

		def key_down(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			# print(f'KEY DOWN {pars.key=}')
			match pars.key:
				case 'Enter':
					# remove zero-lenght last line if necessary
					l = self.get_last_child()
					if self.calc_line_lenght(l) < 1:
						l.remove()
					# change last segment from temp
					if(l := self.get_last_child()):
						l.attrs['stroke'] = self.DEFAULT_COLOR
					# add segment if closed line
					if pars.shiftKey and self.get_childs_count() > 1:
						# close lines # connect first and last lines
						l1, l2 = self.get_last_child(), self.get_first_child()
						self.add_segment(Pos(l1.attrs['x2'], l1.attrs['y2']), Pos(l2.attrs['x1'], l2.attrs['y1']), False)
						self.closed = True
					# check for lines count
					return self.Result.Done if self.get_childs_count() > 0 else self.Result.Cancel
				case 'Escape':
					# cancel entire new line
					return self.Result.Cancel
			return self.Result.Continue

		@classmethod
		def calc_line_lenght(cls, line):
			return (Pos(line.attrs['x1'], line.attrs['y1']) - Pos(line.attrs['x2'], line.attrs['y2'])).get_len()

		@classmethod
		def title(cls) -> str:
			return 'Edit line'


	class EditAction(OdysseyDrawExample.ToolAction, OdysseyDrawExample.UiBase):

		def __init__(self, tool: 'LineTool', pars: ActionBase.Parameters, line: OdysseyDrawExample.Multiline):
			OdysseyDrawExample.ToolAction.__init__(self, tool)
			OdysseyDrawExample.UiBase.__init__(self, line.id)
			self.closed = line.closed  # is closed line # used by commit
			self.line = line  # document line
			self.line_1: object | None = None  # SVG line to edit
			self.line_2: object | None = None  # SVG line to edit
			self.init_pos = pars.pos  # used to restore SVG lines positions
			# aquire document line & SVG line tag
			for l in self.childs_iter():
				pos1 = (int(l.attrs['x1']), int(l.attrs['y1']))
				pos2 = (int(l.attrs['x2']), int(l.attrs['y2']))
				if pos1 == pars.pos:
					self.line_1 = l
				elif pos2 == pars.pos:
					self.line_2 = l

		def _update_lines(self, pos) -> list | None:
			# sync selection point UI & edit lines with position
			if self.line_1:
				self.line_1.attrs['x1'], self.line_1.attrs['y1'] = pos
			if self.line_2:
				self.line_2.attrs['x2'], self.line_2.attrs['y2'] = pos

		def commit(self):
			if(points := list(self.tool.svg_points_iter())):
				print('COMMIT POINT')
				self.line.points = points
			else:
				# empty line with no points # delete line from document
				self.tool.odg().document_del(self.line.id)

		def cancel(self):
			# cancel line edit # restore SVG lines positions
			if(l := self.line_1):
				l.attrs['x1'], l.attrs['y1'] = self.init_pos
			if(l := self.line_2):
				l.attrs['x2'], l.attrs['y2'] = self.init_pos

		def pointer_move(self, pars: ActionBase.Parameters):
			# sync last line segment with pointer position
			self._update_lines(pars.pos)

		def pointer_up(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			return self.Result.Done

		def key_down(self, pars: ActionBase.Parameters) -> ActionBase.Result:
			# print(f'KEY DOWN {pars.key=}')
			match pars.key:
				case 'Enter':
					return self.Result.Done
				case 'Escape':
					return self.Result.Cancel
				case 'Delete':
					if pars.shiftKey:
						# delete line
						self.clear_svg()
					else:
						# delete point
						if self.line_1 and self.line_2:
							self.line_2.attrs['x2'] = self.line_1.attrs['x2']
							self.line_2.attrs['y2'] = self.line_1.attrs['y2']
							self.line_1.remove()
							self.line_1 = None
						elif self.line_1:
							self.line_1.remove()
							self.line_1 = None
						elif self.line_2:
							self.line_2.remove()
							self.line_2 = None
					return self.Result.Done
			return self.Result.Continue

		@classmethod
		def title(cls) -> str:
			return 'Edit line'


	def __init__(self) -> None:
		super().__init__()
		self.point_selection: OdysseyDrawExample.PointSelection | None = None  # point selection UI: show edit points
		self.line: OdysseyDrawExample.Multiline | None = None  # document line to edit

	def commit(self):
		if(a := self.action):
			a.commit()

	def cancel(self):
		if(a := self.action):
			a.cancel()

	def pointer_move(self, pars: ActionBase.Parameters):
		if(a := self.action):
			a.pointer_move(pars)
		else:
			# check for document line points under mouse
			pos = pars.pos
			for line in self.document_iter(OdysseyDrawExample.Multiline):
				for i, p in enumerate(line.points):
					if p == pos:  # is line point under mouse
						# point under mouse found # show selection point UI
						self.point_selection = OdysseyDrawExample.PointSelection(pos, i == 0 or i == len(line.points) - 1)
						self.line = line
						return
			# no one point under mouse # hide selection point UI
			if(ps := self.point_selection):
				ps.clear_svg()
				self.line = self.point_selection = None

	def pointer_down(self, pars: ActionBase.Parameters):
		if(a := self.action):
			a.pointer_down(pars)  # action in progress # redirect input
		elif self.point_selection and self.line:
			self.action = self.EditAction(self, pars, self.line)
			self.point_selection.clear_svg()
			self.line = self.point_selection = None
		else:
			self.action = self.AddAction(self, pars)

	def pointer_up(self, pars: ActionBase.Parameters) -> ActionBase.Result:
		if(a := self.action):
			return a.pointer_up(pars)

	def key_down(self, pars: ActionBase.Parameters) -> ActionBase.Result:
		if(a := self.action):
			return a.key_down(pars)
		elif pars.key == 'Delete':
			if self.point_selection and self.line:
				# delete line/point
				pars.pos = self.point_selection.pos
				self.pointer_down(pars)
				if(a := self.action):
					return a.key_down(pars)

	def document_lines_iter(self):
		'iterate document line by two points'
		if(odg := OdysseyDrawExample.get_odg()):
			for line in (x for x in odg.document_iter(OdysseyDrawExample.Multiline)):
				for pos1, pos2 in zip(line.points[:-1], line.points[1:]):
					yield (pos1, pos2)

	def svg_points_iter(self):
		'iterate line points from action SVG collection (root tag)'
		if(a := self.action) and (rtag := a.root_tag):
			for t in rtag.children:
				if t.tagName == 'line':
					yield Pos(t.attrs['x1'], t.attrs['y1'])
			if not a.closed and (l := a.get_last_child()):
				yield Pos(l.attrs['x2'], l.attrs['y2'])

	@classmethod
	def title(cls) -> str:
		return 'Draw/edit lines'
