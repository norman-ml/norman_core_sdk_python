import os
import subprocess
import sys

PROTO_SOURCE_ENV = "NORMAN_OBJECTS_PATH"
PROTO_SUBDIR = "src/norman_objects/proto/file_push_v2"
OUTPUT_DIR = "norman_core/services/file_push/proto"

PROTO_FILES = [
    "messages/assets/asset_identifiers.proto",
    "messages/assets/asset_upload_request.proto",
    "messages/inputs/input_identifiers.proto",
    "messages/inputs/input_upload_request.proto",
    "messages/shared/file_chunk.proto",
    "messages/shared/upload_complete.proto",
    "messages/shared/upload_response.proto",
    "services/file_push.proto"
]


def main():
    norman_objects_path: str = os.environ.get(PROTO_SOURCE_ENV)
    if not norman_objects_path:
        print(f"Error: {PROTO_SOURCE_ENV} environment variable not set.")
        print(f"Set it to the path of your norman_objects_rust checkout.")
        print(f"Example: export {PROTO_SOURCE_ENV}=/path/to/norman_objects_rust")
        sys.exit(1)

    proto_root: str = os.path.join(norman_objects_path, PROTO_SUBDIR)
    if not os.path.isdir(proto_root):
        print(f"Error: proto directory not found at {proto_root}")
        sys.exit(1)

    script_dir: str = os.path.dirname(os.path.abspath(__file__))
    output_dir: str = os.path.join(script_dir, OUTPUT_DIR)

    for proto_file in PROTO_FILES:
        proto_path: str = os.path.join(proto_root, proto_file)
        if not os.path.isfile(proto_path):
            print(f"Error: proto file not found: {proto_path}")
            sys.exit(1)

    cmd: list[str] = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"--proto_path={proto_root}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}"
    ] + PROTO_FILES

    print(f"Generating proto stubs from {proto_root}")
    print(f"Output directory: {output_dir}")

    result: subprocess.CompletedProcess = subprocess.run(cmd, cwd=proto_root)
    if result.returncode != 0:
        print("Error: proto generation failed")
        sys.exit(1)

    print("Proto stubs generated successfully")


if __name__ == "__main__":
    main()