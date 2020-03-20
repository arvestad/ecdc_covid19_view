import setuptools

def read_version_string(filename):
    versionstring = None
    with open(filename) as h:
        for line in h:
            try:
                identifier, equalsign, versionstring = line.split()
                if identifier == '__version__' and equalsign == '=':
                    return versionstring.strip("'")
            except:
                continue        # Just read past lines to fitting the pattern
    if versionstring is None:
        return 'unknown_version'

__version__ = read_version_string('ecdc_covid19_view/version.py')


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ecdc_covid19_view',
    version=__version__,
    author='Lars Arvestad',
    author_email='arve@math.su.se',
    description="Program for reading ECDC's Excel sheets for CIVD-19 data and make simple visualisations",
    long_description=long_description,
    long_description_content_type="text/markdown; charset=UTF-8",
    url='https://github.com/arvestad/ecdc_covid19_view',
    license='GPLv3',
    packages = setuptools.find_packages(),
    entry_points={
        'console_scripts':[
            'ecdc_covid19_view = ecdc_covid19_view.main:main'
        ]
    },
    install_requires=[
        'pandas'
    ],

)
