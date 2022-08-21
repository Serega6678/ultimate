from pathlib import Path
import typing as tp

from pydantic import BaseModel, Field, validator


class ClassificationSampleInfo(BaseModel):
    id: int = Field(
        ..., description="Id of the data sample", title="id", example="0"
    )
    image_name: str = Field(
        ..., description="Name of the image in the system", title="image name", example="kitten.jpg"
    )
    save_on_error: bool = Field(
        True, description="Whether to save the sample on error or not", title="save on error", example=True
    )
    target_class_id: tp.Optional[int] = Field(
        None, description="Target class id", lt=1000, ge=0, title="target class id", example=281
    )

    @validator("image_name")
    def validate_image_name(cls, image_name: str):
        absolute_path = Path(image_name)
        image_path = Path.cwd() / f"../../data/{image_name}"
        if not absolute_path.exists() and not image_path.exists():
            raise ValueError("Image does not exist")
        if image_path.exists():
            return image_path.absolute()
        return absolute_path.absolute()


class ClassificationStatus(BaseModel):
    correctly_classified: bool = Field(
        ..., description="True if the sample was correctly classified", title="correctly classified", example=True
    )
