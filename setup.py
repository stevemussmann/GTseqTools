from setuptools import setup, find_packages
import os

# Read the contents of your README file
setup_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(setup_directory, "README.md"), encoding="utf-8") as f:
	long_description = f.read()

setup(
	name="GTseqTools",
	version="1.0.1",
	author="Steven Mussmann",
	author_email="smussmann@gmail.com",
	description="Filtering, file conversion, and QA/QC of GTseq data.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/stevemussmann/GTseqTools",
	packages=find_packages(),
	install_requires=[
		"matplotlib>=3.10.7",
		"numpy>=2.3.4",
		"openpyxl>=3.1.5",
		"pandas>=2.3.3"
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.12",
)

