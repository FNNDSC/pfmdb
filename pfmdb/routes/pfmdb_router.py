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
from pudb.remote import set_trace

from pfmongo.models.responseModel import mongodbResponse
from models.iresponse import SmashesResponse

router = APIRouter()
router.tags = ["pfmdb endpoints"]


@router.post(
    "/pfmongo/smashes/{cmd}",
    response_model=iresponse.SmashesResponse,
    summary="""
    POST a command to pfmongo smashes.
    """,
)
async def pfmongo_cmdExec(
    cmd: str,
    database: str = "",
    collection: str = "",
) -> iresponse.SmashesResponse:
    """
    Description
    -----------

    POST a command to a `pfmongo` smash app and return its response.

    Returns
    -------
    * `iresponse.SmashesResponse`: The response from `smashes`.
    """
    # pudb.set_trace()
    resp: iresponse.SmashesResponse = pfmdb_controller.cmd_exec(
        cmd, database, collection
    )

    return resp


@router.get(
    "/pfmongo",
    response_model=SmashesResponse,
    summary="""
    GET the list of databases in the mongo server
    """,
)
async def pfmongo_databaseShowall() -> SmashesResponse:
    """
    Description
    -----------

    GET a list of databases in the mongo server.

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.database_showall()
    # resp: mongodbResponse = pfmdb_controller.run_in_process(
    #     pfmdb_controller.database_showall
    # )
    return resp


@router.delete(
    "/pfmongo/{database}",
    response_model=SmashesResponse,
    summary="""
    DELETE the {database}
    """,
)
async def pfmongo_databaseDel(database: str) -> SmashesResponse:
    """
    Description
    -----------

    DELETE the {database}

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.database_del(database)
    return resp


@router.get(
    "/pfmongo/{database}",
    response_model=SmashesResponse,
    summary="""
    GET the list of collections for the {database}
    """,
)
async def pfmongo_collectionShowall(database: str) -> SmashesResponse:
    """
    Description
    -----------

    GET a list of collections for the given {database}.

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.collection_showall(database)
    return resp


@router.delete(
    "/pfmongo/{database}/{collection}",
    response_model=SmashesResponse,
    summary="""
    DELETE the {collection} in {database}
    """,
)
async def pfmongo_collectionDel(database: str, collection: str) -> SmashesResponse:
    """
    Description
    -----------

    DELETE the {collection} in {database}

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.collection_del(database, collection)
    return resp


@router.get(
    "/pfmongo/{database}/{collection}",
    response_model=SmashesResponse,
    summary="""
    GET the list of documents for the {database} {collection}
    """,
)
async def pfmongo_documentShowall(database: str, collection: str) -> SmashesResponse:
    """
    Description
    -----------

    GET the list of documents for the {database} {collection}

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.document_showall(database, collection)
    return resp


@router.delete(
    "/pfmongo/{database}/{collection}/{document}",
    response_model=SmashesResponse,
    summary="""
    DELETE a {document} in the {database} {collection}
    """,
)
async def pfmongo_documentDel(
    database: str, collection: str, document: str
) -> SmashesResponse:
    """
    Description
    -----------

    DELEtE a {document} in the {database} {collection}

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.document_del(
        database, collection, document
    )
    return resp


@router.get(
    "/pfmongo/{database}/{collection}/{document}",
    response_model=SmashesResponse,
    summary="""
    GET a {document} in the {database} {collection}
    """,
)
async def pfmongo_documentGet(
    database: str, collection: str, document: str
) -> SmashesResponse:
    """
    Description
    -----------

    GET a {document} in the {database} {collection}

    Returns
    -------
    * `iresponse.SmashesResponse`: the response from `pfmongo`
    """
    resp: SmashesResponse = pfmdb_controller.document_get(
        database, collection, document
    )
    return resp


@router.post(
    "/pfmongo/{database}/{collection}/search",
    response_model=iresponse.SmashesResponse,
    summary="""
    POST a search across a collection, returning a list of documents.
    """,
)
async def pfmongo_collectionSearch(
    database: str, collection: str, term: str = ""
) -> iresponse.SmashesResponse:
    """
    Description
    -----------

    POST a search across a collection, returning a list of documents.

    Returns
    -------
    * `iresponse.SmashesResponse`: The response from `smashes`.
    """
    # pudb.set_trace()
    resp: iresponse.SmashesResponse = pfmdb_controller.collection_search(
        database, collection, term
    )

    return resp


@router.get(
    "/help",
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
    # set_trace(term_size=(254, 60), host="0.0.0.0", port=6900)
    resp = await pfmdb_controller.baseHelp_get()
    return resp
