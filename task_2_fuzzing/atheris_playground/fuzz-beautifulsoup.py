import atheris
import sys
from bs4 import BeautifulSoup


def TestInput(data):
    soup = BeautifulSoup(data)
    soup.prettify()


atheris.Setup(sys.argv, TestInput)
atheris.Fuzz()
