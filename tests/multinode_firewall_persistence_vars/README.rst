multinode_firewall_persistence_vars
===================================

This directory is meant to contain distribution specific variables used in
integration tests for the ``multinode_firewall_persistence`` role.

The behavior of the ``with_first_found`` lookup used with the ``include_vars``
module will make it search for the ``vars`` directory in the "usual" order of
precedence which means if there is a ``vars`` directory inside the playbook
directory, it will search there first.

This can result in one of two issues:

1. If you try to prepend ``{{ role_path }}`` to workaround this issue with the
   variable file paths, Zuul will deny the lookup if you are running an
   untrusted playbook because the role was prepared in a trusted location and
   Ansible is trying to search outside the work root as a result.
2. The variables included are the wrong ones -- the ones from
   ``playbooks/vars`` are loaded instead of ``path/to/<role>/vars``

This is why this directory is called ``multinode_firewall_persistence_vars``.
