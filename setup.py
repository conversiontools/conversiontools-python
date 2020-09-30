import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conversiontools",
    version="1.0.0",
    author="Conversion Tools",
    author_email="info@conversiontools.io",
    description="Conversion Tools API Python Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conversiontools/conversiontools-python",
    packages=setuptools.find_packages(),
    keywords=["conversiontools", "api", "client", "conversion", "convert"],
    install_requires=["requests>=2.4.2"],
    project_urls={
        'Documentation': 'https://conversiontools.io/api-documentation',
        'Source': "https://github.com/conversiontools/conversiontools-python",
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7",
    license = "MIT",
)
