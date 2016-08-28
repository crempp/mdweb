#!/usr/bin/env bash

set -e
set -u
set -o pipefail

# more bash-friendly output for jq
JQ="jq --raw-output --exit-status"

configure_aws_cli(){
	aws --version
	aws configure set default.region $AWS_DEFAULT_REGION
	aws configure set default.output json
}

push_ecr_image(){
	eval $(aws ecr get-login --region $AWS_DEFAULT_REGION)

    # NOTE: could also use $CIRCLE_BUILD_NUM
	docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/mdweb-build-registry:$CIRCLE_BRANCH-$CIRCLE_SHA1

    docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/mdweb-build-registry:$CIRCLE_BRANCH-$CIRCLE_SHA1 \
               $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/mdweb-build-registry:latest

    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/mdweb-build-registry:latest
}

configure_aws_cli
push_ecr_image
