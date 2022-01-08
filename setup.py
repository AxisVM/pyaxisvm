# -*- coding: utf-8 -*-
import setuptools
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


with open("README.md", "r") as fh:
    long_description = fh.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()
#required.append('comtypes @ https://github.com/AxisVM/comtypes/archive/refs/tags/v1.0.0.zip')


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="axisvm",                     
    version=get_version("src/axisvm/__init__.py"),                        
    author="InterCAD Ltd.",
    author_email = 'bbalogh@axisvm.eu',
    url = 'https://github.com/AxisVM/pyaxisvm',   
    download_url = 'https://github.com/AxisVM/pyaxisvm/releases',                     
    keywords = ['AxisVM', 'Axis', 'Civil Engineering'],
    description="A Python package for AxisVM",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where='src'),   
    classifiers=[
        'Development Status :: 5 - Production/Stable',     
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',                             
    package_dir={'':'src'},
	install_requires=required
)

