Prepare weblate client use

**Role Variables**

.. zuul:rolevar:: weblate_api_credentials

  Complex argument which contains the Weblate server connection
  information. Currently this includes the Weblate server URL and may be
  extended with additional configuration values in the future. It is
  expected that this argument comes from a `Secret`.

    .. zuul:rolevar:: url

        The url to the weblate server
