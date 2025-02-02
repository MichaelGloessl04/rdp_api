import logging
from typing import List

from fastapi import FastAPI, HTTPException

from rdp.crud import Crud, create_engine
from rdp.sensor import Reader

from . import api_types as ApiTypes
import time

logger = logging.getLogger("rdp.api")
app = FastAPI()


@app.get("/")
def read_root() -> ApiTypes.ApiDescription:
    """This url returns a simple description of the api

    Returns:
        ApiTypes.ApiDescription: the Api description in json format
    """
    return ApiTypes.ApiDescription()


@app.get("/type/")
def read_types() -> List[ApiTypes.ValueType]:
    """Implements the get of all value types

    Returns:
        List[ApiTypes.ValueType]: list of available valuetypes.
    """
    global crud
    return crud.get_value_types()


@app.get("/type/{type_id}/")
def read_type(type_id: int) -> ApiTypes.ValueType:
    """returns an explicit value type identified by id

    Args:
        id (int): primary key of the desired value type

    Raises:
        HTTPException: Thrown if a value type with the given id cannot be
        accessed

    Returns:
        ApiTypes.ValueType: the desired value type
    """
    global crud
    try:
        return crud.get_value_type(type_id)
    except crud.NoResultFound:
        raise HTTPException(status_code=404, detail="Item not found")


@app.put("/type/{type_id}/")
def put_type(
    type_id,
    value_type: ApiTypes.ValueTypeNoID
) -> ApiTypes.ValueType:
    """PUT request to a special valuetype. This api call is used to change a
    value type object.

    Args:
        id (int): primary key of the requested value type
        value_type (ApiTypes.ValueTypeNoID): json object representing the new
        state of the value type.

    Raises:
        HTTPException: Thrown if a value type with the given id cannot be
        accessed

    Returns:
        ApiTypes.ValueType: the requested value type after persisted in the
        database.
    """
    global crud
    try:
        crud.add_or_update_value_type(
            type_id,
            value_type_name=value_type.type_name,
            value_type_unit=value_type.type_unit
        )
        return read_type(type_id)
    except crud.NoResultFound:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/value/")
def get_values(
    type_id: int = None,
    start: int = None,
    end: int = None,
    order: str = None,
    asc: bool = None
) -> List[ApiTypes.Value]:
    """Get values from the database. The default is to return all available
    values. This result can be filtered.

    Args:
        type_id (int, optional): If set, only values of this type are returned.
        Defaults to None.
        start (int, optional): If set, only values at least as new are
        returned. Defaults to None.
        end (int, optional): If set, only values not newer than this are
        returned. Defaults to None.

    Raises:
        HTTPException: _description_

    Returns:
        List[ApiTypes.Value]: _description_
    """
    global crud
    try:
        values = crud.get_values(type_id, start, end, order, asc)
        return values
    except crud.NoResultFound:
        raise HTTPException(status_code=404, detail="Item not found")


@app.post("/value/")
def post_value(
    value_value: float = None,
    value_type: float = None,
    value_device: float = None
) -> None:
    global crud
    try:
        crud.add_value(int(time.time()), value_type, value_value, value_device)
    except crud.NoResultFound:
        raise HTTPException(status_code=404, deltail="Item not found")


@app.get("/device/")
def read_devices() -> List[ApiTypes.Device]:
    """Implements the get of all devices

    Returns:
        List[ApiTypes.Device]: list of available devices.
    """
    global crud
    return crud.get_devices()


@app.get("/average/{type_id}/")
def get_average(type_id, start: int = None, end: int = None) -> float:
    if (bool(start) ^ bool(end)):
        raise ValueError("Both start and end need to be a valid timestamp.")

    values = crud.get_values(type_id, start, end)

    if (len(values) > 0):
        return sum([value.value for value in values]) / len(values)
    else:
        return 0


@app.on_event("startup")
async def startup_event() -> None:
    """start the character device reader
    """
    logger.info("STARTUP: Sensor reader!")
    global reader, crud
    engine = create_engine("sqlite:///rdb.test.db")
    crud = Crud(engine)
    reader = Reader(crud)
    reader.start()
    logger.debug("STARTUP: Sensor reader completed!")


@app.on_event("shutdown")
async def shutdown_event():
    """stop the character device reader
    """
    global reader
    logger.debug("SHUTDOWN: Sensor reader!")
    reader.stop()
    logger.info("SHUTDOWN: Sensor reader completed!")
