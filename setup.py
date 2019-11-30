import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyhomeserver",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A Python package for connecting to your home's smart devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miikama/home-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pyaudio',
        'flask',
        'phue',
        'requests',        
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'hserv = homeserver.cli:main',
    ],
    }
)
