from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="recipes.native_scoring",
        sources=["recipes/native_scoring.pyx"],
    )
]

setup(
    name="recipe-recommender",
    packages=["recipes"],
    ext_modules=cythonize(
        extensions,
        language_level="3",
    ),
)