import os
from setuptools import setup, find_packages
import warnings

setup(
    name='cloud-compose-datadog',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=6.6',
        'datadog>=0.12.0',
        'cloud-compose>=0.3.0',
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
    ],
    namespace_packages = ['cloudcompose'],
    author="Daniel Hoerauf and the WaPo platform tools team",
    author_email="opensource@washingtonpost.com",
    url="https://github.com/cloud-compose/cloud-compose-datadog",
    download_url = "https://github.com/cloud-compose/cloud-compose-datadog/archive/master.zip",
    keywords = ['cloud', 'compose', 'datadog', 'monitoring'],
    classifiers = []
)
