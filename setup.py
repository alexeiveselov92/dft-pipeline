from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dft",
    version="0.1.0",
    author="DFT Team",
    author_email="team@dft.com",
    description="Data Flow Tools - flexible ETL pipeline framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "pyarrow>=12.0.0",
        "jinja2>=3.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "dft=dft.cli.main:cli",
        ],
    },
)