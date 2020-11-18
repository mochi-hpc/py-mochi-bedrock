import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bedrock",
    version="0.0.1",
    author="Matthieu Dorier",
    author_email="mdorier@anl.gov",
    description="Python interface for Mochi Bedrock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://xgitlab.cels.anl.gov/sds/py-bedrock",
    packages=setuptools.find_packages(),
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
