import json
import os
import typing as tp

import aiohttp
from fastapi import FastAPI, Body

from models import ClassificationSampleInfo, ClassificationStatus
from queue_utils import channel, EXCHANGE_NAME, CLASSIFICATION_RECORDER_QUEUE_NAME, StatisticsHandlerRecordSampleMessage


CLASSIFICATION_BACKEND_URL = os.environ.get("CLASSIFICATION_BACKEND_URL")
assert CLASSIFICATION_BACKEND_URL is not None


app = FastAPI()


@app.post("/classify", response_model=ClassificationStatus)
async def classify_sample(sample_info: ClassificationSampleInfo = Body(...)):
    with sample_info.get_image_path().open("rb") as file:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(CLASSIFICATION_BACKEND_URL, data={"data": file}) as response:
                classification_results = await response.text()
                correctly_classified, classified_class_id = get_classification_result(
                    sample_info, classification_results
                )
                if sample_info.save:
                    post_to_queue(sample_info, classified_class_id)
                return ClassificationStatus(correctly_classified=correctly_classified)


def get_classification_result(sample_info: ClassificationSampleInfo, classification_results: str) -> tp.Tuple[bool, int]:
    classification_results_dict: tp.Dict[str, float] = json.loads(classification_results)
    classified_class_id = int(max(classification_results_dict.items(), key=lambda x: x[1])[0])
    target_class_id = sample_info.target_class_id
    correctly_classified = target_class_id == classified_class_id
    return correctly_classified, classified_class_id


def post_to_queue(sample_info: ClassificationSampleInfo, classified_class_id: int) -> None:
    body = StatisticsHandlerRecordSampleMessage(
        test_group_id=sample_info.test_group_id,
        id=sample_info.id,
        image_name=sample_info.image_name,
        target_class_id=sample_info.target_class_id,
        predicted_class=classified_class_id
    )
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=CLASSIFICATION_RECORDER_QUEUE_NAME,
        body=body.json()
    )
