#!/bin/bash

set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."

SCRIPT_PATH=$(dirname $(realpath -s $0))


usage()
{
    cat << USAGE >&2
Usage:
    $SCRIPT_PATH/insatll.sh [for-docker|with-docker|--help]
      --help : display this
      with-docker: will build a docker and tag it as doccortex as well as installing this package
      for-docker: internal. used when installing the package in a docker
USAGE
    exit 1
}
function get-bootstrap {
    BSTRP_TMP=/tmp/getting_bootstrap
    mkdir $BSTRP_TMP
    pushd $BSTRP_TMP
    curl -SL  https://github.com/twbs/bootstrap/releases/download/v4.5.0/bootstrap-4.5.0-dist.zip > bootstrap-4.5.0-dist.zip
    mkdir -p $SCRIPT_PATH/../cortex/web/bootstrap
    yes | unzip bootstrap-4.5.0-dist.zip -d $SCRIPT_PATH/../cortex/web/bootstrap
    popd
    rm -r $BSTRP_TMP
}


function main {
    if ["$1" == "--help"] ; then
        usage
        exit
    fi
    if [ "$1" != "for-docker" ] ; then
	    python -m virtualenv .env --prompt "asd-thoughts"
	    find .env -name site-packages -exec bash -c 'echo "../../../../" > {}/self.pth' \;
    fi
    pip install -U pip
    pip install -r requirements.txt
    get-bootstrap
    if ["$1 == with-docker"] ; then
      docker build . -t doccortex:0.2
    fi
}


main "$@"
