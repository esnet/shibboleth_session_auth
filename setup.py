from setuptools import setup
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

try:
    # Use pandoc to convert .md -> .rst when uploading to pypi
    import pypandoc
    DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError):
    with open(path.join(here, "README.md"), encoding="utf-8") as f:
        DESCRIPTION = f.read()


if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    sys.exit('Sorry, Python 2 < 2.7 is not supported')

if sys.version_info[0] == 3:
    sys.exit('Sorry, Python 3 is not supported')

setup(
    name="django-shibboleth-session-auth",

    version="0.6.0",

    description="Simplistic Shibboleth integration for Django sessions",
    long_description=DESCRIPTION,
    url="https://github.com/esnet/shibboleth_session_auth",

    author="Jon M. Dugan",
    author_email="jdugan@es.net",

    license="BSD",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: Python :: 2.7",
    ],

    keywords="Django Shibboleth",

    packages=["shibboleth_session_auth"],

    install_requires=[
    ],

)
