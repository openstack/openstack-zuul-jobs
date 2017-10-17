Prepare built OpenStack docs to be published to the OpenStack AFS cell.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   Directory to build documentation in.

.. zuul:rolevar:: doc_build_dir
   :default: {{ zuul_work_dir }}/doc/build

   Directory that contains the built documentation.
