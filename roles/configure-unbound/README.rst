An ansible role to dynamically configure DNS forwarders for the
``unbound`` caching service.  IPv6 will be preferred when there is a
usable IPv6 default route, otherwise IPv4.

.. note:: This is not a standalone unbound configuration role.  Base
          setup is done during image builds in
          ``project-config:nodepool/elements/nodepool-base/finalise.d/89-unbound``;
          here we just do dynamic configuration of forwarders based on
          the interfaces available on the actual host.

**Role Variables**

.. zuul:rolevar:: primary_nameserver_v4

   The primary IPv4 nameserver for fowarding requests

.. zuul:rolevar:: primary_nameserver_v6

   The primary IPv6 nameserver for fowarding requests

.. zuul:rolevar:: secondary_nameserver_v4

   The secondary IPv4 nameserver for fowarding requests

.. zuul:rolevar:: secondary_nameserver_v6

   The seconary IPv6 nameserver for fowarding requests
