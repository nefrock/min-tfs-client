import os
from contextlib import contextmanager
from pathlib import Path
from shutil import copy2
from subprocess import check_output

from setuptools import find_namespace_packages, setup

ROOT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
PROTOBUF_TF_INCLUDE_PATH = ROOT_DIR / "protobuf_srcs/"
PROTOBUF_TFS_INCLUDE_PATH = ROOT_DIR / "protobuf_srcs/tensorflow_serving/"
OUTPUT_PATH = ROOT_DIR / "tensor_serving_client/"
PROTO_TF_PATHS = [p for p in PROTOBUF_TF_INCLUDE_PATH.rglob("*.proto")]
PROTO_TFS_PATHS = [p for p in PROTOBUF_TFS_INCLUDE_PATH.rglob("*.proto")]
PROTO_TF_PATHS = [str(p) for p in PROTO_TF_PATHS if p not in PROTO_TFS_PATHS]
PROTO_TFS_PATHS = [str(p.relative_to(PROTOBUF_TFS_INCLUDE_PATH)) for p in PROTO_TFS_PATHS]


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


if __name__ == "__main__":
    pb_compile_command = [
        "python", "-m", "grpc_tools.protoc",
        f"-I={str(PROTOBUF_TF_INCLUDE_PATH)}",
        f"--python_out={str(OUTPUT_PATH)}",
        *PROTO_TF_PATHS
    ]
    with cd(str(PROTOBUF_TF_INCLUDE_PATH)):
        check_output(pb_compile_command)
    pb_compile_command = [
        "python", "-m", "grpc_tools.protoc",
        f"-I={str(PROTOBUF_TF_INCLUDE_PATH)}",
        f"-I={str(PROTOBUF_TFS_INCLUDE_PATH)}",
        f"--python_out={str(OUTPUT_PATH)}",
        *PROTO_TFS_PATHS
    ]
    with cd(str(PROTOBUF_TFS_INCLUDE_PATH)):
        check_output(pb_compile_command)
    predict_service_stub = (
        PROTOBUF_TFS_INCLUDE_PATH / "tensorflow_serving/apis/prediction_service_pb2_grpc.py"
    )
    model_service_stub = (
        PROTOBUF_TFS_INCLUDE_PATH / "tensorflow_serving/apis/model_service_pb2_grpc.py"
    )
    destination = ROOT_DIR / "tensor_serving_client/tensorflow_serving/apis/"
    copy2(predict_service_stub, destination)
    copy2(model_service_stub, destination)

    with open("README.md", "r") as fh:
        long_description = fh.read()
    setup(
        name="min_tfs_client",
        version="1.0.2",
        description="A minified Tensor Serving Client for Python",
        long_description=long_description,
        long_description_content_type="text/markdown",
        package_dir={"": "tensor_serving_client"},
        packages=find_namespace_packages(where="tensor_serving_client"),
        install_requires=[
            "grpcio>=1.24.3, <2.0",
            "protobuf>=3.9.2, <3.20",
            "numpy>=1.20"
        ],
        tests_require=["pytest"],
        extras_require={"dev": ["black==19.10b0", "flake8", "mypy", "pytest"]},
    )
