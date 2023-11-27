#!/usr/bin/env bash

if [[ "$VIRTUAL_ENV" == "" ]]
then
    source env/bin/activate
fi

echo "isorting .py files"
isort *.py

echo "pep8"
pep8 *.py
if [[ "$?" != 0 ]]
then
    exit $?
fi
echo "- good"

echo "flake8"
flake8 *.py
if [[ "$?" != 0 ]]
then
    exit $?
fi
echo "- good"

