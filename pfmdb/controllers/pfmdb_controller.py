# from fastapi import APIRouter, Query, Request, UploadFile
#
# from fastapi.encoders import jsonable_encoder
# from fastapi.concurrency import run_in_threadpool
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Callable, Any
#
import asyncio

# from pydantic_core.core_schema import ExpectedSerializationTypes
from models import iresponse, credentialModel
import os
from datetime import datetime

import json
import pudb
from pudb.remote import set_trace
from config import settings
from controllers import credentialController

from argparse import Namespace, ArgumentParser
import sys
from loguru import logger
import shutil

import tempfile
from pathlib import Path
import uuid
from uuid import UUID
from lib import jobController

from starlette.responses import FileResponse

from pfmongo import pfmongo
from pfmongo import __main__ as main
from pfmongo.commands import smash
from pfmongo.models.responseModel import mongodbResponse
from pfmongo.pfmongo import options_initialize
from pfmongo.commands.dbop import showAll as db
from pfmongo import smashes
from argparse import Namespace

from models.iresponse import SmashesResponse
from models.iresponse import Smashes

from typing import Awaitable, Callable
import queue
import threading
import multiprocessing


logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.opt(colors=True)
logger.add(sys.stderr, format=logger_format)
LOG = logger.info


def noop():
    """
    A dummy function that does nothing.
    """
    return {"status": True}


def run_in_thread(func: Callable[..., Awaitable[mongodbResponse]]) -> mongodbResponse:
    set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    q: queue.Queue = queue.Queue()

    async def run_async() -> None:
        result: mongodbResponse = await func()
        q.put(result)

    def thread_func() -> None:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_async())

    thread: threading.Thread = threading.Thread(target=thread_func)
    thread.start()
    result: mongodbResponse = q.get()
    return result


def process_func(
    func: Callable[..., Awaitable[mongodbResponse]], q: multiprocessing.Queue
) -> None:
    # Get the current event loop policy and create a new instance
    event_loop_policy = asyncio.get_event_loop_policy()
    new_event_loop_policy = type(event_loop_policy)()
    asyncio.set_event_loop_policy(new_event_loop_policy)

    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result: mongodbResponse = loop.run_until_complete(func())
    q.put(result)


def run_in_process(func: Callable[..., Awaitable[mongodbResponse]]) -> mongodbResponse:
    q: multiprocessing.Queue = multiprocessing.Queue()
    process: multiprocessing.Process = multiprocessing.Process(
        target=process_func, args=(func, q)
    )
    process.start()
    process.join()  # Wait for the child process to finish
    result: mongodbResponse = q.get()
    return result


def smashes_do(cmd: str) -> SmashesResponse:
    resp: SmashesResponse
    smash: str | dict[str, str] = smashes.main(Smashes(msg=cmd).cli_addMsg())
    if isinstance(smash, str):
        resp = SmashesResponse(response=smash)
    else:
        resp = SmashesResponse(response=smash["response"])
    return resp


def cmd_exec(cmd: str, database: str, collection: str) -> SmashesResponse:
    resp: SmashesResponse
    if len(database.strip()):
        resp = smashes_do(f"cd /{database}/{collection.strip()}")
    else:
        resp = smashes_do("cd /")

    resp = smashes_do(cmd)
    return resp


def database_showall() -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse = smashes_do("database showall")
    return resp


def database_del(database: str) -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"rm /{database}")
    return resp


def collection_showall(database: str) -> SmashesResponse:
    # set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"cd /{database}")
    resp = smashes_do("collection showall")
    return resp


def document_showall(database: str, collection: str) -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"cd /{database}/{collection}")
    resp = smashes_do("document showall")
    return resp


def collection_del(database: str, collection: str) -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"rm /{database}/{collection}")
    return resp


def collection_search(database: str, collection: str, term: str) -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"cd /{database}/{collection}")
    resp = smashes_do(f"sg {term}")
    return resp


def document_get(database: str, collection: str, document: str) -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"cat /{database}/{collection}/{document}")
    return resp


def document_del(database: str, collection: str, document: str) -> SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    resp = smashes_do(f"rm /{database}/{collection}/{document}")
    return resp


# async def database_showall() -> iresponse.PfmongoResponse:
#     # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
#     set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
#     resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
#     mdbOptions: Namespace = options_initialize()
#     response = smash.smash_execute(
#         smash.command_parse(
#             smash.command_get(mdbOptions, noninteractive="database showall")
#         )
#     )
#     smashResp: str | bytes = response
#     resp.stdout = smashResp
#     return resp


async def baseHelp_get() -> iresponse.PfmongoResponse:
    resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
    # set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
    smashResp: str | bytes = smash.smash_execute("--help")
    resp.stdout = smashResp
    return resp
