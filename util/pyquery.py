from itertools import islice

from util import attach

from pyquery import PyQuery as pq, text as _text


class Text:
  _tag = 'text'
  _html = f'<{_tag}>'
  def __new__(cls, text, prev=None):
    return pq(cls._html).append(text or '').before(prev)

_text.INLINE_TAGS.update([Text._tag])

def _Text(node, prev=None):
  return Text(node, prev)[0] if isinstance(node, str) else node

_before = pq.before
@attach(pq.fn)
def before(other):
  if other is None:
    return this
  return _before(this, other)

#@attach(pq.fn)
def _iter(this):
  if not this:
    return this
  prev = _Text(this[0])
  yield pq(prev)
  for node in islice(this, 1, None):
    if isinstance(node, str):
      elem = Text(node)
      yield elem.set(_prev=pq(prev))
      prev = elem[0]
    else:
      yield pq(node)
      prev = node

@attach(pq.fn)
def test(include=None, exclude=None):
  if not this.is_(include):
    return False

  if exclude and this.is_(exclude):
    return False

  return True

@attach(pq.fn)
def set(**kw):
  for name, val in kw.items():
    setattr(this, name, val)
  return this

_prev = pq.prev
@attach(pq.fn)
def prev(sel=None):
  if hasattr(this, '_prev'):
    return this._prev.filter(sel)
  return _prev(this, sel)

@attach(pq.fn)
def default(name, default=None):
  value = this.attr(name)
  return default if value is None else value

_items = pq.items
@attach(pq.fn)
def items(include=None, exclude=None):
  for node in _iter(this):
    if node.test(include, exclude):
      yield node

@attach(pq.fn)
def tail(sel=None):
  return pq([Text(e.tail)[0] for e in this]).filter(sel)

@attach(pq.fn)
def nextUntil(sel=None, filter=None):
  res = OrderedSet()
  if sel is None:
    sel = ':not(*)'
  for node in this.items():
    while True:
      res.update(node.tail(filter))
      node = node.next()
      if node.is_(sel) or not node:
        break
      if node.is_(filter):
        res.update(node)

  return pq(res[:])
