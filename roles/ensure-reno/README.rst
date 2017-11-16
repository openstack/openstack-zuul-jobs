Ensure reno is installed

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   Directory to operate in. Needed only for a little while until we have
   projects migrated to not need to be installed just to generate
   release notes.
