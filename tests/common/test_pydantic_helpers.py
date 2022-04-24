from typing import Optional, Type

from pydantic import BaseModel, ValidationError
import pytest

from floodgate.common.pydantic_helpers import *


@pytest.fixture()
def angie():
    return {"person_name": "Angie"}


@pytest.fixture()
def fiona():
    return {"pet_name": "Fiona"}


@pytest.fixture()
def bulldog():
    return {"pet_breed": "bulldog"}


@pytest.fixture()
def angie_bulldog():
    return {
        "person_name": "Angie",
        "pet_breed": "bulldog",
    }


@pytest.fixture()
def fiona_bulldog():
    return {
        "pet_name": "Fiona",
        "pet_breed": "bulldog",
    }


@pytest.fixture()
def angie_fiona_bulldog():
    return {
        "person_name": "Angie",
        "pet_name": "Fiona",
        "pet_breed": "bulldog",
    }


class BaseTestOneOf:
    def assert_pass(self, model: Type[BaseModel], obj: dict, **kwargs):
        parsed = model.parse_obj(obj)
        for attr, value in kwargs.items():
            assert getattr(parsed, attr) == value

    def assert_fail(self, model: Type[BaseModel], obj: dict):
        with pytest.raises(ValidationError):
            model.parse_obj(obj)


class TestOneOfRequired(BaseTestOneOf):
    @pytest.fixture()
    def model(self):
        class Model(BaseModel):
            person_name: Optional[str] = None
            # OR
            pet_name: Optional[str] = None
            pet_breed: Optional[str] = None

            _check = only_one_of(
                "person_name",
                ["pet_name", "pet_breed"],
                need_all=[True, True],
            )

        return Model

    def test_angie(self, model, angie):
        self.assert_pass(
            model, angie, person_name="Angie", pet_name=None, pet_breed=None
        )

    def test_fiona_bulldog(self, model, fiona_bulldog):
        self.assert_pass(
            model,
            fiona_bulldog,
            person_name=None,
            pet_name="Fiona",
            pet_breed="bulldog",
        )

    def test_fiona_fails(self, model, fiona):
        self.assert_fail(model, fiona)

    def test_bulldog_fails(self, model, bulldog):
        self.assert_fail(model, bulldog)

    def test_angie_bulldog_fails(self, model, angie_bulldog):
        self.assert_fail(model, angie_bulldog)

    def test_angie_fiona_bulldog_fails(self, model, angie_fiona_bulldog):
        self.assert_fail(model, angie_fiona_bulldog)


class TestOneOfNotRequired(BaseTestOneOf):
    @pytest.fixture()
    def model(self):
        class Model(BaseModel):
            person_name: Optional[str] = None
            # OR
            pet_name: Optional[str] = None
            pet_breed: Optional[str] = None

            _check = only_one_of(
                "person_name",
                ["pet_name", "pet_breed"],
                need_all=[False, False],
            )

        return Model

    def test_fiona_passes(self, model, fiona):
        self.assert_pass(
            model,
            fiona,
            person_name=None,
            pet_name="Fiona",
            pet_breed=None,
        )

    def test_bulldog_passes(self, model, bulldog):
        self.assert_pass(
            model,
            bulldog,
            person_name=None,
            pet_name=None,
            pet_breed="bulldog",
        )

    def test_angie_bulldog_fails(self, model, angie_bulldog):
        self.assert_fail(model, angie_bulldog)
