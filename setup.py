import os
from setuptools import setup, find_packages
from subprocess import check_output
from subprocess import CalledProcessError

setup_path = os.path.dirname(__file__)

print("setup_path: {}".format(setup_path))


def read(fname):
    return open(os.path.join(setup_path, fname)).read()

MAJOR_VERSION = 0
MINOR_VERSION = 0
REPO_URL = 'https://github.com/sebotic/WikidataIntegrator'

version_file = os.path.join(setup_path, 'VERSION')

try:
    MICRO_VERSION = int(check_output("git rev-list --count master", shell=True).decode('utf-8').strip('\n'))

    f = open(version_file, 'w')
    f.write("{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION))
    f.close()
except:
    if os.path.isfile(version_file):
        f = open(version_file, 'rt')
        version_string = f.readline()
        MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION = version_string.split('.')
    else:
        MICRO_VERSION = 1

# Calculate commit hash
try:
    commit_hash = check_output("git rev-parse HEAD", shell=True).decode('utf-8').strip('\n')
except CalledProcessError:
    commit_hash = ''

f = open('./.git-commit-hash', 'w')
f.write("{}.git\n{}".format(REPO_URL, commit_hash))
f.close()

setup(
    name='wikidataintegrator',
    version="{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION),
    author='Sebastian Burgstaller-Muehlbacher, Greg Stupp, Andra Waagmeester',
    author_email='sburgs@scripps.edu',
    description='Python package for reading and writing to/from Wikidata',
    license='AGPLv3',
    keywords='Wikidata biology chemistry medicine',
    url=REPO_URL,
    download_url='https://github.com/sebotic/WikidataIntegrator/tarball/0.0.325',
    # packages=find_packages(),
    packages=['wikidataintegrator', 'wikidataintegrator.backoff'],
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
