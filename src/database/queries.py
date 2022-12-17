import typing as tp

from sqlalchemy import FLOAT, Integer, cast, func, insert, select

from .meta import engine
from .models import ClassificationInfo


def insert_sample(
    test_group_id: str, id: int, image_name: str, target_class_id: int, predicted_class: int
) -> None:
    insertion_query = insert(ClassificationInfo).values(
        test_group_id=test_group_id,
        id=id,
        image_name=image_name,
        target_class_id=target_class_id,
        predicted_class=predicted_class,
    )
    with engine.begin() as conn:
        conn.execute(insertion_query)


def get_report(test_group_id: str) -> tp.Tuple[int, int, float]:
    report_query = select(
        func.count(ClassificationInfo.correctly_classified),
        func.count(func.distinct(ClassificationInfo.target_class_id)),
        cast(func.avg(ClassificationInfo.correctly_classified.cast(Integer)), FLOAT),
    ).where(ClassificationInfo.test_group_id == test_group_id)

    with engine.begin() as conn:
        data: tp.Tuple[int, int, tp.Optional[float]] = conn.execute(report_query).all()[0]
    total_samples, n_classes, accuracy = data
    if accuracy is None:
        accuracy = 0
    return total_samples, n_classes, accuracy
