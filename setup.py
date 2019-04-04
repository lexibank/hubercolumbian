from setuptools import setup
import sys
import json


PY2 = sys.version_info.major == 2
with open('metadata.json', **({} if PY2 else {'encoding': 'utf-8'})) as fp:
    metadata = json.load(fp)


setup(
    name='lexibank_hubercolumbian',
    version="1.0",
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_hubercolumbian'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'hubercolumbian=lexibank_hubercolumbian:Dataset',
        ]
    },
    install_requires=[
<<<<<<< HEAD
        'pylexibank>=1.0',
=======
        'pylexibank>=0.11',
        'segments>=2.0.1',
>>>>>>> 01da4f1c356d420bc453397241232c6588f94c26
    ]
)
