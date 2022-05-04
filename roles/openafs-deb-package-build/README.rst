Build OpenAFS Ubuntu Packages

This builds openafs source packages and, with the publishing steps,
pushes them to be built by as an Ubuntu PPA.

OpenDev has traditionally kept separate OpenAFS packages in a PPA
which are used by production hosts.  In the past the LTS distro
versions have had bugs, or lacked support for architectures/kernels
(ARM64 + HWE kernels, practically) we needed -- necessitating keeping
separate, fresh versions.

Upstream packages keep a PPA at
https://launchpad.net/~openafs/+archive/ubuntu/stable

As much as possible, we generally import and use their debian/*
infrastructure (including patches, etc.) as a base here.  This PPA
doesn't build all the architectures we need, but also isn't focused on
the immediate needs of OpenDev production; thus despite it's regular
maintence it is still helpful for us to have our own package builds.

These problems are much less with current distros (>= 2022) and
openafs 1.8 series; our goal is to generally carry no differences.

Note the openafs-rpm-package-build jobs are a counter-part to this, as
OpenAFS hasn't been available on RPM distros.  We try to keep these in
sync so our infrastructure is more or less at the same level.
