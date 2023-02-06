
from builtins import property as _property, tuple as _tuple
from operator import itemgetter as _itemgetter
from enum import Enum, auto
from math import copysign, sqrt
from browser import html, document


def create_svg_tag(tag_name: str, classes: str | tuple[str] | None = None, id: str | None = None):
	ret = document.createElementNS('http://www.w3.org/2000/svg', tag_name)
	if isinstance(classes, str):
		ret.classList.add(classes)
	elif classes:
		for c in classes:
			ret.classList.add(c)
	if id:
		ret.attrs['id'] = id
	return ret

def find_parent(tag, Class: str | None = None, tag_name: str | None = None) -> object | None:
	if tag_name:
		tag_name = tag_name.lower()
	while True:
		if (not Class or tag.classList.contains(Class))\
				and (not tag_name or tag.tagName.lower() == tag_name):
			return tag
		if not tag.parentElement:
			return None
		tag = tag.parentElement


class Pos(tuple):
	'Pos(x, y) -- x, y is integers'
	__slots__ = ()
	x = _property(_itemgetter(0), doc='Alias for field number 0')
	y = _property(_itemgetter(1), doc='Alias for field number 1')

	def __new__(_cls, x=0, y=0):
		'Create new instance of Pos(x, y)'
		return _tuple.__new__(_cls, (int(x), int(y)))

	def __repr__(self) -> str:
		return f'{self.x},{self.y}'

	def __add__(self, other):
		return type(self)(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return type(self)(self.x - other.x, self.y - other.y)

	def abs_max(self) -> int:
		'return max of x and y'
		return max(abs(self.x), abs(self.y))

	def get_with_min(self, abs_min=1) -> 'Pos':
		'return Pos with respect of minimum x and y values'
		x, y = self
		if abs(self.x) < abs_min:
			x = int(copysign(abs_min, self.x))
		if abs(self.y) < abs_min:
			y = int(copysign(abs_min, self.y))
		return type(self)(x, y)

	def get_len(self) -> float:
		'return Cartesian length'
		return sqrt(self.x * self.x + self.y * self.y)


class ActionBase:


	class Result(Enum):
		Continue = auto()
		Done = auto()
		Cancel = auto()


	class Parameters:

		def __init__(self, ev):
			self.metaKey, self.altKey, self.shiftKey = ev.metaKey, ev.altKey, ev.shiftKey


	class PointerParameters(Parameters):

		def __init__(self, ev):
			super().__init__(ev)
			self.pos = Pos(ev.offsetX, ev.offsetY)
			#  0: No button or un-initialized
			#  1: Primary button (usually the left button)
			#  2: Secondary button (usually the right button)
			#  4: Auxiliary button (usually the mouse wheel button or middle button)
			#  8: 4th button (typically the "Browser Back" button)
			# 16: 5th button (typically the "Browser Forward" button)
			self.buttons = ev.buttons


	class KeyParameters(Parameters):

		def __init__(self, ev):
			super().__init__(ev)
			self.key = ev.key


	def commit(self):
		pass

	def cancel(self):
		pass

	def pointer_down(self, pars: Parameters) -> Result:
		return self.Result.Cancel

	def pointer_move(self, pars: Parameters):
		pass

	def pointer_up(self, pars: Parameters) -> Result:
		return self.Result.Cancel

	def key_down(self, pars: Parameters) -> Result:
		return self.Result.Cancel


class Inputbase:

	def __init__(self, root_tag_id: str) -> None:

		def mouse_move(ev):
			ev.preventDefault()
			ev.stopPropagation()
			ev.cancelBubble = True
			self.hovered_tag = ev.target
			if find_parent(ev.target, self.root_tag_id):
				# pointer move over root tag
				pars = ActionBase.PointerParameters(ev)
				# print(f'Move {pars=}')
				self.on_mouse_move(pars)

		def pointer_down(ev):
			pars = ActionBase.PointerParameters(ev)
			# print(f'DOWN {pars=}')
			self.on_pointer_down(pars)

		def pointer_up(ev):
			pars = ActionBase.PointerParameters(ev)
			# print(f'UP   {pars=}')
			self.on_pointer_up(pars)

		def key_down(ev):
			pars = ActionBase.KeyParameters(ev)
			# print(f'KEY DOWN: key: {pars.key}')
			self.on_key_down(pars)
			ev.preventDefault()
			ev.stopPropagation()

		self.root_tag_id = root_tag_id

		self.hovered_tag = None
		document.bind('mousemove', mouse_move)
		document.bind('pointerdown', pointer_down)
		document.bind('pointerup', pointer_up)
		document.bind('keydown', key_down)

	def on_mouse_move(self, pars: ActionBase.PointerParameters):
		pass

	def on_pointer_down(self, pars: ActionBase.PointerParameters):
		pass

	def on_pointer_up(self, pars: ActionBase.PointerParameters):
		pass

	def on_key_down(self, pars: ActionBase.KeyParameters):
		pass
