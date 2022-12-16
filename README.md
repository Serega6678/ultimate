# Ultimate Project

## Info

This is a pet project where I've used:
* Auto-migration (Alembic)
* Docker-compose
* DVC
* FastAPI & pydantic
* Make
* Nginx
* Prometheus & Grafana
* Python
* RabbitMQ
* SQL & SQLAlchemy
* Streamlit
* Torchserve

and other technologies.

## Setup

Download model and convert it into the necessary format
```
pip install -r torchserve_requirements.txt
make archive-model
```

## Launch

Launch the entire system
```
docker-compose up
```

