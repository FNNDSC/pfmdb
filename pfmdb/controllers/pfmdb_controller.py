# from fastapi import APIRouter, Query, Request, UploadFile
#
# from fastapi.encoders import jsonable_encoder
# from fastapi.concurrency import run_in_threadpool
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Callable, Any
#
import asyncio

from pfmongo.commands.smash import command_get, command_parse, smash_execute_async

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
import re

import tempfile
from pathlib import Path
import uuid
from uuid import UUID
from lib import jobController

from starlette.responses import FileResponse

from pfmongo import pfmongo
from pfmongo import __main__ as main

# from pfmongo.pfmongo.commands import smash
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


async def smashes_do(cmd: str) -> SmashesResponse:
    resp: SmashesResponse
    smash: str | dict[str, str] = smashes.main(Smashes(msg=cmd).cli_addMsg())
    if isinstance(smash, str):
        resp = SmashesResponse(response=smash)
    else:
        resp = SmashesResponse(response=smash["response"])
    return resp


async def smash_do(cmd: str) -> SmashesResponse:
    resp: SmashesResponse = SmashesResponse(response="")
    options: Namespace = options_initialize()
    smash: str | bytes = await smash_execute_async(
        command_parse(await command_get(options, noninteractive=cmd))
    )
    if isinstance(smash, str):
        resp = SmashesResponse(response=smash)
    elif isinstance(smash, bytes):
        resp = SmashesResponse(response=smash.decode())
    return resp


def winToNix_path(cmd: str) -> str:
    """
    Any cmd from the client that contains a windows style '\\'
    has this replaced with '/'
    """
    return re.sub(r"\\(?!\\)", "/", cmd)


async def cmd_exec(
    cmd: str, database: str, collection: str, handler: str
) -> SmashesResponse:
    # set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
    resp: SmashesResponse
    path: str = ""
    cmd = winToNix_path(cmd)

    if len(database.strip()):
        path += database.strip()
    if len(collection.strip()) and len(path):
        path += f"/{collection.strip()}"

    f_handler: Callable[[str], Awaitable[SmashesResponse]]
    if "smashes" in handler.lower():
        f_handler = smashes_do
    else:
        f_handler = smash_do

    if len(path):
        resp = await f_handler(f"cd {path}")

    resp = await f_handler(cmd)
    return resp


async def process(
    func: Callable[[Namespace], Awaitable[mongodbResponse]],
    setup: Callable[[Namespace], Namespace],
    cmd: str,
    rettype: str,
) -> mongodbResponse | SmashesResponse:
    respMongo: mongodbResponse = mongodbResponse()
    respSmash: SmashesResponse
    match rettype.lower():
        case "smash":
            respSmash = await smash_do(cmd)
            return respSmash
        case "smashes":
            respSmash = await smashes_do(cmd)
            return respSmash
        case _:
            respMongo = await func(setup(options))
            return respMongo


async def database_showall(
    rettype: str = "smash",
) -> mongodbResponse | SmashesResponse:
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    # set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
    return await process(
        db.showAll_asModel, db.options_add, "database showall", rettype
    )
    # respMongo: mongodbResponse = mongodbResponse()
    # respSmash: SmashesResponse
    # options: Namespace = options_initialize()
    # options.eventLoopDebug = True
    # match rettype.lower():
    #     case "smash":
    #         respSmash = await smash_do(options, "database showall")
    #         return respSmash
    #     case "smashes":
    #         respSmash = smashes_do("database showall")
    #         return respSmash
    #     case _:
    #         respMongo = await db.showAll_asModel(db.options_add(options))
    #         return respMongo


# def database_showall() -> SmashesResponse:
#     # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
#     resp: SmashesResponse = smashes_do("database showall")
#     return resp


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


async def baseHelp_get() -> iresponse.PfmongoResponse:
    resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
    # set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
    smashResp: str | bytes = smash.smash_execute("--help")
    resp.stdout = smashResp
    return resp
