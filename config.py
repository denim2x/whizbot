import os, re
from itertools import chain, zip_longest
from collections import namedtuple

from munch import munchify
import yaml

from util import realpath, Object, Executor, HTMLParser
from util.request import Request


with open(realpath('config.yaml')) as f:
  data = yaml.load(f, Loader=yaml.SafeLoader)
  locals().update(munchify(data))
  
class chuck_norris:
  _base = 'https://api.chucknorris.io/jokes'
  _categories = Request('GET', f'{_base}/categories')
  _random = Request('GET', f'{_base}/random')
  
  @classmethod
  def categories(cls, raw=False):
    ret = cls._categories().json()
    if raw:
      return ret
    return ', '.join(ret)
  
  @classmethod
  def random(cls, category=None, count=1, raw=False):
    params = None
    if category:
      params = { 'category': category }
      
    executor = Executor()
    for i in executor(count):
      executor[cls._random](params=params)
      
    ret = [munchify(e.json()) for e in executor.collect()]
    if raw:
      return ret
    return [e.value for e in ret]
  
_parser = HTMLParser()
def strip_html(html):
  return _parser(html).text
    
class Snippet:
  def __init__(self, data):
    self._data = data
    self._text = strip_html(data.snippet).strip()
    if not re.match(r'^.*[\.!\?]$', self._text):
      self._text = f"{self._text}…"
    self._caption = data.title
    
  def __bool__(self):
    return bool(self._text)
    
  @property
  def text(self):
    return self._text
  
  @property
  def caption(self):
    return self._caption
  
class wikipedia:
  _base = 'https://en.wikipedia.org/w/api.php'
  _search = Request('GET', _base, params={
    'action': 'query',
    'format': 'json',
    'list': 'search',
    'srsort': 'relevance',
    'srenablerewrites': 'on'
  })
  def __new__(cls, query, type=None, count=None):
    params = { 'srsearch': query }
    if count is not None:
      params['srlimit'] = count
    if type is not None:
      params['srprop'] = type
    res = cls._search(params=params)
    if not res.ok:
      return []
    return munchify(res.json()).query.search
    
  @classmethod
  def snippets(cls, query, count=None):
    return [Snippet(e) for e in cls(query, 'snippet', count)]
  
  @classmethod
  def snippet(cls, query):
    ret = cls.snippets(query, 1)
    return ret[0] if ret else None
  
_units = Object(metric='m', imperial='e')
units_ = Object(m='metric', e='imperial')

Precipitation = namedtuple('Precipitation', 'total hourly snow')

class Value(dict):
  def __init__(self, units, type):
    super().__init__()
    self._units = units
    self._unit = Units[units].get(type, '')
    
  def _format(self, key):
    return f"{self[key]}{self._unit}"

class Temperature(Value):
  def __init__(self, value, feel, min, max, units):
    super().__init__(units, 'temperature')
    self['value'] = value
    self['feel'] = feel
    
  def __bool__(self):
    return bool(self['value'])
    
  @property
  def value(self):
    return self._format('value')
  
  @property
  def feel(self):
    return self._format('feel')
  
class Wind(Value):
  def __init__(self, speed, direction, units):
    super().__init__(units, 'speed')
    self['speed'] = speed
    self['direction'] = direction or ''
    
  def __bool__(self):
    return bool(self['speed'])
    
  @property
  def speed(self):
    return self._format('speed')
  
  @property
  def direction(self):
    return self['direction']

Units = Object(
  metric = Object(
    temperature = '°C',
    speed = ' km/h',
  ),
)

class Observation:
  def __init__(self, data):
    self._meta = data.metadata
    self._units = units_[self._meta.units]
    data = data.observation
    self._data = data
    self._precipitation = Precipitation(data.precip_total, data.precip_hrly, data.snow_hrly)
    self._temperature = Temperature(data.temp, data.feels_like, data.min_temp, data.max_temp, self._units)
    self._wind = Wind(data.wspd, data.wdir_cardinal, self._units)
    
  @property
  def units(self):
    return self._units
  
  @property
  def observation(self):
    return self._data.wx_phrase
    
  @property
  def temperature(self):
    return self._temperature
  
  @property
  def precipitation(self):
    return self._precipitation
  
  @property
  def wind(self):
    return self._wind
  
  @property
  def pressure(self):
    return self._data.pressure
  
  @property
  def visibility(self):
    return self._data.vis
  
class Weather:
  notions = { 'forecast', 'humidity', 'precipitation', 'pressure', 'temperature', 'visibility', 'weather', 'wind speed' }
  def __init__(self, host, username, password):
    self._host = host
    self._auth = (username, password)
    self._url = f"https://{host}/api/weather"
    self._language = 'en-US'
    self._params = dict(language=self._language)
    self._location = Request('GET', f"{self._url}/v3/location/search", params=self._params, auth=self._auth)
    self._current = None
    
  def __bool__(self):
    return bool(self._current)
    
  def location(self, query):
    res = self._location(params=dict(query=query))
    if not res.ok:
      return False
    location = res.result().location
    latitude = location.latitude[0]
    longitude = location.longitude[0]
    geocode = f"geocode/{latitude}/{longitude}"
    self._current = Request('GET', f"{self._url}/v1/{geocode}/observations.json", params=self._params, auth=self._auth)
    return True
  
  def forecast(self, hours=None, days=None):
    pass
    
  def get_params(self, units):
    units = _units.get(units, units)
    return dict(units=units, **self._params)
    
  def current(self, units='m'):
    if not self:
      return
    res = self._current(params=self.get_params(units))
    if res.ok:
      return Observation(res.result())
    
__all__ = { 'ibm_cloud', 'chuck_norris', 'wikipedia' }
