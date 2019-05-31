from itertools import chain, repeat
from collections import namedtuple, defaultdict
from uuid import uuid4
from datetime import datetime
import re

from ibm_watson import AssistantV2, AssistantV1
from ibm_watson.assistant_v2 import MessageInput, MessageInputOptions, RuntimeIntent
from ibm_watson.assistant_v1 import \
  MessageInput as MessageInput_1, RuntimeIntent as RuntimeIntent_1, \
  Example, DialogNodeOutput, DialogNodeOutputGeneric, DialogNodeOutputTextValuesElement as DialogNodeText
from munch import munchify

from util import Timer, Data, String, split, Object
from watson import Result

def uuid():
  return uuid4().hex

_Output = namedtuple('Output', 'text intent confidence')

Fallback = namedtuple('Fallback', 'assistant threshold')

class Assistant:
  _api = AssistantV2
  api_version = 2
  @classmethod
  def v1(cls, id, **kw):
    return V1(id, **kw)
  
  def __init__(self, id, **kw):
    self._id = id
    self._service = self._api(**kw)
    self._session = None
    self._timer = Timer(mins=5)
    self.return_context = True
    self.version = self._service.version
    self.context = None
    self._fallback = None
    
  @property
  def session_id(self):
    if not self._session or self._timer: # expired
      self._session = self._service.create_session(self._id).get_result()['session_id']
      self._timer()   # restart timer
    return self._session
  
  def _output(self, output, text, intents):
    fallback = self._fallback
    if not output:
      return output
    if fallback and output.confidence < fallback.threshold or not output.intent:
      return fallback.assistant(text, intents)
    return output
    
  def __call__(self, text=None, intents=None, bypass=False):
    if intents:
      intents = [RuntimeIntent(e, 1) for e in intents]
    options = MessageInputOptions(return_context=self.return_context)
    input = MessageInput(text=text, intents=intents, options=options)._to_dict()
    
    res = Result(self._service.message(self._id, self.session_id, input, self.context))
    self.context = res.get('context')
    ret = Output(res.output)
    return ret if bypass else self._output(ret, text, intents)
  
  def __setitem__(self, input, output):
    raise NotImplementedError
    
  def link(self, assistant, threshold):
    assert 0 < threshold <= 1
    self._fallback = Fallback(assistant, threshold)
    
class Intent:
  _maxlen = 1024
  def __new__(cls, text, description=None):
    assert isinstance(text, str)
    text = text.strip()
    assert 0 < len(text) <= cls._maxlen
    assert not re.match(r"[\n\r\t]", text)
    examples = [Example(text, created=datetime.now())]
    return Object(intent=uuid(), description=description, examples=examples)
  
class DialogNode:
  _maxlen = 4096
  def __new__(cls, intent, text):
    assert isinstance(text, str)
    text = text.strip()
    assert 0 < len(text) <= cls._maxlen
    values = [DialogNodeText(text)]
    generic = [DialogNodeOutputGeneric('text', values)]
    output = DialogNodeOutput(generic)
    name = intent.intent
    return Object(dialog_node=name, description=intent.description, conditions=f'#{name}', output=output)
    
class V1(Assistant):
  _api = AssistantV1
  api_version = 1
  def __call__(self, text, intents=None):
    input = MessageInput_1(text=text)._to_dict()
    res = Result(self._service.message(self._id, input, alternate_intents=False, context=self.context))
    self.context = res.get('context')
    return self._output(Output_1(res), text, intents)
  
  def __setitem__(self, input, output):
    description = None
    if not isinstance(input, str):
      input, description = input
      
    intent = Intent(input, description)
    self._service.create_intent(self._id, **intent)
    
    node = DialogNode(intent, output)
    self._service.create_dialog_node(self._id, **node)

_entities = ({},)
_intents = repeat(RuntimeIntent(None, 1))
class Output(Data):
  def __init__(self, output):
    super().__init__()
    self._source = output
    
    entities = defaultdict(dict)
    for e in output.entities:
      entities[e.entity][e.value] = e
      entities[e.entity, e.value] = e
    self._entities = entities #munchify(entities)
      
    for g, i in zip(output.generic, chain(output.intents, _intents)):
      self._append(_Output(g.text, i.intent, i.confidence))
      
  @property
  def entities(self):
    return self._entities
  
  @property
  def _text(self):
    return self[0].text if self else None
  
  @property
  def text(self):
    return split(self._text) if self else []
  
  @property
  def intent(self):
    return self[0].intent if self else None
  
  @property
  def confidence(self):
    return self[0].confidence if self else None
  
  @property
  def data(self):
    return self._source

_intents_1 = repeat(RuntimeIntent_1(None, 1))
class Output_1(Output):
  def __init__(self, data):
    Data.__init__(self)
    #super().__init__()
    self._source = data
    for t, i in zip(data.output.text, chain(data.intents, _intents_1)):
      self._append(_Output(t, i.intent, i.confidence))
  