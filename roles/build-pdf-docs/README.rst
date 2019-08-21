Build PDFs from sphinx documents

If the tox environment specified in `tox_pdf_envlist`
does not exist, the PDF build will be skipped.

**Role Variables**

.. zuul:rolevar:: tox_pdf_envlist
   :default: pdf-docs

   The tox environment used for PDF doc build.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   The location of the main working directory of the job.
