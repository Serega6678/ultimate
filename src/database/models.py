from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property

from .meta import Base


class ClassificationInfo(Base):
    __tablename__ = "classification_info"

    test_group_id = Column(String, primary_key=True, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    image_name = Column(String, nullable=False)
    target_class_id = Column(Integer, nullable=False)
    predicted_class = Column(Integer, nullable=False)

    __table_args__ = {
        "schema": "statistics_calculation"
    }

    @hybrid_property
    def correctly_classified(self):
        return self.target_class_id == self.predicted_class
