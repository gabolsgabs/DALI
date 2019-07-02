from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='DALI-dataset',
      version='1.0.0',
      description='Code for working with the DALI dataset',
      url='http://github.com/gabolsgabs/DALI',
      author='Gabriel Meseguer Brocal',
      author_email='gabriel.meseguer.brocal@ircam.fr',
      license='afl-3.0',
      long_description=long_description,
      long_description_content_type="text/markdown",
      #  https://help.github.com/articles/licensing-a-repository/#disclaimer
      packages=['DALI'],
      include_package_data=True,
      install_requires=['youtube_dl',],
      zip_safe=False)
