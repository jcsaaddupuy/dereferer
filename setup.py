#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
import version


with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = open("requirements.txt").read()


setup(
    name='dereferer',
    version=version.APP_VERSION,
    description="",
    long_description=readme,
    author="jcsaaddupuy",
    author_email='jcsaaddupuy@fsfe.org',
    url='https://github.com/jcsaaddupuy/dereferer',
    packages= find_packages('.', exclude=['tests*',]),

    # configure the default command line entry point.
    entry_points={
        'console_scripts': [
            'dereferer-manage = dereferer.manage:main',
        ]
    },



    include_package_data=True,
    install_requires=requirements,
    license="WTFPL",
    zip_safe=False,
    keywords='dereferer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
