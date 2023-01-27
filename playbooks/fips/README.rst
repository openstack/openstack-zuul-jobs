The enable-fips playbook can be invoked to enable FIPS mode on jobs.

This playbook will call the enable-fips role in zuul-jobs, which will
turn FIPS mode on and then reboot the node.  To get consistent results,
this role should be run very early in the node setup process, so that
resources set up later are not affected by the reboot.

In practice, this means that the playbook is invoked as part of a base job
like openstack-multinode-fips for example.  In order to avoid duplicating
complex inheritance trees, we expect to use this base job for most jobs.

As most jobs will not require fips, a playbook variable enable_fips - which
defaults to False - is provided.  To enable FIPS mode, a job will simply need
to set enable_fips to True as a job variable.

**Job Variables**

.. zuul:jobvar:: enable_fips
   :default: False

   Whether to run the playbook and enable fips.  Defaults to False.

