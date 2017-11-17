Hack around some requirements being declared in tox_install.sh

.. note:: TODO(mordred) ZOMG DELETE THIS

neutron and horizon plugin repos currently require running the tox_install.sh
script where a list of additional dependencies are listed that are not in
their requirements files. Luckily, tox_install.sh is designed to be run
inside of a virtualenv, so we can just run it in the sphinx ~/.venv and
get them installed. This will let us work towards a solution that does not
involve a custom install script.

**Role Variables**

.. zuul:rolevar:: constraints_file

   Optional path to a constraints file to use.

.. zuul:rolevar:: zuul_work_virtualenv
   :default: ~/.venv

   Virtualenv that sphinx is installed in.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   Directory to operate in.
