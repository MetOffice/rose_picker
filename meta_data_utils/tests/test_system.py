import os
import pathlib
from subprocess import run

TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data/"
META_TYPES_FOLDER = "/um_physics/source/diagnostics_meta/meta_types/"
LFRIC_URL = "fcm:lfric.x_tr@31284"
ENUM_TEST_FILE = "/enum_test_file"
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/tests"


def test_system():

    pwd = pathlib.Path.cwd()

    test_data_dir = pwd/"tests/system_test_data/"

    program = "./diag_meta_gen.py "

    command = "{} -p {} -o {} -s {} -v".format(program,
                                               test_data_dir,
                                               test_data_dir,
                                               test_data_dir/"meta_types/")
    run(command, shell=True)

    test_json_file = open(
        test_data_dir / "test_json_data.json", "r")
    json_test_data = test_json_file.readlines()

    rose_meta_test_file = open(
        test_data_dir / "test_rose_meta.conf", "r")
    rose_test_data = rose_meta_test_file.readlines()

    rose_meta_file = open(
        test_data_dir / "example_rose_suite/meta/rose-meta.conf", "r")
    rose_result_data = rose_meta_file.readlines()

    json_file = open(
        test_data_dir / "example_rose_suite/LFRic_meta_data.json", "r")
    json_result_data = json_file.readlines()

    assert json_result_data == json_test_data
    assert rose_result_data == rose_test_data
