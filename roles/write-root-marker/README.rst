Write the root marker for an AFS publishing job

** Role Variables **

.. zuul:rolevar:: sphinx_build_dir
   :default: doc/build

   Directory relative to zuul_work_dir where Sphinx build output was put.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   Directory to operate in.

.. zuul:rolevar:: root_marker_dir
   :default: {{ zuul_work_dir }}/{{ sphinx_build_dir }}/html

   The documentation build directory.  The marker file will be placed
   in this directory.
