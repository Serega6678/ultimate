from enum import Enum, auto

from pydantic import BaseModel, Field


class TaskTypeStatisticsHandlerEnum(str, Enum):
    RECORD_SAMPLE = auto()
    BUILD_REPORT = auto()


class TaskTypeStatisticsHandler(BaseModel):
    task_type: TaskTypeStatisticsHandlerEnum = Field(default_factory=TaskTypeStatisticsHandlerEnum)


class RecordSampleMessageTaskTypeStatisticsHandler(TaskTypeStatisticsHandler):
    test_group_id: str
    id: int
    image_name: str
    target_class_id: int
    predicted_class: int
    task_type = TaskTypeStatisticsHandlerEnum.RECORD_SAMPLE


class BuildReportStatisticsHandler(TaskTypeStatisticsHandler):
    test_group_id: str
    save_path: str
    task_type = TaskTypeStatisticsHandlerEnum.BUILD_REPORT
