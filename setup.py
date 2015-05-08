from setuptools import setup, find_packages

import roboticsbase

setup(
    name='roboticsbase',
    version=roboticsbase.__version__,

    description='',
    long_description=open('README.rst').read(),
    # url='http://www.github.com/psyomn/pypsylbm',
    license='MIT',

    author='TBD',

    packages=['roboticsbase'],
    zip_safe=False,
    scripts=['roboticsbase/bin/roboticsbase-test']
)
