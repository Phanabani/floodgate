from pathlib import Path
from typing import Any, Callable, Optional, Type, TypeVar, Union

from pydantic import BaseModel, validator as validator_base
from pydantic.fields import FieldInfo

from floodgate.common.typing import get_function_args_annotations

__all__ = [
    "Factory",
    "instance_list_factory",
    "maybe_relative_path",
    "validator",
    "FieldConverterError",
    "FieldConverter",
    "update_forward_refs_recursive",
]

V = TypeVar("V")


class Factory(FieldInfo):
    def __init__(self, default_factory, *args, **kwargs):
        super().__init__(*args, default_factory=default_factory, **kwargs)


def instance_list_factory(class_: Type[V], *args, **kwargs) -> Callable[[], list[V]]:
    def make_list():
        return [class_(*args, **kwargs)]

    return make_list


def maybe_relative_path(path: Union[Path, str], root_path: Path):
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_absolute():
        return root_path / path
    return path


def validator(
    field: str,
    func: Callable[[Any, ...], Any],
    *func_args,
    validator_kw: Optional[dict[str, Any]] = None,
    **func_kwargs,
):
    # noinspection PyUnusedLocal
    def wrapper(value, values, config, field):
        return func(value, *func_args, **func_kwargs)

    validator_kw = validator_kw or {}
    # Always wrap so we can skip function signature errors, such as:
    # Invalid signature for validator: (##Signature##),
    #   should be: (value, values, config, field)
    return validator_base(field, allow_reuse=True, **validator_kw)(wrapper)


class FieldConverterError(Exception):
    pass


T_Converter = Callable[[Type["FieldConverterBase"], Any], Any]


class FieldConverter:
    _pyd_converters: dict[type, T_Converter] = None
    _pyd_converter_prefix = "_pyd_convert"

    @classmethod
    def __get_validators__(cls):
        yield cls._pyd_convert

    @classmethod
    def _pyd_get_converters(cls) -> dict[type, T_Converter]:
        if cls._pyd_converters is not None:
            return cls._pyd_converters

        converters: dict[type, T_Converter] = {}
        for name, member in cls.__dict__.items():
            # Iterate through this class's members and find converter methods
            if not isinstance(member, classmethod):
                continue
            if not name.startswith(cls._pyd_converter_prefix):
                continue

            # Check that the converter method has a single value argument and
            # that the type doesn't already have a converter
            fn = member.__func__  # Unwrap classmethod
            fn_args_types = list(get_function_args_annotations(fn).values())
            if len(fn_args_types) != 1:
                raise FieldConverterError(
                    f"Converter {name} must take one positional argument: value"
                )
            converter_type = fn_args_types[0]
            if converter_type in converters:
                raise FieldConverterError(
                    f"Multiple converters found for type {converter_type}, there "
                    f"should only be one"
                )
            converters[converter_type] = fn

        cls._pyd_converters = converters
        return cls._pyd_converters

    @classmethod
    def _pyd_convert(cls, value):
        converters = cls._pyd_get_converters()
        try:
            fn = converters[type(value)]
        except KeyError:
            raise TypeError(f"No converter for type {type(value)}")
        return fn(cls, value)


def update_forward_refs_recursive(model: Type[BaseModel]):
    for name, value in model.__dict__.items():
        if isinstance(value, type) and issubclass(value, BaseModel):
            update_forward_refs_recursive(value)

    model.update_forward_refs(**model.__dict__)
