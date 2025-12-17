Rose Picker
===========

Rose Picker uses Rose code (which has to be copied into the repository since we
can't easily import it from Git) to read the metadata file and converts it into
an intermediate JSON file. This can be read by our configuration reading code
generator scripts without mixing licenses.

Installation
~~~~~~~~~~~~

These tools can be installed in the usual way using ``pip install .``.

Why is it licenced differently to LFRic?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LFRic is distributed under the BSD 3-Clause license, while the Rose tool is
released under the GPL license. As Rose Picker incorporates code from Rose, it
must comply with the GPL licensing terms.
