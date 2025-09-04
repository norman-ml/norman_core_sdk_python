from io import BufferedReader
from typing import TypedDict, Any, Union, Iterator, AsyncIterator

from aiofiles.threadpool.binary import AsyncBufferedReader

FileStream = Union[BufferedReader, AsyncBufferedReader, bytes]

class RequestKwargs(TypedDict, total=False):
    json: Any
    data: Union[dict[str, Any], bytes, str]
    files: dict[str, tuple[FileStream, str]]
    content: Union[bytes, str]
    stream: Union[Iterator[bytes], AsyncIterator[bytes]]
    params: dict[str, Any]
