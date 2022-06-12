from distutils.core import setup

NAME = "envc"
VERSION = "0.1.0"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description="Loads configuration from environment using type hints",
    url="",
    author="Murad Byashimov",
    author_email="byashimov@gmail.com",
    packages=[NAME],
    package_dir={NAME: "lib"},
    package_data={
        NAME: ["LICENSE"],
    },
    keywords=["envconfig", "configuration"],
    license="MIT",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
