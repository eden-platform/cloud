# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# get version from __version__ variable in press/__init__.py
from press import __version__ as version

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")


setup(
	name="cloud",
	version=version,
	description="Cloud Management System for Eden Platform",
	author="Don't Panic Consulting",
	author_email="support@dpcco.me",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
	entry_points={"console_scripts": ["backbone = backbone.cli:cli"]},
)
