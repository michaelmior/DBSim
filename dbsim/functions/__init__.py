from . import math, relational, string


def register_on(dataset):
  math.register_on(dataset)
  string.register_on(dataset)
  relational.register_on(dataset)
