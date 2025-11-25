Extract the `env_dir`__ used for a tox `test environment (testenv)`__.

.. __: https://tox.wiki/en/latest/config.html#env_dir
.. __: https://tox.wiki/en/latest/user_guide.html#test-environments

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   The location of the main working directory of the job.

.. zuul:rolevar:: tox_env

   The tox testenv to extract the ``env_dir`` for.
