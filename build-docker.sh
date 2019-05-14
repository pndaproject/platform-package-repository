#!/bin/bash
#

repo=$(basename `git rev-parse --show-toplevel`)
commit_tag=$(git log -1 --format=%h)

echo building docker image ${repo}:${commit_tag}

docker build --build-arg GIT_COMMIT=${commit_tag} -t pnda/${repo}:${commit_tag} .




