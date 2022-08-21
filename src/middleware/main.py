import json
import os
import typing as tp

import aiohttp
from fastapi import FastAPI, Body

from models import ClassificationSampleInfo, ClassificationStatus


CLASSIFICATION_BACKEND_URL = os.environ.get("CLASSIFICATION_BACKEND_URL")
assert CLASSIFICATION_BACKEND_URL is not None


app = FastAPI()


@app.post("/classify", response_model=ClassificationStatus)
async def classify_sample(sample_info: ClassificationSampleInfo = Body(...)):
    with open(sample_info.image_name, "rb") as file:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(CLASSIFICATION_BACKEND_URL, data={"data": file}) as response:
                classification_results = await response.text()
                classification_results_dict: tp.Dict[int, float] = json.loads(classification_results)
                classified_class_id = max(classification_results_dict.items(), key=lambda x: x[1])[0]
                target_class_id = sample_info.target_class_id
                correctly_classified = target_class_id == classified_class_id
                classification_status = ClassificationStatus(correctly_classified=correctly_classified)
                return classification_status
