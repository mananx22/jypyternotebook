from setuptools import find_packages,setup
from typing import List
def fetcher(file:str)->List[str]:
    requirements = []
    with open(file) as file_obj:
        requirements = file_obj.readlines()
        requirements = [k.replace("\n","") for k in requirements]
        if "-e ." in requirements:
            requirements.remove("-e .")
        return requirements



setup(name="mlproject",
      version='0.0.1',
      author='manan',
      packages=find_packages(),
      install_requires=fetcher('requirements.txt'),
      )