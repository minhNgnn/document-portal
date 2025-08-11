from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(

    name="document-portal",
    version="0.1",
    author="Minh",
    packages=find_packages(),
    install_requires = requirements,
)