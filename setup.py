# ! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup for pip package."""

import codecs
import os
import subprocess
import importlib.util
import logging
from itertools import chain
from setuptools import setup, find_packages, Command


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("setup")


here = os.path.abspath(os.path.dirname(__file__))
package_info_path = os.path.join(here, "nemo", "package_info.py")

spec = importlib.util.spec_from_file_location("package_info", package_info_path)
package_info = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_info)

__contact_emails__ = package_info.__contact_emails__
__contact_names__ = package_info.__contact_names__
__description__ = package_info.__description__
__download_url__ = package_info.__download_url__
__homepage__ = package_info.__homepage__
__keywords__ = package_info.__keywords__
__license__ = package_info.__license__
__package_name__ = package_info.__package_name__
__repository_url__ = package_info.__repository_url__
__version__ = package_info.__version__



if os.path.exists('nemo/README.md'):
    with open("nemo/README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    long_description_content_type = "text/markdown"

elif os.path.exists('README.rst'):
    long_description = codecs.open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'),
        'r',
        'utf-8',
    ).read()
    long_description_content_type = "text/x-rst"

else:
    long_description = 'See ' + __homepage__
    long_description_content_type = "text/plain"


###############################################################################
#                             Dependency Loading                              #
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
def req_file(filename, folder="requirements"):
    with open(os.path.join(folder, filename), encoding="utf-8") as f:
        content = f.readlines()
    return [x.strip() for x in content if x.strip() and not x.startswith("#")]


install_requires = req_file("requirements.txt")

extras_require = {
    'test': req_file("requirements_test.txt"),
    'asr': req_file("requirements_asr.txt"),
    'cv': req_file("requirements_cv.txt"),
    'nlp': req_file("requirements_nlp.txt"),
    'tts': req_file("requirements_tts.txt"),
    'text_processing': req_file("requirements_text_processing.txt"),
}

# Flatten extras into one big "all"
extras_require['all'] = list(chain.from_iterable(extras_require.values()))

# TTS depends on ASR
extras_require['tts'] = list(chain(extras_require['tts'], extras_require['asr']))

tests_requirements = extras_require["test"]


###############################################################################
#                            Code style checkers                              #
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

class StyleCommand(Command):
    __LINE_WIDTH = 119
    __ISORT_BASE = (
        'isort '
        '--multi-line=3 --trailing-comma --force-grid-wrap=0 '
        f'--use-parentheses --line-width={__LINE_WIDTH} -rc -ws'
    )
    __BLACK_BASE = f'black --skip-string-normalization --line-length={__LINE_WIDTH}'
    description = 'Checks overall project code style.'
    user_options = [
        ('scope=', None, 'Folder or file to operate within.'),
        ('fix', None, 'True if tries to fix issues in-place.'),
    ]

    def __call_checker(self, base_command, scope, check):
        command = list(base_command)
        command.append(scope)
        if check:
            command.extend(['--check', '--diff'])

        logger.info("Running command: %s", " ".join(command))
        return subprocess.call(command)

    def _isort(self, scope, check):
        return self.__call_checker(self.__ISORT_BASE.split(), scope, check)

    def _black(self, scope, check):
        return self.__call_checker(self.__BLACK_BASE.split(), scope, check)

    def _pass(self):
        logger.info("\033[32mPASS\x1b[0m")

    def _fail(self):
        logger.error("\033[31mFAIL\x1b[0m")

    def initialize_options(self):
        self.scope = '.'
        self.fix = ''

    def finalize_options(self):
        pass

    def run(self):
        scope, check = self.scope, not self.fix
        isort_return = self._isort(scope, check)
        black_return = self._black(scope, check)

        if isort_return == 0 and black_return == 0:
            self._pass()
        else:
            self._fail()
            raise SystemExit(isort_return if isort_return != 0 else black_return)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
setup(
    name=__package_name__,
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url=__repository_url__,
    download_url=__download_url__,
    author=__contact_names__,
    author_email=__contact_emails__,
    maintainer=__contact_names__,
    maintainer_email=__contact_emails__,
    license=__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_requirements,
    extras_require=extras_require,
    include_package_data=True,
    exclude=['tools', 'tests'],
    package_data={'': ['*.tsv', '*.txt', '*.far']},
    zip_safe=False,
    keywords=__keywords__,
    cmdclass={'style': StyleCommand},
)
