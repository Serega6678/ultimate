import json
import os
import random
import string
import typing as tp

import aiohttp
from fastapi import FastAPI, Body, Query

from models import ClassificationSampleInfo, ClassificationStatus
from queue_utils import channel, EXCHANGE_NAME, CLASSIFICATION_RECORDER_QUEUE_NAME, RecordSampleMessageTaskTypeStatisticsHandler, BuildReportStatisticsHandler


CLASSIFICATION_BACKEND_URL = os.environ.get("CLASSIFICATION_BACKEND_URL")
assert CLASSIFICATION_BACKEND_URL is not None


app = FastAPI()


@app.post("/classify", response_model=ClassificationStatus)
async def classify_sample(sample_info: ClassificationSampleInfo = Body(...)) -> ClassificationStatus:
    with sample_info.get_image_path().open("rb") as file:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(CLASSIFICATION_BACKEND_URL, data={"data": file}) as response:
                classification_results = await response.text()
                correctly_classified, classified_class_id = get_classification_result(
                    sample_info, classification_results
                )
                if sample_info.save:
                    post_to_queue_classify(sample_info, classified_class_id)
                return ClassificationStatus(correctly_classified=correctly_classified)


@app.get("/report", response_model=str)
def get_report(
        test_group_id: str = Query(..., title="test group id", example="initial_dataset", description="test group id")
) -> str:
    path_to_save = "/reports/" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)) + ".json"
    post_to_queue_report(test_group_id, path_to_save)
    return path_to_save


def get_classification_result(sample_info: ClassificationSampleInfo, classification_results: str) -> tp.Tuple[bool, int]:
    classification_results_dict: tp.Dict[str, float] = json.loads(classification_results)
    classified_class_id = int(max(classification_results_dict.items(), key=lambda x: x[1])[0])
    target_class_id = sample_info.target_class_id
    correctly_classified = target_class_id == classified_class_id
    return correctly_classified, classified_class_id


def post_to_queue_classify(sample_info: ClassificationSampleInfo, classified_class_id: int) -> None:
    body = RecordSampleMessageTaskTypeStatisticsHandler(
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


def post_to_queue_report(test_group_id: str, path_to_save: str):
    body = BuildReportStatisticsHandler(
        test_group_id=test_group_id,
        save_path=path_to_save
    )
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=CLASSIFICATION_RECORDER_QUEUE_NAME,
        body=body.json()
    )
