from pydantic import BaseModel


class ValueTypeNoID(BaseModel):
    type_name: str
    type_unit: str


class ValueType(ValueTypeNoID):
    id: int


class ValueNoID(BaseModel):
    value_type_id: int
    device_id: int
    time: int
    value: float


class Value(ValueNoID):
    id: int


class DeviceNoID(BaseModel):
    name: str
    location: str


class Device(DeviceNoID):
    id: int


class ApiDescription(BaseModel):
    description: str = "This is the Api"
    value_type_link: str = "/type"
    value_link: str = "/value"
