FROM centos:7.6.1810

RUN yum install -y epel-release
RUN yum install -y python36-devel python36-pip gcc

COPY api/src/main/resources /package-repository/

WORKDIR /package-repository/

RUN pip3 install -r requirements.txt

# PNDA platform users must transition from Linux SO users to cloud-native. For now we add a pnda user to container images.
RUN useradd pnda
