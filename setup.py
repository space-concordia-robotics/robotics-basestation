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
    url='https://github.com/space-concordia-robotics/robotics-basestation',
    license='MIT',

    author='TBD',

    #dependencies
    install_requires=['roboticsnet'],
    dependency_links=['https://github.com/space-concordia-robotics/robotics-networking/tarball/master'],

    packages=['roboticsbase'],
    zip_safe=False,
    scripts=['roboticsbase/bin/roboticsbase-test']
    
)

