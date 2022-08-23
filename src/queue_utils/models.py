from pydantic import BaseModel


class StatisticsHandlerRecordSampleMessage(BaseModel):
    test_group_id: str
    id: int
    image_name: str
    target_class_id: int
    predicted_class: int
