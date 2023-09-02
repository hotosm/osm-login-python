import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["itsdangerous~=2.1.2", "pydantic~=2.3.0", "requests_oauthlib~=1.3.1"]

setuptools.setup(
    name="osm-login-python",
    version="1.0.0",
    author="Kshitij Raj Sharma",
    author_email="skshitizraj@gmail.com",
    description="Use OSM Token exchange with OAuth2.0 for python projects",
    license="BSD-3-Clause",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kshitijrajsharma/osm-login-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    requires_python=">=3.0",
)
