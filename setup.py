#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python pluggable.core
"""

from setuptools import setup, find_namespace_packages

from Cython.Build import cythonize


install_requires = ["aioworker"]
extras_require = {}
extras_require['test'] = [
    "pytest",
    "pytest-mock",
    "coverage",
    "cython",
    "pytest-coverage",
    "codecov",
    "flake8"],

setup(
    name='pluggable.core',
    version='0.1.0',
    description='pluggable.core',
    long_description="pluggable.core",
    url='https://github.com/phlax/pluggable.core',
    author='Ryan Northey',
    author_email='ryan@synca.io',
    license='GPL3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Programming Language :: Python :: 3.5',
    ],
    keywords='python pluggable',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_namespace_packages(),
    namespace_packages=["pluggable"],
    ext_modules=(
        cythonize("pluggable/core/*.pyx", annotate=True)
        + cythonize("pluggable/core/auth/*.pyx", annotate=True)
        + cythonize("pluggable/core/managers/*.pyx", annotate=True)),
    include_package_data=True)
