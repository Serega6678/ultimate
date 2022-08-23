from pathlib import Path

from pydantic import BaseModel, Field, validator
import typing as tp


class ClassificationSampleInfo(BaseModel):
    test_group_id: str = Field(
        ..., description="Id of the test group of the sample", title="test group id", example="initial_dataset"
    )
    id: int = Field(
        ..., description="Id of the data sample", title="id", example=0
    )
    image_name: str = Field(
        ..., description="Name of the image in the system", title="image name", example="kitten.jpg"
    )
    target_class_id: int = Field(
        ..., description="Target class id", lt=1000, ge=0, title="target class id", example=281
    )
    save: bool = Field(
        True, description="Whether to save the sample info or not", title="save info", example=True
    )

    @validator("image_name")
    def validate_image_name(cls, image_name: str):
        image_path = Path.cwd() / f"../../data/{image_name}"
        if not image_path.exists():
            raise ValueError("Image does not exist")
        return image_name

    def get_image_path(self) -> Path:
        return Path.cwd() / f"../../data/{self.image_name}"


class ClassificationStatus(BaseModel):
    correctly_classified: bool = Field(
        ..., description="True if the sample was correctly classified", title="correctly classified", example=True
    )
