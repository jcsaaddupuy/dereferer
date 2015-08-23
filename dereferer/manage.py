# coding: utf-8
import os

from flask.ext.script import Manager
from dereferer.app import app

manager = Manager(app)
root_directory = os.path.abspath(os.path.dirname(__file__))


def main():
    manager.run()

if __name__ == "__main__":
    main()

