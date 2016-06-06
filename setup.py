import os
from setuptools import setup, find_packages
import warnings

setup(
    name='cloud-compose-monitoring',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=6.6',
        'boto3>=1.3.1',
        'botocore>=1.4.14',
        'datadog>=0.12.0',
        'docutils>=0.12',
        'futures>=3.0.5',
        'Jinja2>=2.8',
        'jmespath>=0.9.0',
        'MarkupSafe>=0.23',
        'cloud-compose>=0.3.0',
        'python-dateutil>=2.5.3',
        'PyYAML>=3.11',
        'retrying>=1.3.3',
        'six>=1.10.0'
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
