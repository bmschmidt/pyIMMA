# (C) British Crown Copyright 2018, Met Office
#
# This code is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#

"""
This module provides a Python API to `IMMA files <http://icoads.noaa.gov/e-doc/imma>`_.

IMMA files are not necessarily consistent in their contents - each line can have a different set of extensions. So we can't treat the file as a table of data - instead we treat it as a list of records, and read those records one at a time.

So an IMMA file is best thought of as an `iterator <https://anandology.com/python-practice-book/iterators.html>`_. Set up a file as an iterator with the  :meth:`get` function:

.. code-block:: python

    import IMMA
    iobs=IMMA.get('some_file.imma')

Then every time you call ``iobs.next()`` you will get the next record from ``some_file.imma``.

Each record is returned as a :obj:`dict` where vthe keys are the IMMA variable names. So after ``rec=iobs.next()``, the sea-surface temperature is in ``rec['SST']``.

If you want all the records in the file loaded simultaniously, either use ``obs=list(iobs)`` or call the :func:`read` function:

.. code-block:: python

    obs=IMMA.read('some_file.imma')

In both cases ``obs`` will be a list of dictionaries. So ``obs[3]['SST']`` will be the SST from the fourth record in the file. If you want a list of all the SSTs in the file, you need something like:

.. code-block:: python

   SSTs=[ob['SST'] for ob in obs]

``SST`` is in the ``core`` extension, so ``rec['SST']`` will either have a valid number, or be ``None`` (blank in the IMMA record). If you look for a variable in an extension other than ``core`` it may be that the extension is not present in the selected record. In this case looking for it will raise a ``KeyError``. I.e. ``rec['DCK']`` might be a valid deck ID, it might be ``None`` (if the ``ICOADS`` extension is present but the DCK entry is blank) or it might raise a ``KeyError`` (if the ICOADS extension is missing from that record).

To output records to a file, first ``open`` the file, and then :func:`write` records to it one at a time:

.. code-block:: python

   opfile=open('some_output_file.imma','w')
   for ob in obs:
       IMMA.write(ob,opfile)

The list of extensions to write to the file is controlled by ``ob['extensions']`` - an integer array containing the ``extension_id`` for all the extensions in the record. You need to update this explicitly - if you add or delete extensions from a record, update this array.

|
"""

from .structure import attachment
from .structure import parameters
from .structure import definitions
from .read import *
from .write import *

