#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=
# mkvenv: no-deps
""" Debian packaging for the jupyterhub package.

    | Copyright ©  2018, 1&1 Group
    | See LICENSE for details.

    This puts the ``jupyterhub`` Python package and its dependencies as released
    on PyPI into a DEB package, using ``dh-virtualenv``.
    The resulting *omnibus package* is thus easily installed to and removed
    from a machine, but is not a ‘normal’ Debian ``python-*`` package.
    Services are controlled by ``systemd`` units.

    See the `GitHub README`_ for more.

    .. _`GitHub README`: https://github.com/1and1/debianized-jupyterhub
"""
import io
import os
import re
import sys
import json
import textwrap
import subprocess

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from rfc822 import Message as rfc822_headers
except ImportError:
    from email import message_from_file as rfc822_headers

try:
    from setuptools import setup
except ImportError as exc:
    raise RuntimeError("setuptools is missing ({1})".format(exc))


# get external project data (and map Debian version semantics to PEP440)
pkg_version = subprocess.check_output("parsechangelog | grep ^Version:", shell=True)
try:
    pkg_version = pkg_version.decode('ascii')
except (UnicodeDecodeError, AttributeError):
    pass
pkg_version = pkg_version.strip()
upstream_version, maintainer_version = pkg_version.split()[1].rsplit('~', 1)[0].split('-', 1)
maintainer_version = maintainer_version.replace('~~rc', 'rc').replace('~~dev', '.dev')
pypi_version = upstream_version + '.' + maintainer_version

with io.open('debian/control', encoding='utf-8') as control_file:
    data = [x for x in control_file.readlines() if not x.startswith('#')]
    control_cleaned = StringIO(''.join(data))
    deb_source = rfc822_headers(control_cleaned)
    deb_binary = rfc822_headers(control_cleaned)
    if not deb_binary:
        deb_binary = rfc822_headers(StringIO(deb_source.get_payload()))

try:
    doc_string = __doc__.decode('utf-8')
except (UnicodeDecodeError, AttributeError):
    doc_string = __doc__

maintainer, email = re.match(r'(.+) <([^>]+)>', deb_source['Maintainer']).groups()
desc, long_desc = deb_binary['Description'].split('.', 1)
desc, pypi_desc = doc_string.split('\n', 1)
long_desc = textwrap.dedent(pypi_desc) + textwrap.dedent(long_desc).replace('\n.\n', '\n\n')
dev_status = 'Development Status :: 5 - Production/Stable'

# Check for pre-release versions like "1.2-3~~rc1~distro"
if '~~rc' in pkg_version or '~~dev' in pkg_version:
    rc_tag = re.match('.*~~([a-z0-9]+).*', pkg_version).group(1)
    if rc_tag.startswith('dev'):
        rc_tag = '.' + rc_tag
    if rc_tag not in upstream_version:
        upstream_version += rc_tag
    if rc_tag not in pypi_version:
        pypi_version += rc_tag
    dev_status = 'Development Status :: 4 - Beta'

# build setuptools metadata
project = dict(
    name='debianized-' + deb_source['Source'],
    version=pypi_version,
    author=maintainer,
    author_email=email,
    license='BSD 3-clause',
    description=desc.strip(),
    long_description=textwrap.dedent(long_desc).strip(),
    url=deb_source['Homepage'],
    classifiers=[
        # Details at http://pypi.python.org/pypi?:action=list_classifiers
        dev_status,
        'Environment :: Web Environment',
        'Framework :: Jupyter',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Distributed Computing',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)',
    ],
    keywords='jupyterhub deployment debian-packages dh-virtualenv devops omnibus-packages'.split(),
    install_requires=[
        # core
        'jupyterhub==' + upstream_version,
        'notebook==5.7.6',
        'ipython==7.3.0',
        'sudospawner==0.5.2',
        'pycurl==7.43.0.2',  # recommended by server logs

        'Cython==0.29.6',
        'numpy==1.16.2',
        'pandas==0.24.2',
        'tornado==5.1.1',
        'jupyter==1.0.0',
        'ipywidgets==7.4.2',
    ],
    extras_require=dict(
        arrow=['pyarrow==0.12.1', 'csv2parquet==0.0.6'],
        docker=['dockerspawner==0.11.0', 'swarmspawner==0.1.0'],
        parquet=['fastparquet==0.2.1', 'parquet-cli==1.2'],
        nlp=[
            'gensim==3.7.1',  # Topic Modelling in Python
            #'polyglot==16.7.4',  # badly maintained, and setup has Unicode problems
            'spacy==2.0.18',
        ],
        nltk=['nltk==3.4', 'textblob==0.15.3'],
        ml=[
            'scikit-learn==0.20.3',
            'word2vec==0.10.2',
        ],
        spark=['pyspark==2.4.0', 'pyspark-flame==0.2.6'],
        utils=[
            'colour==0.1.5',
            'dfply==0.3.3',
            'jupyter-console==6.0.0',
            'openpyxl==2.6.1',
            'xlsxwriter==1.1.5',
            #'jupytext==1.0.1',  # see https://github.com/mwouts/jupytext/issues/185
        ],
        viz=[
            'seaborn==0.9.0', 'missingno==0.4.1',
            'holoviews[recommended]==1.11.3',
        ],
        vizjs=[
            'plotly==3.7.0', 'cufflinks==0.14.6',
            'bokeh==1.0.4', 'psutil==5.6.1', 'chartify==2.6.0',
            'altair==2.4.1', 'vega==1.4.0', 'vega_datasets==0.7.0',  # needs Python 3.5.3+
            'selenium==3.141.0', 'chromedriver-binary==2.46.0', 'phantomjs-binary==2.1.3',
        ],
    ),
    packages=[],
)


# 'main'
__all__ = ['project']
if __name__ == '__main__':
    if '--metadata' in sys.argv[:2]:
        json.dump(project, sys.stdout, default=repr, indent=4, sort_keys=True)
        sys.stdout.write('\n')
    elif '--tag' in sys.argv[:2]:
        subprocess.call("git tag -a 'v{version}' -m 'Release v{version}'"
                        .format(version=pypi_version), shell=True)
    else:
        setup(**project)
