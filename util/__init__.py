import os, re
from platform import python_version_tuple as get_pyversion
from statistics import mean as _mean, StatisticsError
from time import time_ns
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor as _Executor      
from html.parser import HTMLParser as _HTMLParser

from munch import munchify


pyversion = tuple(int(e) for e in get_pyversion())
if pyversion >= (3, 6, 0):
  OrderedDict = dict
else:
  from collections import OrderedDict

__dir__ = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/..')

def realpath(path):
  return os.path.join(__dir__, path)

def new(cls, *args, **kw):
  if not isinstance(cls, type):
    cls = type(cls)
  return cls(*args, **kw)

def attach(target):
  def deco(func):
    setattr(target, func.__name__, func)
    return func
  return deco

def mixin(target):
  exclude = { '__module__', '__dict__', '__weakref__', '__doc__', '__new__' }
  def deco(cls):
    for name, attr in cls.__dict__.items():
      if name in exclude:
        continue
      setattr(target, name, attr)
    return cls
  return deco
  
class Object:
  def __new__(cls, **kw):
    return munchify(kw)

class Map:
  def __new__(cls, data=None, key=None):
    if isinstance(key, property):
      key = property.fget
    if data is None:
      return
    if key:
      return dict((key(e), e) for e in data)
    return dict(data)

class String:
  def encode(self, *args, **kw):
    if str(self):
      return str(self).encode(*args, **kw)
  
  def __str__(self):
    pass
  
class List:
  def __new__(cls, self):
    if self is None:
      return []
    if hasattr(self, '__len__'):
      return self
    return list(self)

class Data:
  def __init__(self, data=None):
    self._data = List(data)
  
  def __getitem__(self, index):
    return self._data[index] if self else None
  
  def __len__(self):
    return len(self._data)
  
  def __bool__(self):
    return bool(self._data)
    
  def __iter__(self):
    yield from self._data
    
  def _append(self, item):
    return self._data.append(item)
    
class TimeDelta:   # Immutable data class
  def __init__(self, days=0, secs=0, nanos=0, micros=0, millis=0, mins=0, *args, **kw):
    self._time = timedelta(days, secs + nanos / 1e9, micros, millis, mins, *args, **kw)
    self.secs = self.time.total_seconds()
    
    self.mins = self.secs / 60
    self.hours = self.mins / 60
    self.days = self.hours / 24
    
    self.millis = self.secs * 1e3
    self.micros = self.secs * 1e6
    self.nanos = self.secs * 1e9
    
  @property
  def time(self):
    return self._time

class Timer:
  def __init__(self, *args, **kw):
    self._time = None
    self.duration = TimeDelta(*args, **kw) 
    
  @property
  def duration(self):
    return self._duration
  
  @duration.setter
  def duration(self, value):
    self._duration = value
    return self.reset()
  
  def reset(self):
    if self._time is None:
      return False
    self._time = None
    return True
    
  @property
  def elapsed(self):
    return TimeDelta(nanos=self._elapsed)
  
  def restart(self):
    return self()
    
  def __call__(self):
    self._time = time_ns()
  
  def __bool__(self):
    if self._elapsed <= self._duration.nanos:
      return False
    return self.reset()
    
  @property
  def _elapsed(self):
    if self._time is None:
      return 0
    return time_ns() - self._time

def mean(data, default=None):
  try:
    return _mean(data)
  except StatisticsError:
    return default
  
def _bisect(self, value, key, a, b):  
  n = b - a
  if n <= 0:
    return a
  m = (a + b) // 2
  x = key(self[m])
  if value == x:
    return m
  if value < x:
    return _bisect(self, value, key, a, m-1)
  return _bisect(self, value, key, m+1, b)
  
def bisect(self, value, key=None):
  if key is None:
    key = lambda e: e
  return _bisect(self, value, key, 0, len(self))
  
_newline = r'\s*[\n\r]+\s*'

def strip(text):
  return re.sub(_newline, '', text)

def split(text):
  return re.split(_newline, text)

def casefold(self):
  return str(self).casefold()

def sign(self):
  if self == 0:
    return 0
  return -1 if self < 0 else 1

class Future:
  def __init__(self, func, executor):
    self._func = func
    self._executor = executor
  
  def __call__(self, *args, **kw):
    self._executor.submit(self._func, *args, **kw)
    return self

class Executor:
  def __init__(self, src=None):    #FIXME
    self._executor = None
    self._futures = None
  
  def __call__(self, *args, **kw):    #FIXME
    _range = range(*args, **kw)
    self._executor = _Executor(max_workers=len(_range))
    self._futures = []
    yield from _range
    
  def __bool__(self):
    return bool(self._executor)
    
  def __getitem__(self, func):
    return Future(func, self)
  
  def __iter__(self):
    if self:
      for future in self._futures:
        yield future.result()
      self._executor.shutdown(False)
      self._executor = None
      
  def collect(self):
    return tuple(self)
  
  def submit(self, func, *args, **kw):
    if self:
      future = self._executor.submit(func, *args, **kw)
      self._futures.append(future)

class HTMLParser(_HTMLParser):
  def __init__(self, html=None):
    super().__init__()
    self.strict = False
    self.convert_charrefs = True
    self._text = []
    self(html)
    
  def handle_data(self, text):
    self._text.append(text)
    
  def __call__(self, html):
    self.reset()
    self._text.clear()
    if html is not None:
      self.feed(html)
    return self
    
  @property
  def text(self):
    return re.sub(r" +", " ", ''.join(self._text))
