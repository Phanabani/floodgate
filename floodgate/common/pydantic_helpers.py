from pathlib import Path
from typing import Callable, Type, TypeVar, Union

from pydantic import validator
from pydantic.fields import FieldInfo

__all__ = ["Factory", "instance_list_factory", "validator_maybe_relative_path"]


class Factory(FieldInfo):
    def __init__(self, default_factory, *args, **kwargs):
        super().__init__(*args, default_factory=default_factory, **kwargs)


V = TypeVar("V")


def instance_list_factory(class_: Type[V], *args, **kwargs) -> Callable[[], list[V]]:
    def make_list():
        return [class_(*args, **kwargs)]

    return make_list


def maybe_relative_path(root_path: Path, path: Union[Path, str]):
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_absolute():
        return root_path / path
    return path


def validator_maybe_relative_path(root_path: Path):
    def f(path: Union[Path, str]):
        return maybe_relative_path(root_path, path)

    return validator("output_file", allow_reuse=True)(f)
