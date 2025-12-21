# Norman Core SDK Overview

Welcome to the **Norman Core SDK** —  
the foundational layer that powers all Norman services.

The Core SDK provides **low-level, high-performance utilities** used internally
by Norman’s platform components, including HTTP communication, file streaming,
socket encryption, and retrieval of stored model data.

---

## Purpose

While the **Norman SDK** (the high-level developer SDK) focuses on user-facing operations  
like uploading models and invoking them, the **Norman Core SDK** provides
the **infrastructure-level primitives** that make those operations possible.

It offers:
- Fast, asynchronous networking primitives (`HttpClient`)
- Streamed file upload/download utilities (`FilePush`, `FilePull`)
- Encrypted socket transfers (`SocketClient`)
- Persistent data access for stored models, invocations, and assets (`Retrieve`)

---

## Architecture

The Core SDK sits between Norman’s **microservices** and **user-facing SDK**,  
ensuring consistent network behavior, secure communication, and reliable data handling.

```text
+----------------------------------------------------------+
|                   User-facing Norman SDK                 |
| (Model Upload, Invoke, Account Management, Authentication)|
+------------------------------▲---------------------------+
                               │
                     uses (async services)
                               │
+----------------------------------------------------------+
|                    Norman Core SDK                       |
|  (HttpClient, FilePush, FilePull, Retrieve, SocketClient) |
+------------------------------▲---------------------------+
                               │
                      communicates via HTTP
                               │
+----------------------------------------------------------+
|               Norman Cloud Microservices                 |
| (Authenticate, Persist, Compute, Retrieve, Storage, etc.)|
+----------------------------------------------------------+
```

---

## Core Components

### **1. HttpClient**
> Centralized asynchronous HTTP client wrapper.

- Handles connection pooling, retries, and request encoding.  
- Supports multiple response types (`Json`, `Text`, `Bytes`, `Iterator`).  
- Automatically injects Bearer tokens using `Sensitive[str]`.

**Example:**
```python
async with HttpClient() as client:
    response = await client.get("persist/models/get", token=my_token)
    print(response)
```

---

### **2. FilePush**
> Upload-side service for large binary files.

- Allocates encrypted sockets for uploading assets or inputs.  
- Streams binary data using ChaCha20 encryption.  
- Finalizes uploads with integrity verification via checksums.

**Key methods:**
- `allocate_socket_for_asset()`  
- `allocate_socket_for_input()`  
- `complete_file_transfer()`

---

### **3. FilePull**
> Download-side service for model assets and I/O files.

- Provides upload link submission and metadata retrieval.  
- Supports both input and output link management.

**Key methods:**
- `get_download_metadata()`  
- `submit_asset_links()`  
- `submit_input_links()`  
- `submit_output_links()`

---

### **4. Retrieve**
> Directly streams stored binary data from Norman storage.

- Returns async iterators for model assets, invocation inputs, and outputs.  
- Efficient for large file retrievals and lazy processing.

**Key methods:**
- `get_model_asset()`  
- `get_invocation_input()`  
- `get_invocation_output()`

---

### **5. SocketClient**
> Handles raw encrypted socket connections.

- Streams binary chunks securely via ChaCha20.  
- Used by `FilePush` to send encrypted uploads.  
- Computes file hashes with integrated streaming checksum (`xxh3_64`).

**Example:**
```python
checksum = await SocketClient.write_and_digest(socket_info, stream)
print("Upload verified:", checksum)
```

---

### **6. StatusFlags**
> Fetch system or entity-level health and operational flags.

- Used to check runtime status of models, invocations, or services.  
- Returns structured flag collections (`dict[str, list[StatusFlag]]`).

---

### **7. Utilities**
> Includes supporting modules for streaming, encryption, and serialization:
- `StreamingUtils` for async file IO.  
- `Sensitive` for secure credential handling.  
- `AppConfig` for runtime configuration (timeouts, chunk sizes, etc.).

---

## Example Workflow

Below is an example showing how several core components work together:

```python
from norman_core.clients.http_client import HttpClient
from norman_core.services.retrieve.retrieve import Retrieve
from norman_core.services.file_push.file_push import FilePush

async def upload_and_verify(token, socket_info, file_path):
    # Upload file via encrypted socket
    async with open(file_path, "rb") as f:
        checksum = await SocketClient.write_and_digest(socket_info, f)
        print("Upload complete, checksum:", checksum)

    # Notify Norman backend to finalize upload
    checksum_request = ChecksumRequest(upload_id=socket_info.upload_id, checksum=checksum)
    await FilePush().complete_file_transfer(token, checksum_request)

    # Retrieve stored version for validation
    stream = await Retrieve().get_model_asset(token, "account_id", "model_id", "asset_id")
    async for chunk in stream:
        ...
```

---

## When to Use the Core SDK

Use the **Norman Core SDK** if you are:
- Building internal Norman services or infrastructure tools.  
- Handling large file uploads/downloads.  
- Managing encrypted or streamed network operations.  
- Integrating with Norman microservices directly (bypassing high-level SDK).

If you are building an application that consumes models,  
use the **Norman SDK** instead — it builds on top of the Core SDK for simplicity.

---

## Related SDKs

| SDK | Purpose | Audience |
|------|----------|-----------|
| **Norman SDK** | High-level SDK for developers and model creators | External users |
| **Norman Core SDK** | Low-level infrastructure SDK | Internal services |
| **Norman Objects** | Shared type definitions and schemas | All components |
| **Norman Utils** | Common async and streaming utilities | Internal use |

---

## Security Notes

> ⚠️ **Important:**  
> All Core SDK network methods use secure tokens wrapped in `Sensitive[str]`.  
> Never log, print, or serialize `Sensitive` values directly.

---

## Summary

The **Norman Core SDK** is the foundation of all Norman platform interactions.  
It handles:
- Secure communication  
- Efficient file streaming  
- Encrypted socket transfers  
- Data persistence and retrieval  

It is the **engine** beneath the Norman SDK — designed for reliability, scalability, and speed.
