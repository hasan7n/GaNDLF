#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
  readme = readme_file.read()

requirements = [
  'nibabel',
  'numpy',
  'scipy',
  'SimpleITK',
  'torch>=1.2',
  'torchvision',
  'tqdm',
]

setup(
  author="Megh Bhalerao, Siddhesh Thakur, Sarthak Pati",
  author_email='software@cbica.upenn.edu',
  python_requires='>=3.6',
  classifiers=[
    'Development Status :: Pre-Alpha',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD-3-Clause License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
  description=(
    "Semantic segmenation using various DL architectures"
    " on PyTorch."
  ),
  install_requires=requirements,
  license="BSD-3-Clause License",
  long_description=readme,
  long_description_content_type='text/markdown',
  include_package_data=True,
  keywords='segmentation, semantic, brain, breast',
  name='deep-seg',
  dependency_links=['https://github.com/sarthakpati/torchio/tarball/master#egg=repo-v0.17.10'],
  # url='https://github.com/fepegar/torchio',
  version='0.0.1',
  zip_safe=False,
)