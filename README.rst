================
The Best Spinner
================

`The Best Spinner`_ is a windows desktop application for spinning text (synonym substitution) to create unique version(s) of existing text. This package provides a way to easily interact with The Best Spinner API (requires an account, get one from `this site`__)

Installation
============

Install into your python path using pip or easy_install::

    pip install tbs
    easy_install tbs
            

Usage
=====

>>> original_text = "This is the text we want to spin"
>>> import tbs
>>> tbs = tbs.Api('your_username', 'your_password')
>>> spin_text = tbs.identifySynonyms(text)
>>> print spin_text
u"{This is|This really is|That is|This can be} some text that we'd {like to
|prefer to|want to|love to} spin"
>>> tbs.randomSpin(spin_text)
u"This really is some text that we'd love to spin"


Docs
====

See `tbs docs`_.

.. _`The Best Spinner`: http://snurl.com/the-best-spinner 
__ `The Best Spinner`_
.. _`tbs docs`: http://www.whywouldwe.com/the-best-spinner
