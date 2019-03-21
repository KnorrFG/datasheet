from setuptools import setup, find_packages

setup(name='datasheet',
      python_requires='>=3.7',
      version='1.0',
      description='A html page generator to present scientific results',
      author='Felix G. Knorr',
      author_email='felix.knorr@tu-dresden.de',
      url='datasheet.readthedocs.io/',
      packages=find_packages(),
      install_requires=[
          "markdown", "pandas", "yattag", "matplotlib", "nibabel", "joblib"
      ],
      license='MIT',
      long_description = """
      * Version: 1.0
      """)
