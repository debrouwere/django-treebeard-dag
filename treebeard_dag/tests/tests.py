from utils import TestCase
from django.test.client import Client
from revisions import models

# mirror the tests from treebeard: 
# http://github.com/tabo/django-treebeard/blob/master/treebeard/tests.py
#
# (actually, most of them should run as-is and mostly require additional ones
# to test the polyhierarchy, since treebeard-dag tries to stay as close to the 
# treebeard API as can be done sensibly)
#
# -- het zou interessant zijn om de treebeard testclasses te subclassen,
# met, waar er verschillen zijn of waar een test irrelevant is, overrides