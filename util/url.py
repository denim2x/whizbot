import os
from urllib.parse import urlsplit, urlunsplit, SplitResult

from util import Tuple


class URL(object):
  class _Dict(dict):
    _extra = { 'basename', 'subdomain' }

    def regular(self, key):
      return key in self and key not in self._extra

    def __setitem__(self, key, value):
      if key is 'path':
        super().__setitem__('basename', os.path.basename(value) if value else '')
      elif key is 'netloc':
        domain = value.rsplit('.', 2)
        super().__setitem__('subdomain', domain[0] if len(domain) is 3 else '')

      return super().__setitem__(key, value)

  _keys = Tuple(SplitResult._fields)
  basename = None
  subdomain = None

  def __init__(self, url=None, cut=None):
    self.__dict__ = self._Dict()
    _keys = self._keys
    if isinstance(url, str):
      data = _keys * urlsplit(url)
    elif isinstance(url, dict):
      data = url
    elif url is not None:
      data = _keys * url
    else:
      data = []

    index = len(_keys)
    if isinstance(cut, str):
      index = _keys.index(cut, index)
    elif isinstance(cut, int):
      index = cut

    _dict = dict(data)
    for k in _keys[:index]:
      self._set(k, _dict.get(k, ''))
    for k in _keys[index:]:
      self._set(k)

  def _set(self, key, value=''):
    self.__dict__[key] = value

  def _regular(self, key):
    return self.__dict__.regular(key)

  def _key(self, key):
    return key if isinstance(key, str) else self._keys.get(key)

  def __getitem__(self, key):
    return self.__dict__[self._key(key)]

  def __setitem__(self, key, value):
    key = self._key(key)
    if self._regular(key):
      self._set(key, value)

  def __len__(self):
    return len(self._keys)

  def __iter__(self):
    for k in self._keys:
      yield self[k]

  def __str__(self):
    return urlunsplit(self)

  def format(self, *args, **kw):
    return str(self).format(*args, **kw)

  def __repr__(self):
    _name = self.__class__.__name__
    data = (f"{k}='{self[k]}'" for k in self._keys)
    return f"{_name}({', '.join(data)})"
