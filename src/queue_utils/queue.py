import pika

EXCHANGE_NAME = "classification_statistics"
CLASSIFICATION_RECORDER_QUEUE_NAME = "classification_recorder"
CLASSIFICATION_SUMMARIZER_QUEUE_NAME = "classification_summarizer"

conn_params = pika.ConnectionParameters('rabbitmq', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE_NAME)
classification_recorder_queue = channel.queue_declare(CLASSIFICATION_RECORDER_QUEUE_NAME)
classification_summarizer_queue = channel.queue_declare(CLASSIFICATION_SUMMARIZER_QUEUE_NAME)
