from util import new, Set

class SortedList(list):
  def __init__(self, src=None, key=None):
    super().__init__(self, src)
    self._key = key
    
  def sort(self):
    super().sort(self._key)
    return self

class _List:
  def __add__(self, item):
    return new(self, [*self, item])

  def __radd__(self, item):
    return new(self, [item, *self])

  def __and__(self, other):
    return new(self, [*self, *other])

  def __rand__(self, other):
    return new(self, [*other, *self])

  def __mul__(self, other):
    return new(self, zip(self, other))

  def __rmul__(self, other):
    return new(self, zip(other, self))

  def join(self, sep=''):
    return sep.join(self)

  def range(self):
    return range(len(self))

  def get(self, index, default=None):
    return self[index] if index in self.range() else default

  def index(self, item, default=None):
    try:
      return super().index(item)
    except ValueError:
      return default

class Tuple(_List, tuple):
  def __repr__(self):
    return tuple.__repr__(self)

class List(_List, list):
  def __init__(self, src=None, banned=None, **kw):
    super().__init__()
    self.__banned = Set(banned)
    self.__format = kw.get('format', '{item}')
    self._str = kw.get('str', ', ')
    self.extend(src)

  def __repr__(self):
    return list.__repr__(self)

  def _format(self, item):
    return self.__format.format(item=str(item))

  def __str__(self):
    return self._str.join(self._format(e) for e in self)

  def _banned(self, kw):
    return self.__banned | kw.get('banned')

  def append(self, item, **kw):
    if item not in self._banned(kw):
      super().append(item)

  def extend(self, other, **kw):
    if other is None:
      return False
    super().extend(e for e in other if e not in self._banned(kw))
    return True
