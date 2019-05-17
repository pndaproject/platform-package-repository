FROM centos:7.6.1810

RUN yum install -y python-devel epel-release
RUN yum install -y python2-pip gcc

COPY api/src/main/resources /package-repository/

WORKDIR /package-repository/

RUN pip install -r requirements.txt
