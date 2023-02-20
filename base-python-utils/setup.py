from setuptools import setup

EXTRAS_REQUIRE = {
    "settings": [
        "pydantic<2",
    ],
}

EXTRAS_REQUIRE["all"] = list(set(sum(EXTRAS_REQUIRE.values(), [])))

REQUIRES = []


setup(
    name="meysam-utils",
    version="0.1.0",
    description="A set of repetitive utilities that I'm using everywhere with the same code",
    packages=["meysam_utils"],
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.7",
)
