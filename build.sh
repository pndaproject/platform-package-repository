#!/bin/bash
#
# Please check pnda-build/ for the build products

VERSION=${1}

function error {
    echo "Not Found"
    echo "Please run the build dependency installer script"
    exit -1
}

echo -n "Apache Maven 3.0.5: "
if [[ $(mvn -version 2>&1) == *"Apache Maven 3.0.5"* ]]; then
    echo "OK"
else
    error
fi

mkdir -p pnda-build
cd api
mvn versions:set -DnewVersion=${VERSION}
mvn clean package
cd ..
mv api/target/package-repository-${VERSION}.tar.gz pnda-build/
sha512sum pnda-build/package-repository-${VERSION}.tar.gz > pnda-build/package-repository-${VERSION}.tar.gz.sha512.txt


