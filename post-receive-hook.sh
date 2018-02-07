#! /bin/bash
#
# @(#)$Id$
#
# Git post commit hook to ignore from a certain user
#

JENKINS_URL=''
GIT_URL=''
BRANCHLIST=''
IGNOREUSER=''
GITREF=''
GITUSER=''

read oldrev newrev refname
echo "Old revision: $oldrev"
echo "New revision: $newrev"
echo "Reference name: $refname"
USER_NAME=$(git log -1 --format=format:%an HEAD)
echo $USER_NAME

contains() {
    local i
    for i in "${@:2}"
    do 
        [[ "$i" == "$1" ]] && return 0;
    done
    return 1
}


for i in "$@"
do
    case $i in
        --branch=*)
        BRANCHLIST="${i#*=}"
        shift
        ;;
        
        --ignoreuser=*)
        IGNOREUSER="${i#*=}"
        shift
        ;;

        --jenkinsurl=*)
        JENKINS_URL="${i#*=}"
        shift
        ;;

        --giturl=*)
        GIT_URL="${i#*=}"
        shift
        ;;

        --gitref=*)
        GITREF="${i#*=}"
        shift
        ;;

    --gituser=*)
        GITUSER="${i#*=}"
        shift
        ;;

        *)
        ;;
    esac
    shift
done

BRANCHES=$(echo $BRANCHLIST | tr ',' "\n")
REFNAME=$(echo $GITREF | tr '/' "\n")


if [ contains "${REFNAME[-1]}" "${BRANCHES[@]}" ]; then
    echo "Working on ${REFNAME[-1]}"
fi

