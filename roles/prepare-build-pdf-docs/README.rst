Install Packages for build-pdf-docs

Install binary packages for :zuul:role:`build-pdf-docs`.

This role currently only supports Ubuntu Bionic.

If the tox environment specified in `tox_pdf_envlist`
does not exist, package installation will be skipped.

**Role Variables**

.. zuul:rolevar:: tox_pdf_envlist
   :default: pdf-docs

   The tox environment used for PDF doc building.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   The location of the main working directory of the job.
