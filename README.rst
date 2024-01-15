LFRic GPL Tools
===============

The LFRic project is licensed using the BSD 3-Caluse licence. As such it
cannot be mixed with GPL licensed software. Unfortunately our own Rose
tool is so licensed.

This is a problem because we avoid duplication and maintain a single source
of truth by deriving our configuration loading code from the Rose metadata
used to create the namelists. In order to avoid duplicating the code to
ready the metadata file the "rose picker" tool was created.

Rose Picker
~~~~~~~~~~~

Rose Picker uses Rose code (which has to be copied into the repository
since we can't easily import it from Git) to read the metadata file and
converts it into an intermediate JSON file. This can be read by our
configuration reading code generator scripts without mixing licenses.

Installation
~~~~~~~~~~~~

These tools can be installed in the usual way using ``pip install .``.
