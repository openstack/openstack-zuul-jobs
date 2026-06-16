Upload Ansible collections to Galaxy. This is slightly more advanced version
of the ansible-galaxy-import role that respects galaxy.yml in tree of your
project and get the namespace and collection name from it.

It also updates version in galaxy.yml before upload, so that developer does
not need to bother updating version there before each release.

**Role Variables**

.. zuul:rolevar:: ansible_galaxy_info

   Complex argument which contains the information about the ansible-galaxy
   server as well as the authentication information needed. It is
   expected that this argument comes from a `Secret`.

  .. zuul:rolevar:: token
     :default: None

     Ansible Galaxy API token to use for upload.

  .. zuul:rolevar:: url
     :default: https://galaxy.ansible.com

     URL of the GALAXY_SERVER

.. zuul:rolevar:: ansible_galaxy_collection_path
   :default: ${HOME}/{{ zuul.project.src_dir }}

   Path containing collection to upload.

.. zuul:rolevar:: ansible_galaxy_build_collection_path
   :default: /tmp/collection_build/

   Path where collection will be built and packed

.. zuul:rolevar:: ansible_collection_version_tag
   :default: {{ zuul.tag | default('no_version', true) }}

   Current version of the collection to publish. By default,
   matches the issued tag.

.. zuul:rolevar:: ansible_galaxy_virtualenv_path
   :default: ~/.virtualenvs/ansible-galaxy

   Virtual environment where ansible-core will be installed to

.. zuul:rolevar:: ansible_core_version
   :default: None

   ansible-core version that will be installed to the virtualenv.
   Latest available will be installed if not defined.
