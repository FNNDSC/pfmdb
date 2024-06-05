from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field
import pudb
from pfmongo import smashes
from config.settings import smashesData
from pudb.remote import set_trace


class Smashes(BaseModel):
    host: str = Field(default=smashesData.smashesHost)
    port: str = Field(default=smashesData.smashesPort)
    msg: str = Field(default="")
    server: str = Field(default="")

    def run(self):
        args: list = f"--host {self.host} --port {self.port}".split()
        if self.server:
            args.append(self.server)
        smashes.main(args)

    def cli_addMsg(self, msg: str = "") -> dict[str, str]:
        message: str = ""
        if isinstance(self.msg, str):
            message = self.msg
        if len(msg):
            message = msg

        d_cli: dict[str, str] = {"host": self.host, "port": self.port, "msg": message}
        return d_cli


class PfmongoResponse(BaseModel):
    stdout: bytes | str = b""
    stderr: bytes | str = b""
    returncode: int = 0


class SmashesResponse(BaseModel):
    response: str
