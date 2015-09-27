from setuptools import setup, find_packages

import roboticsbase

# requirements and links can be added and removed here. PyGTK does not support distutils on linux so it is not included for now.
REQUIREMENTS = [
    'pygame'
]

DEPENDENCY_LINKS = [
    'https://github.com/space-concordia-robotics/robotics-networking/tarball/master#egg=roboticsnet-0.1.0',
]

setup(
    name='roboticsbase',
    version=roboticsbase.__version__,

    description='',
    long_description=open('README.rst').read(),
    url='https://github.com/space-concordia-robotics/robotics-basestation',
    license='MIT',

    author='TBD',

    install_requires=REQUIREMENTS,
    dependency_links=DEPENDENCY_LINKS,

    packages=['roboticsbase'],
    zip_safe=False,
    scripts=['roboticsbase/bin/roboticsbase-test'],
    test_suite="test"

)

