from setuptools import setup, find_namespace_packages, Extension
import os.path
from os import environ

build_py_bedrock_client = False
if environ.get('BUILD_PY_BEDROCK_CLIENT') is not None:
    build_py_bedrock_client = True

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_pybind11_include():
    path = os.path.dirname(pybind11.__file__)
    return '/'.join(path.split('/')[0:-4] + ['include'])

if build_py_bedrock_client:
    import pybind11
    import pkgconfig
    bedrock_client = pkgconfig.parse('bedrock-client')
    bedrock_ext = Extension('_pybedrock',
                            sources=['mochi/bedrock/src/bedrock.cpp'],
                            libraries=bedrock_client['libraries'],
                            library_dirs=bedrock_client['library_dirs'],
                            include_dirs=bedrock_client['include_dirs'] + [get_pybind11_include()],
                            depends=[])
    ext_modules = [bedrock_ext]
else:
    ext_modules = []

setup(
    name="py-mochi-bedrock",
    version="0.0.1",
    author="Matthieu Dorier",
    author_email="mdorier@anl.gov",
    description="Python interface for Mochi Bedrock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://xgitlab.cels.anl.gov/sds/py-bedrock",
    packages=find_namespace_packages(include=['mochi.*']),
    ext_modules=ext_modules,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "attrs"
    ],
    python_requires='>=3.6',
)
