#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md', encoding='utf-8') as history_file:
    history = history_file.read()

pomegranate_requires =

setup_requires = [
    'pytest-runner>=2.11.1',
]

setup(
    extras_require={
        'test': tests_require + torch_requires,
        'torch': torch_requires,
        'pomegranate': pomegranate_requires,
        'dev': development_requires + tests_require + torch_requires,
    },
    install_package_data=True,
    install_requires=install_requires,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    packages=find_packages(include=['sdmetrics', 'sdmetrics.*']),
    setup_requires=setup_requires,
    test_suite='tests',
    tests_require=tests_require,
    zip_safe=False,
)
