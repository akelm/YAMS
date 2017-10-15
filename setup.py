from distutils.core import setup
from Cython.Build import cythonize

# extensions = [Extension("*", ["yamsx/*.pyx"])]

setup(
    ext_modules = cythonize("yamsx/yams.pyx")
)