from setuptools import setup, find_packages

setup(
    name="audit2-adversarial",
    version="1.0.0",
    description="Monte Carlo failure-cascade simulation with strategic adversary for enterprise audit",
    author="Francesco Orsi",
    url="https://kunskap.substack.com",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "networkx>=3.0",
        "matplotlib>=3.7",
        "scipy>=1.10",
        "seaborn>=0.13",
    ],
)
