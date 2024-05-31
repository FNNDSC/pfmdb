from os import walk
from shutil import ignore_patterns
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks, Request
from fastapi import File, UploadFile, Path, Form
from typing import List, Dict, Any, Union, Annotated

from starlette.responses import FileResponse

from models import credentialModel
from models import iresponse
from controllers import pfmdb_controller
from routes import credentialRouter
from pathlib import Path as PathLib
from config import settings
from pftag import pftag
import pudb

from pfmongo.models.responseModel import mongodbResponse

router = APIRouter()
router.tags = ["pfmdb endpoints"]


@router.post(
    "/pfmongo/smash/{cmd}",
    response_model=iresponse.PfmongoResponse,
    summary="""
    POST a command to pfmongo smash.
    """,
)
async def pfmongo_cmdExec(
    cmd: str,
    database: str,
    collection: str,
) -> iresponse.PfmongoResponse:
    """
    Description
    -----------

    POST a command to a `pfmongo` smash app and return its response.

    Returns
    -------
    * `iresponse.PfmongoResponse`: The response from `pfmongo`.
    """
    # pudb.set_trace()
    resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
    resp = await pfmdb_controller.cmd_exec(cmd, database, collection)

    return resp


@router.get(
    "/pfmongo/database/showall",
    response_model=mongodbResponse,
    summary="""
    GET the list of databases in the mongo server
    """,
)
async def pfmongo_databaseShowall() -> mongodbResponse:
    """
    Description
    -----------

    GET a list of databases in the mongo server.

    Returns
    -------
    * `iresponse.PfmongoResponse`: the response from `pfmongo`
    """
    # resp: mongodbResponse = await pfmdb_controller.database_showall()
    resp: mongodbResponse = pfmdb_controller.run_in_thread(
        pfmdb_controller.database_showall
    )
    return resp


@router.get(
    "/pfmongo/help",
    response_model=iresponse.PfmongoResponse,
    summary="""
    GET the overall help response from pfmongo
    """,
)
async def pfmongo_help() -> iresponse.PfmongoResponse:
    """
    Description
    -----------

    GET the general `--help` response from `pfmongo`.

    Returns
    -------
    * `iresponse.PfmongoResponse`: the response from `pfmongo`
    """
    resp: iresponse.PfmongoResponse = iresponse.PfmongoResponse()
    resp = await pfmdb_controller.baseHelp_get()
    return resp