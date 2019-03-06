from setuptools import setup, find_packages

setup(name='data-sheet',
      python_requires='>=3.7',
      version='0.1',
      description='A html page generator to present scientific results',
      author='Felix Knorr',
      author_email='felix.knorr@tu-dresden.de',
      url='knorrfg.github.io',
      packages=find_packages(),
      install_requires=[
          "markdown", "pandas", "yattag", "matplotlib", "nibabel", "joblib"
      ],
      license='MIT')
