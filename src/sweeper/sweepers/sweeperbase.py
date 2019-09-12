#!/usr/bin/env python
# * coding: utf8 *
'''
sweeperbase.py
A class that defines the sweeper.sweepers contract
'''

class SweeperBase(object):
  def __init__(self):
    pass

  def sweep(self, params):
    raise NotImplemented()

  def try_fix(self, params):
    raise NotImplemented()
