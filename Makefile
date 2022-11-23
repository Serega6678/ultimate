SHELL = /bin/bash
.DEFAULT_GOAL = help

help:
	echo "Please provide a command"

run:
	cd src/middleware && QUEUE_ADDRESS="localhost" CLASSIFICATION_BACKEND_URL="https://localhost:8080/predictions/resnet-18" gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8079 --workers 4

archive-model:
	source venv_torchserve/bin/activate
	cd src/serving && python get_model.py && torch-model-archiver --model-name resnet-18 --version 1.0 --serialized-file resnet-18.pt --handler image_classifier --export-path $(shell pwd)/src/serving/deployment_data/model-store -f

run-torchserve:
	docker run --rm -it -p 8080:8080 -p 8081:8081 -v $(shell pwd)/src/serving/deployment_data:/home/model-server/deployment_data pytorch/torchserve:0.6.0-cpu torchserve --start --ts-config /home/model-server/deployment_data/config.properties --models resnet-18=resnet-18.mar

inspect-served-models:
	curl --insecure https://localhost:8081/models

inspect-served-classifier:
	curl --insecure https://localhost:8081/models/resnet-18

run_docker_compose:
	docker-compose --env-file .env up
