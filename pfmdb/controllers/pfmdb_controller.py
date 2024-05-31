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

from pfmongo.commands.dbop import showAll as db
from argparse import Namespace

LOG = logger.debug

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


async def cmd_exec(
    cmd: str, database: str, collection: str
) -> iresponse.PfmongoResponse:
    resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
    resp.stdout = smash.smash_execute(
        f"--database {datebase} --collection {collection} {cmd}"
    )
    return resp


async def database_showall() -> mongodbResponse:
    set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    options: Namespace = pfmongo.options_initialize()
    # options.eventLoopDebug = True
    resp: mongodbResponse = db.showAll_asModel(db.options_add(options))
    return resp


async def baseHelp_get() -> iresponse.PfmongoResponse:
    resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
    # set_trace(term_size=(381, 95), host="0.0.0.0", port=6900)
    smashResp: str | bytes = smash.smash_execute("--help")
    resp.stdout = smashResp
    return resp
