from util import OrderedDict


def _check(value):
  if isinstance(value, bool):
    return True
  try:
    iter(value)
    return True
  except TypeError:
    return False

class Set(set):
  def __init__(self, src):
    super().__init__()
    self._bool = None
    self.update(src)

  def clone(self):
    res = Set(self)
    res._bool = self._bool
    return res

  def union(self, other):
    if _check(other):
      return self.clone().update(other)
    return self

  def __contains__(self, item):
    if super().__contains__(item):
      return True
    return self._bool is bool(item)

  def update(self, src):
    if isinstance(src, bool):
      if self._bool is None:
        self._bool = src
        return True
      return False
    if _check(src):
      super().update(src)
      return True
    return False

Set.__or__ = Set.union

class OrderedSet:
  def __init__(self, src=None):
    super().__init__()
    self._data = OrderedDict()

    if src:
      self.update(src)

  def update(self, *sources):
    for src in sources:
      for item in src:
        self.add(item)
    return self

  def difference_update(self, src):
    for item in src:
      self.discard(item)
    return self

  def add(self, item):
    if item in self:
      return False
    self._data[item] = None
    return True

  def __contains__(self, item):
    return item in self._data

  def discard(self, item):
    if item in self:
      return False
    del self._data[item]
    return True

  def remove(self, item):
    if not self.discard(item):
      raise KeyError

  def __iter__(self):
    yield from self._data

  def clear(self):
    if not self:
      return False
    self._data.clear()
    return True

  def __bool__(self):
    return bool(self._data)

  def __repr__(self):
    return f"{{{', '.join(repr(e) for e in self)}}}"

  def __len__(self):
    return len(self._data)

  def __getitem__(self, index):
    res = list(self)
    if index == slice(None):
      return res
    return res[index]
