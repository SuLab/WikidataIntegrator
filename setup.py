from setuptools import setup, find_packages

MAJOR_VERSION = 0
MINOR_VERSION = 0
MICRO_VERSION = 498

REPO_URL = 'https://github.com/sulab/WikidataIntegrator'

setup(
    name='wikidataintegrator',
    version="{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION),
    author='Sebastian Burgstaller-Muehlbacher, Greg Stupp, Andra Waagmeester',
    author_email='sburgs@scripps.edu',
    description='Python package for reading and writing to/from Wikidata',
    license='MIT',
    keywords='Wikidata biology chemistry medicine',
    url=REPO_URL,
    # packages=find_packages(),
    packages=['wikidataintegrator', 'wikidataintegrator.backoff', 'wikidataintegrator.ref_handlers'],
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
        'pandas',
        'python-dateutil',
        'simplejson',
        'mwoauth',
    ],
)
