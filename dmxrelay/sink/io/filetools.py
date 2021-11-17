import json
import os
import errno


def writeFile(path, content, mode="w"):
    """
    Writes content to a file at the given path

    :param path: Path of the file to write
    :param content: Content to write to the file
    :param mode: File Open mode, 'w' for write, 'a' for append
    :return: None
    """
    dirname = os.path.dirname(path)
    if len(dirname.strip()) > 0 and not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    f = open(path, mode, encoding='utf8')
    try:
        f.write(content)
    finally:
        f.close()


def readFileLinesStripped(path):
    """
    Read the file Line by Line and strip each line of leading and trailing whitespaces

    :param path: Path to read from
    :return: a list of stripped Lines
    """
    f = open(path, "r", encoding='utf8')
    lines = []
    try:
        for line in f:
            lines.append(line.strip())
    finally:
        f.close()

    return lines


def readFile(path):
    """
    Read the complete file

    :param path: Path to read from
    :return: the data of the file
    """
    f = open(path, "r", encoding='utf8')
    result = ""
    try:
        result = f.read()
    finally:
        f.close()

    return result


def writeFileBinary(path, content, mode="wb"):
    """
    Writes content to a file at the given path

    :param path: Path of the file to write
    :param content: Content to write to the file
    :param mode: File Open mode, 'w' for write, 'a' for append
    :return: None
    """
    dirname = os.path.dirname(path)
    if len(dirname.strip()) > 0 and not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    f = open(path, mode)
    try:
        f.write(content)
    finally:
        f.close()


def readFileBinary(path):
    """
    Read the complete file

    :param path: Path to read from
    :return: the data of the file
    """
    f = open(path, "rb")
    result = ""
    try:
        result = f.read()
    finally:
        f.close()

    return result


def writeJSON(path: str, values: dict):
    content = json.dumps(values, indent=2, sort_keys=True)
    writeFile(path, content)


def readJSON(path: str) -> dict:
    content = readFile(path)
    return json.loads(content)