from setuptools import setup, find_packages
import sys

# ParetoBench needed Python 3 to run
if sys.version_info.major != 3:
    raise RuntimeError("PhenoGraph requires Python 3")

main_info = {}

# get version and description
with open("ParetoBench/version.py") as f:
    exec(f.read(), main_info)
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ParetoBench",
    description="Integrated multi-perspective evaluation of clustering algorithms using Pareto fronts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=main_info["__version__"],
    author=main_info["__author__"],
    author_email=main_info["__email__"],
    packages=find_packages(),
    zip_safe=False,
    url="https://github.com/ghar1821/ParetoBench.git",
    license="LICENSE",
    install_requires=open("requirements.txt").read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    python_requires=">=3.6",
)