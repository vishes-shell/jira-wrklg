#!/usr/bin/env python

import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


setup(
    name="jira-wrklg",
    python_requires=">=3.7",
    version=get_version("jira_wrklg"),
    description="Utils to ease fetch of jira issue worklogs",
    author="Alex Shalynin",
    py_modules=["jira_wrklg"],
    packages=find_packages(exclude=("tests/*",)),
    install_requires=["jira>=2.0.0,<2.1", "click>=7.0,<8"],
    entry_points={"console_scripts": ["jira-wrklg=jira_wrklg.__main__:cli"]},
    zip_safe=False,
)
