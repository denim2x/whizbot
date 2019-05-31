from munch import munchify


class Result:
  def __new__(cls, res):
    return munchify(res.get_result())

from .assistant import Assistant
