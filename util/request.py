from util import mixin

from munch import munchify
from requests import Request, Session, Response
_session = Session()

@mixin(Request)
class _Request:
  def __call__(self, params=None, json=None):
    req = self.prepare()
    if params:
      req.prepare_url(req.url, params)
    if json:
      req.prepare_body(None, self.files, json)
    return _session.send(req)
    
    
@mixin(Response)
class _Reponse:
  def result(self):
    if self.ok:
      return munchify(self.json())
  
