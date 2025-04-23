import copy
import json
import math
import os
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from itertools import combinations
from pprint import pprint
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import joblib
import numpy as np
import orjson
import pandas as pd
import requests
import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from IPython.display import display
from pytz import timezone
from starlette.responses import JSONResponse

from routers import mlb

openapi_tags = [
    {
        'name': 'MSG Baseball',
        'description': 'MLB models, systems, and scrapers.'
    }
]


class ORJSONResponse(JSONResponse):
    """To handle numpy arrays in json responses."""
    media_type = 'application/json'

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_SERIALIZE_NUMPY)

url_prefix = '/mlb'
docs_url = f'{url_prefix}/docs'


async def not_found_error(request: Request, exc: HTTPException):
    json_ = {'detail': f'Not Found. please check {docs_url}'}
    return JSONResponse(content=json_)


exception_handlers = {404: not_found_error}

api = FastAPI(
    title='MSG MLB Baseball API',
    description='Collection of Maverick Sports Group MLB Endpoints.',
    # using build date as version number
    version=datetime.utcnow().strftime('%Y.%m.%d'),
    openapi_url=f'{url_prefix}/openapi.json',
    docs_url=docs_url,
    redoc_url=None,
    exception_handlers=exception_handlers,
    openapi_tags=openapi_tags,
    default_response_class=ORJSONResponse
    # dependencies=[Depends(get_query_token)],
)

api.include_router(mlb.router, prefix=url_prefix)

# Global exception handlers that do a little more introspection.
@api.exception_handler(RequestValidationError)
async def custom_form_validation_error(request, exc):
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error['loc'], pydantic_error['msg']
        filtered_loc = loc[1:] if loc[0] in ('body', 'query', 'path') else loc
        field_string = '.'.join(filtered_loc)  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)
    return JSONResponse(
        content=jsonable_encoder(
            {
                'error':
                    {
                        'message': 'Invalid request',
                        'detail': reformatted_message
                    }
            }
        ),
        status_code=status.HTTP_400_BAD_REQUEST
    )


@api.middleware('http')
async def add_process_exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as ex:
        detail = ''.join(
            traceback.TracebackException.from_exception(ex).format()
        )
        print(detail)
        return JSONResponse(
            content=jsonable_encoder(
                {
                    'error':
                        {
                            'message': f'Backend Error: {str(ex)}',
                            'detail': detail
                        }
                }
            ),
            status_code=500
        )


@api.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print(
        f'starting request id:{id(request)} -> {request.url.path}?{request.url.query}',
        flush=True
    )
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    print(
        f'finished request id:{id(request)} in {process_time} sec -> {request.url.path}?{request.url.query}',
        flush=True
    )
    return response


@api.get('/')
def root():
    return {'message': f'Docs are located at {docs_url}'}


if __name__ == '__main__':
    uvicorn.run('main:api', host='0.0.0.0', port=81, workers=9)
    #uvicorn main:api --reload --port=8000 --host=0.0.0.0
    pass
