from setuptools import setup, find_packages

VERSION = "0.7.0"

setup(
    name='wikidataintegrator',
    version=VERSION,
    author='Andra Waagmeester, Greg Stupp, Sebastian Burgstaller-Muehlbacher ',
    author_email='andra@micel.io',
    description='Python package for reading and writing to/from Wikidata',
    license='MIT',
    keywords='Wikidata genewiki biology chemistry medicine ShEx citations',
    url='https://github.com/sulab/WikidataIntegrator',
    packages=find_packages(),
    # packages=['wikidataintegrator',
    #          'wikidataintegrator.ref_handlers', 'wikidataintegrator.wdi_helpers'],
    include_package_data=True,
    ## long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=[
        'requests',
        'python-dateutil',
        'simplejson',
        'pandas',
        'tqdm',
        'mwoauth',
        'oauthlib',
        'sparql_slurper',
        'ShExJSG',
        'jsonasobj',
        'pyshex',
        'backoff'
    ],
)
