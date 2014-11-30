#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="conssert",
    version="0.2.9",
    description="Content assertion library for Python",
    url="https://github.com/podio/conssert",
    download_url="https://github.com/podio/conssert/tarball/0.2.9",
    author="Juan Alvarez",
    author_email="juan.afernandez@ymail.com",
    platforms=["any"],
    packages=find_packages(exclude="tests"),
    keywords=["validation", "test", "unit test", "content assertion"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)