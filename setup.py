import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parsergen",
    version="1.0.0b1",
    author="Conqu3red",
    description="Python library for building Parsers and Lexers Easily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Conqu3red/parsergen",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[]
)