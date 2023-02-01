import os
import re

from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt", encoding="utf8") as file:
    requirements = file.readlines()


def find_version(*filepath):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, *filepath)) as fp:
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", fp.read(), re.M
        )
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name="async_dynamic_batching",
    version=find_version("async_dynamic_batching/__init__.py"),
    author="Tudor Surdoiu",
    author_email="studormarian@gmail.com",
    license="MIT",
    description="Small package that provides zero latency cost dynamic batching for ML model serving for async endpoints handlers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["dyanmic-batch", "inference", "machine-learning"],
    url="https://github.com/DACUS1995/async_dynamic_batching",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)