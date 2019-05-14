FROM alpine:3.9 as builder
LABEL maintainer="cgiraldo@gradiant.org"
LABEL organization="gradiant.org"

ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT

COPY . /src
RUN apk add --no-cache bash  build-base maven grep bc python2-dev py2-nose py2-pip linux-headers && \ 
    ln -s /usr/bin/nosetests-2.7 /usr/bin/nosetests 
RUN pip2 install pylint==1.6.4 mock==2.0.0 && \
    find /src -name requirements.txt -exec pip2 install -r '{}' \;
#pnda.io platform-package repository search for Maven 3.0.5. We patch this to use Maven 3.6
RUN sed -i 's/Apache Maven 3.0.5/Apache Maven 3.6/g' /src/build.sh
RUN cd /src && ./build.sh $GIT_COMMIT
RUN mkdir /dist && tar -xvzf /src/pnda-build/package-repository-$GIT_COMMIT.tar.gz -C /dist

FROM alpine:3.9 as package-repository
LABEL maintainer="cgiraldo@gradiant.org"
LABEL organization="gradiant.org"

ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT

COPY --from=builder /dist/package-repository-$GIT_COMMIT /opt/package-repository
WORKDIR /opt/package-repository
RUN apk add --no-cache bash py2-pip build-base python2-dev linux-headers && pip2 install -r requirements.txt

ENTRYPOINT ["python2", "package_repository_rest_server.py"]
