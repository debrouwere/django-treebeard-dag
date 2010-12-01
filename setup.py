import os
from setuptools import setup, find_packages
version = '0.2'
README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read()
setup(name='django-treebeard-dag',
      version=version,
      description=("Directed acyclic graphs in Django."),
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      keywords='graphs dag',
      author='Stijn Debrouwere',
      author_email='stijn@stdout.be',
      url='http://stdbrouw.github.com/django-treebeard-dag/',
      download_url='http://www.github.com/stdbrouw/django-treebeard-dag/tarball/master',
      license='MIT',
      packages=find_packages(),
      )