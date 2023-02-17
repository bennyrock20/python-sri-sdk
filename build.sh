#!/bin/bash

pipenv run python -m build && pipenv run python -m twine upload --repository testpypi dist/*
