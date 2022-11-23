#!/usr/bin/env bash

/app/wait-for-it.sh postgres:5432
alembic -c database/alembic.ini upgrade head
/app/wait-for-it.sh rabbit:5672
python main.py