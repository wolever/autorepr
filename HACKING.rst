Run tests via tox
=================
::

    $ pip install 'tox>=2.6'
    $ tox

And tests will be run against each Python interpreter you have installed.


Activating particular virtualenv
================================

Assuming you have already run the ``tox`` command, you can activate any of
created virtualenvs::

    $ source .tox/py27/bin/activate
    (py27)$

or on Windows::

    $ .tox/py27/Scripts/activate.bat
    (py27)$


Running tests in particular virtualenv
======================================

``nose`` is installed into ``tox`` created virtulanev (as it is present in
``test_requirements.txt``).

To run the tests::

    (py27)$ nosetests

To run doctests::

    (py27)$ python autorepr.py
