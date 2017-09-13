|License LGPL-3| | |Build Status| | |Test Coverage| | |Code Climate|

========
Reverend
========

Reverend is a simple Bayesian classifier.
It is designed to be easy to adapt and extend for
your application.

Usage
=====

* `Read The API Documentation <https://laslabs.github.io/python-reverend>`_

A simple example would look like:

.. code-block:: python

   from reverend.thomas import Bayes

   guesser = Bayes()
   guesser.train('fish', 'salmon trout cod carp')
   guesser.train('fowl', 'hen chicken duck goose')

   guesser.guess('chicken tikka marsala')

   You can also "forget" some training:
   guesser.untrain('fish', 'salmon carp')

The first argument of ``train`` is the bucket or class that
you want associated with the training. If the bucket does not
exist, Bayes will create it.

The second argument is the object that you want Bayes to be
trained on. By default, Bayes expects a string and uses something
like ``string.split`` to break it into individual tokens (words).
It uses these tokens as the basis of its bookkeeping.


The two ways to extend it are:
1. Pass in a function as the tokenizer when creating
   your Bayes. The function should expect one argument
   which will be whatever you pass to the train() method.
   The function should return a list of strings, which
   are the tokens that are relevant to your app.

2. Subclass Bayes and override the method getTokens to
   return a list of string tokens relevant to your app.

Known Issues / Road Map
=======================

Credits
=======

Contributors
------------

* Amir Bakhtiar <amir@divmod.org>
* `Jean-Paul Calderone <https://launchpad.net/~exarkun>`_
* `Tristan Seligmann <https://launchpad.net/~mithrandi>`_
* `Allen Short <https://launchpad.net/~washort>`_
* Dave Lasley <dave@laslabs.com>

Maintainer
----------

.. image:: https://laslabs.com/logo.png
   :alt: LasLabs Inc.
   :target: https://laslabs.com

This module is maintained by LasLabs Inc.

It was migrated from the `Launchpad Divmod Project <https://launchpad.net/divmod>`_,
which is no longer maintained.

.. |Build Status| image:: https://api.travis-ci.org/LasLabs/python-reverend.svg?branch=master
   :target: https://travis-ci.org/LasLabs/python-reverend
.. |Test Coverage| image:: https://codecov.io/gh/LasLabs/python-reverend/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/LasLabs/python-reverend
.. |Code Climate| image:: https://codeclimate.com/github/LasLabs/python-reverend/badges/gpa.svg
   :target: https://codeclimate.com/github/LasLabs/python-reverend
.. |License LGPL-3| image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3
