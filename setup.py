from setuptools import setup, find_packages

setup(
    name="hypnobot",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
) 