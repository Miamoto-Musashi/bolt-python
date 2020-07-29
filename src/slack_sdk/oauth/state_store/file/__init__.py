import os
import time
from logging import Logger
from pathlib import Path
from typing import Union, Optional
from uuid import uuid4

from ..state_store import OAuthStateStore


class FileOAuthStateStore(OAuthStateStore):

    def __init__(
        self,
        *,
        expiration_seconds: int,
        base_dir: str = str(Path.home()) + "/.bolt-app-oauth-state",
        client_id: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        self.expiration_seconds = expiration_seconds

        self.base_dir = base_dir
        self.client_id = client_id
        if self.client_id is not None:
            self.base_dir = f"{self.base_dir}/{self.client_id}"
        self.logger = logger

    def issue(self) -> str:
        state = uuid4()
        self._mkdir(self.base_dir)
        filepath = f"{self.base_dir}/{state}"
        with open(filepath, "w") as f:
            content = str(time.time())
            f.write(content)
        return state

    def consume(self, state: str) -> bool:
        filepath = f"{self.base_dir}/{state}"
        try:
            with open(filepath) as f:
                created = float(f.read())
                expiration = created + self.expiration_seconds
                still_valid: bool = time.time() < expiration

            os.remove(filepath)  # consume the file by deleting it
            return still_valid

        except FileNotFoundError as e:
            message = f"Failed to find any persistent data for state: {state} - {e}"
            self.logger.warning(message)
            return False

    @staticmethod
    def _mkdir(path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
