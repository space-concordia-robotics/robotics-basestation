from setuptools import setup, find_packages

import roboticsbase

import pygtk
pygtk.require('2.0')
import gtk

#REQUIREMENTS = [
#    'pygtk>=2.0',
#]

setup(
    name='roboticsbase',
    version=roboticsbase.__version__,

    description='',
    long_description=open('README.rst').read(),
    # url='http://www.github.com/psyomn/pypsylbm',
    license='MIT',

    author='TBD',

 #   install_requires=REQUIREMENTS,

    packages=['roboticsbase'],
    zip_safe=False,
    scripts=['roboticsbase/bin/roboticsbase-test']
)

