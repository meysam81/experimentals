from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from v1 import data_store_pb2 as _data_store_pb2

BAD: Value
DESCRIPTOR: _descriptor.FileDescriptor
FEMALE: Gender
GOOD: Value
MALE: Gender
NONBINARY: Gender

class Person(_message.Message):
    __slots__ = [
        "email",
        "extra",
        "gender",
        "height",
        "id",
        "metadata",
        "name",
        "passport",
        "phone",
        "ssn",
        "tags",
        "values",
    ]

    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    class ValuesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Value
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[_Union[Value, str]] = ...
        ) -> None: ...
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PASSPORT_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    SSN_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    email: str
    extra: _any_pb2.Any
    gender: Gender
    height: float
    id: int
    metadata: _containers.RepeatedCompositeFieldContainer[_data_store_pb2.SaveRequest]
    name: str
    passport: str
    phone: _containers.RepeatedScalarFieldContainer[str]
    ssn: str
    tags: _containers.ScalarMap[str, str]
    values: _containers.ScalarMap[str, Value]
    def __init__(
        self,
        name: _Optional[str] = ...,
        id: _Optional[int] = ...,
        email: _Optional[str] = ...,
        phone: _Optional[_Iterable[str]] = ...,
        height: _Optional[float] = ...,
        gender: _Optional[_Union[Gender, str]] = ...,
        metadata: _Optional[
            _Iterable[_Union[_data_store_pb2.SaveRequest, _Mapping]]
        ] = ...,
        extra: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
        ssn: _Optional[str] = ...,
        passport: _Optional[str] = ...,
        tags: _Optional[_Mapping[str, str]] = ...,
        values: _Optional[_Mapping[str, Value]] = ...,
    ) -> None: ...

class Value(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Gender(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
