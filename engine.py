import re

from _bareasgi import text_reader, text_response, json_response
from config import ibm_cloud, chuck_norris, wikipedia, Weather
from watson import Assistant
from util import split


def _clean(text):
  """Strips any CR/LF/TAB characters from text"""
  if text is None:
    return None
  return re.sub(r"\s+", " ", text)

weather = Weather(**ibm_cloud.weather)
  
assistant = Assistant(**ibm_cloud.chatbot)
wikibot = Assistant.v1(**ibm_cloud.wikibot)
assistant.link(wikibot, 0.9)

def retry():
  return json_response(assistant(intents=['retry']).text)

_weather = None

async def message(scope, info, matches, content):
  global _weather
  text = _clean((await text_reader(content)).strip().lstrip('.').lstrip())
  if text == '':
    return json_response(assistant(intents=['welcome']).text)
  
  if not _weather:
    res = assistant(text)
    if res is None:
      return json_response(res.data, 404)
    
    if not res.intent or res.confidence < 0.9:
      ret = wikipedia.snippet(text)
      if not ret:
        return retry()
      
      wikibot[text, ret.caption] = ret.text
      return json_response(split(ret.text))
  else:
    res = assistant(text, bypass=True)
    if res and res.intent and res.confidence >= 0.9:
      _weather = None
      return json_response(res.text)
      
  if _weather or res.intent == 'weather':
    if _weather:
      notions = _weather
      location = text
    else:
      ret = dict(res.entities['notion'])
      notions = set()
      for notion in set(ret):
        if notion in Weather.notions:
          notions.add(notion)
          del ret[notion] 

      locations = list(ret.values())
      location = locations[0].value if locations else None
      if not location and not weather:
        _weather = notions
        return json_response(res.text)
    
    if location and not weather.location(location):
      return retry()
    
    _weather = None
    obs = weather.current()
    if not obs:
      return retry()
    
    answer = []
    if obs.observation:
      answer.append(obs.observation)
      
    if 'weather' in notions:
      notions.update({ 'temperature', 'wind speed' })
      
    if 'temperature' in notions:
      e = obs.temperature
      if e:
        answer.append(f"temperature: {e.value} (feels like: {e.feel})")
      
    if 'wind speed' in notions:
      e = obs.wind
      if e:
        answer.append(f"wind: {e.direction} {e.speed}")
    
    if not answer:
      return retry()
      
    return json_response(answer)
      
  if res.intent == 'chuck_norris':
    category = res.entities['domain'].get('value')
    if ('notion', 'categories') in res.entities:
      ret = [chuck_norris.categories()]
    elif ('notion', 'joke') in res.entities:
      ret = chuck_norris.random(category)
    else:
      ret = chuck_norris.random(category, 3)
    return json_response(ret)
  
  return json_response(res.text)
      
