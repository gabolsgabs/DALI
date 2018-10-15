from setuptools import setup

setup(name='DALI_dataset',
      version='1.0',
      description='Code for working with the DALI dataset',
      url='http://github.com/gabolsgabs/DALI',
      author='Gabriel Meseguer Brocal',
      author_email='gabriel.meseguer.brocal@ircam.fr',
      license='afl-3.0',
      #  https://help.github.com/articles/licensing-a-repository/#disclaimer
      packages=['DALI'],
      include_package_data=True,
      zip_safe=False)
