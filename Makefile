SHELL = /bin/bash
.DEFAULT_GOAL = help

help:
	echo "Please provide a command"

run:
	docker-compose up

archive-model:
	cd src/serving && python get_model.py && torch-model-archiver --model-name resnet-18 --version 1.0 --serialized-file resnet-18.pt --handler image_classifier --export-path $(shell pwd)/src/serving/deployment_data/model-store -f

inspect-served-models:
	curl http://localhost:8081/models

inspect-served-classifier:
	curl http://localhost:8081/models/resnet-18
