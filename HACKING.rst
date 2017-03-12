================
Hacking the code
================

The tests suite uses pytest and tox.

It assumes you have `tox` installed (`tox` is the kind of tool, which is best when install
globally but that is not required).

Run the tests via tox
=====================
::

    $ tox

It creates set of virtualenvs in directory `.tox`. The number depends on number of python
interpreter version you have available.

Activating particular virtualenv
================================
Assuming you have already run the `tox` command, you can activate any of created virtualenvs::

    $ source .tox/py27/bin/activate
    (py27)$

or on MS Windows::

    $ .tox/py27/Scripts/activate.bat
    (py27)$


Running tests in particular virtualenv
======================================
`pytest` is installed into `tox` created virtulanev (as it is present in `test_requirements.txt`.

To run tests in tests directory::

    (py27)$ pytest tests

To run doctests::

    (py27)$ pytest --doctest-modules autorepr.py

Use any other pytest switches (e.g. `-sv` to get more verbose output and see what got printed to
stdout by test cases.
