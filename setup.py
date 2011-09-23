from setuptools import setup

setup(name="dectest",
      version="0.1",
      author="Laurie Clark-Michalek",
      author_email="bluepeppers@archlinux.us",
      maintainer="Laurie Clark-Michalek",
      maintainer_email="bluepeppers@archlinux.us",
      description=("A testing library/framework for lazy and decorator " + 
                   "based testing."),
      platform=["linux"],
      license="lgpl",
      
      package_dir={"dectest": "dectest"},
      packages=["dectest"],
      )
      
