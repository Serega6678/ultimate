import json
import typing as tp

from database import get_report, insert_sample
from queue_utils import (
    CLASSIFICATION_RECORDER_QUEUE_NAME,
    BuildReportStatisticsHandler,
    RecordSampleMessageTaskTypeStatisticsHandler,
    TaskTypeStatisticsHandlerEnum,
    channel,
)


def consumer_callback(ch: tp.Any, method: tp.Any, properties: tp.Any, body):
    body_data = json.loads(body)
    task_type = TaskTypeStatisticsHandlerEnum(body_data["task_type"])
    if task_type == TaskTypeStatisticsHandlerEnum.RECORD_SAMPLE:
        sample_info = RecordSampleMessageTaskTypeStatisticsHandler(**body_data)
        insert_sample(
            test_group_id=sample_info.test_group_id,
            id=sample_info.id,
            image_name=sample_info.image_name,
            target_class_id=sample_info.target_class_id,
            predicted_class=sample_info.predicted_class,
        )
    elif task_type == TaskTypeStatisticsHandlerEnum.BUILD_REPORT:
        report_info = BuildReportStatisticsHandler(**body_data)
        total_samples, n_classes, accuracy = get_report(test_group_id=report_info.test_group_id)
        with open(report_info.save_path, "w") as f:
            json.dump(
                {"total_samples": total_samples, "n_classes": n_classes, "accuracy": accuracy}, f
            )
    else:
        raise NotImplementedError("Task type not supported")


if __name__ == "__main__":
    channel.basic_consume(
        queue=CLASSIFICATION_RECORDER_QUEUE_NAME,
        on_message_callback=consumer_callback,
        auto_ack=True,
    )
    try:
        channel.start_consuming()
    except Exception:
        import traceback

        traceback.print_exc()
        channel.stop_consuming()
