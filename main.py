import os
import time
import socket
from typing import Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel
from appdynamics.agent import api as appd


def do_something():
    # Loop to put enough load.
    for x in range(1):
        print('do something')
        time.sleep(1)


app = FastAPI()
env_dict = {
    "APPD_NODE_NAME":
        os.getenv('APPD_NODE_NAME', 'fastAPI-test') +
        "_" + socket.gethostname()
}
appd.init(environ=env_dict, timeout_ms=appd.api.NO_TIMEOUT)


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, request: Request, q: Optional[str] = None):
    with appd.bt('/items_get') as bt_handle:
        do_something()
        optional_properties = {}
        optional_properties['client_host'] = request.client.host
        # Set the identifying properties (required to mark exit call)
        FINANCIALS_ID_PROPS = {'Host': 'financials-lb',
                               'Port': 3456, 'Vendor': 'custom db'}
        with appd.exit_call(bt_handle, appd.EXIT_CUSTOM, 'Faked_Exit', FINANCIALS_ID_PROPS, optional_properties=optional_properties):
            print('in exit call')
            time.sleep(1)
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    mybt = appd.start_bt('/items_put')
    do_something()
    appd.end_bt(mybt)
    return {"item_name": item.name, "item_id": item_id}


@app.on_event("shutdown")
async def shutdown():
    appd.shutdown(timeout_ms=None)
