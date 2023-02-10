import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='python-sri-sdk',
    version='1.0.0',
    author='William Tapa',
    author_email='info@rushdelivery.app',
    description='SRI provides a simple interface to the SRI API.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/bennyrock20/python-sri-sdk',
    project_urls={
        "Bug Tracker": "https://github.com/bennyrock20/python-sri-sdk/issues"
    },
    license='MIT',
    packages=['sri'],
    install_requires=[
        'zeep====4.2.1',
        'jinja2==3.0.3',
        'pydantic==1.8.2',
        'signxml==3.0.0',
    ],
)