#!/bin/bash -xe

# Working variables
WHEELHOUSE_DIR=$1
WORKING_DIR=$(pwd)/src/opendev.org/openstack/requirements
PYTHON_VERSION=$2
LOGS=$(pwd)/logs

FAIL_LOG=${LOGS}/failed.txt

# NOTE(ianw) : Some Python 3 platforms (>= 9-stream) are deprecating
# virtualenv.  When we finally ditch Python 2 platforms, just use
# python3 -m venv everywhere.
if [[ ${PYTHON_VERSION} =~ python2 ]]; then
    VIRTUALENV_CMD="virtualenv -p $PYTHON_VERSION"
else
    VIRTUALENV_CMD="${PYTHON_VERSION} -m venv"
fi

# preclean logs
mkdir -p ${LOGS}
rm -rf ${LOGS}/*

# output everything to a logfile incase we are killed in flight
exec 1> ${LOGS}/wheel-build.sh.log
exec 2>&1

# Extract and iterate over all the branch names.
if [[ $(uname -m) != 'x86_64' ]] || $(lsb_release -a 2>&1 | grep -q bullseye) ; then
    # Because arm64 has so many more wheels to make, we limit to just the latest
    # two branches.  Bullseye is using Python 3.9 by default and also
    # has to build too much at this stage, so we do similar there.
    BRANCHES=$(git --git-dir=$WORKING_DIR/.git branch -a | grep '^  stable' | \
                   tail -2)
else
    BRANCHES=$(git --git-dir=$WORKING_DIR/.git branch -a | grep '^  stable' | \
                      grep -Ev '(newton)')
fi
for BRANCH in master $BRANCHES; do
    git --git-dir=$WORKING_DIR/.git show $BRANCH:upper-constraints.txt \
        2>/dev/null > /tmp/upper-constraints.txt  || true

    # TODO(ianw) 2020-06: these are taking like 2000 seconds each to
    # build on arm64 and blowing out the build past a reasonable
    # timeout.  It only seems to happen with the master versions for
    # now (scipy===1.4.1 and scikit-learn===0.23.1, at least).  It
    # seems like they should not take that long; skip until someone
    # can investigate thoroughly.
    if [[ $(uname -m) != 'x86_64' && ${BRANCH} == 'master' ]]; then
        sed -i -e '/^scipy.*/d' -e '/^scikit-learn.*/d' /tmp/upper-constraints.txt
    fi

    # setup the building virtualenv.  We want to freshen this for each
    # branch.
    rm -rf build_env
    ${VIRTUALENV_CMD} build_env

    build_env/bin/pip install --upgrade pip

    # SHORT_BRANCH is just "master","newton","kilo" etc. because this
    # keeps the output log hierarchy much simpler.
    SHORT_BRANCH=${BRANCH##origin/}
    SHORT_BRANCH=${SHORT_BRANCH##stable/}

    # Failed parallel jobs don't fail the whole job, we just report
    # the issues for investigation.
    set +e

    # This runs all the jobs under "parallel".  The stdout, stderr and
    # exit status for each pip invocation will be captured into files
    # kept in ${LOGS}/build/${SHORT_BRANCH}/1/[package].  The --joblog
    # file keeps an overview of all run jobs, which we can probe to
    # find failed jobs.
    cat /tmp/upper-constraints.txt | \
        parallel --files --joblog ${LOGS}/$SHORT_BRANCH-job.log \
                --results ${LOGS}/build/$SHORT_BRANCH \
                build_env/bin/pip --exists-action=i wheel \
                -c /tmp/upper-constraints.txt \
                -w $WHEELHOUSE_DIR {}
    set -e

    # Column $7 is the exit status of the job, $NF is the last
    # argument to pip, which is our package.
    FAILED=$(awk -e '$7!=0 {print $NF}' ${LOGS}/$SHORT_BRANCH-job.log)
    if [ -n "${FAILED}" ]; then
        echo "*** FAILED BUILDS FOR BRANCH ${BRANCH}" >> ${FAIL_LOG}
        echo "${FAILED}" >> ${FAIL_LOG}
        echo -e "***\n\n" >> ${FAIL_LOG}
    fi
done

# Parse stdout from all the build logs to build up a unique list of all
# wheels downloaded from PyPI and delete them from the wheelhouse, since
# this is only meant to provide built wheels which are absent from PyPI.
find ${LOGS}/build/ -name stdout -exec grep 'Downloading' {} \; \
    | sed -n 's,.*Downloading.*[ /]\([^ /]*\.whl\)\([ #].*\|$\),\1,p' \
    | sort -u > ${LOGS}/remove-wheels.txt
pushd ${WHEELHOUSE_DIR}
# NOTE(ianw) -f to ignore missing because the new pip resolver says it
# downloaded some things that it has ulitmately cleaned up itself; see
#  https://github.com/pypa/pip/issues/9271
cat ${LOGS}/remove-wheels.txt | xargs rm -f
popd

if [ -f ${FAIL_LOG} ]; then
    cat ${FAIL_LOG}
fi

# Set the final exit status to 1 if remove-wheels.txt is empty so the
# job will fail.
if [ ! -s ${LOGS}/remove-wheels.txt ]; then
    echo "*** EMPTY WHEEL REMOVAL LIST: THIS SHOULD NOT HAPPEN ***"
    exit 1
fi
