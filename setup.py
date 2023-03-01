import codecs
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
long_desc = ""

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_desc = "\n" + f.read()


setup(
    long_description_content_type="text/markdown",
    long_description=long_desc,
)
