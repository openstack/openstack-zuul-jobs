Write the root marker for an AFS publishing job

** Role Variables **

.. zuul:rolevar:: root_marker_dir
   :default: src/{{ zuul.project.canonical_name }}/doc/build/html

   The documentation build directory.  The marker file will be placed
   in this directory.
