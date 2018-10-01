from setuptools import setup, find_packages

VERSION = "0.1.1"

setup(
    name='wikidataintegrator',
    version=VERSION,
    author='Sebastian Burgstaller-Muehlbacher, Greg Stupp, Andra Waagmeester',
    author_email='sburgs@scripps.edu',
    description='Python package for reading and writing to/from Wikidata',
    license='MIT',
    keywords='Wikidata biology chemistry medicine',
    url='https://github.com/sulab/WikidataIntegrator',
    packages=find_packages(),
    # packages=['wikidataintegrator', 'wikidataintegrator.backoff',
    #          'wikidataintegrator.ref_handlers', 'wikidataintegrator.wdi_helpers'],
    include_package_data=True,
    # long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=[
        'requests',
        'python-dateutil',
        'simplejson',
        'mwoauth',
    ],
)
