from setuptools import setup
import json

with open("metadata.json") as fp:
    metadata = json.load(fp)

setup(
    name="lexibank_hubercolumbian",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_hubercolumbian"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["hubercolumbian=lexibank_hubercolumbian:Dataset"]},
    install_requires=["pylexibank>=2.1"],
    extras_require={"test": ["pytest-cldf"]},
)
