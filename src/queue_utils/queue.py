import os

import pika

QUEUE_ADDRESS = os.getenv("QUEUE_ADDRESS")

EXCHANGE_NAME = "classification_statistics"
CLASSIFICATION_RECORDER_QUEUE_NAME = "classification_recorder"

conn_params = pika.ConnectionParameters(QUEUE_ADDRESS, 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE_NAME)
classification_recorder_queue = channel.queue_declare(CLASSIFICATION_RECORDER_QUEUE_NAME)
channel.queue_bind(CLASSIFICATION_RECORDER_QUEUE_NAME, EXCHANGE_NAME)
