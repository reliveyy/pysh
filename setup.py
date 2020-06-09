from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pysh",
    version="1.0.0.dev1",
    description="A python implemented shell with very limited features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reliveyy/pysh",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8"
)
