"""Utility functions for Kafka and Protobuf."""

import os
import subprocess
import sys
import time


def compile_protos():
    """Compile proto files using the Makefile."""
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add build directory to path
    build_dir = os.path.join(project_root, "build")
    if build_dir not in sys.path:
        sys.path.append(build_dir)
    
    # Ensure build directory exists
    os.makedirs(build_dir, exist_ok=True)
    
    # Create __init__.py in build directory if it doesn't exist
    init_file = os.path.join(build_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Generated package for proto files\n")
    
    # Run make compile-protos from project root
    try:
        subprocess.run(
            ["make", "compile-protos"], 
            check=True,
            cwd=project_root
        )
    except subprocess.CalledProcessError:
        # Fallback: compile directly if make fails
        protos_dir = os.path.join(project_root, "protos")
        if os.path.exists(protos_dir):
            for proto_file in os.listdir(protos_dir):
                if proto_file.endswith(".proto"):
                    proto_path = os.path.join(protos_dir, proto_file)
                    subprocess.run(
                        ["protoc", f"--python_out={build_dir}", "-I", protos_dir, proto_path],
                        check=False
                    )
    
    return build_dir


def wait_for_kafka(bootstrap_servers, timeout=60):
    """Wait for Kafka to be available."""
    from confluent_kafka.admin import AdminClient
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            admin = AdminClient({"bootstrap.servers": bootstrap_servers})
            metadata = admin.list_topics(timeout=10)
            if metadata:
                return True
        except Exception:
            pass
        time.sleep(1)
    
    return False


def wait_for_schema_registry(url, timeout=60):
    """Wait for Schema Registry to be available."""
    import requests
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/subjects")
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    
    return False