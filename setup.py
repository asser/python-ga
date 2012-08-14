from distutils.core import setup

setup(
    name='googleanalytics',
    version='0.1.0',
    author='Asser Schrøder Femø',
    author_email='asser@diku.dk',
    packages=['googleanalytics','googleanalytics.test'],
    scripts=[],
    url='http://github.com/asser/python-ga',
    license='LICENSE.txt',
    description='Google Analytics client',
    long_description=open('README.md').read(),
)

