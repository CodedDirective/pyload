#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import sys
from os.path import abspath, dirname, join

from pyload.remote.thriftbackend.thriftgen import ttypes
from pyload.remote.thriftbackend.thriftgen.pyload import Iface

path = dirname(abspath(__file__))
module = join(path, "..", "..")

sys.path.append(join(module, "lib"))
sys.path.append(join(module, "remote"))


def main():

    enums = []
    classes = []

    print("generating lightweight ttypes.py")

    for name in dir(ttypes):
        klass = getattr(ttypes, name)

        if (
            name in ("TBase", "TExceptionBase")
            or name.startswith("_")
            or not (
                issubclass(klass, ttypes.TBase)
                or issubclass(klass, ttypes.TExceptionBase)
            )
        ):
            continue

        if hasattr(klass, "thrift_spec"):
            classes.append(klass)
        else:
            enums.append(klass)

    f = open(join(path, "ttypes.py"), "wb")

    f.write(
        """# -*- coding: utf-8 -*-
from builtins import _
# Autogenerated by pyload
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING

class BaseObject(object):
\t__slots__ = []

"""
    )

    # generate enums
    for enum in enums:
        name = enum.__name__
        f.write("class {}:\n".format(name))

        for attr in dir(enum):
            if attr.startswith("_") or attr in ("read", "write"):
                continue

            f.write("\t{} = {}\n".format(attr, getattr(enum, attr)))

        f.write("\n")

    for klass in classes:
        name = klass.__name__
        base = "Exception" if issubclass(klass, ttypes.TExceptionBase) else "BaseObject"
        f.write("class {}({}):\n".format(name, base))
        f.write("\t__slots__ = {}\n\n".format(klass.__slots__))

        # create init
        args = ["self"] + ["{}=None".format(x for x in klass.__slots__)]

        f.write("\tdef __init__({}):\n".format(", ".join(args)))
        for attr in klass.__slots__:
            f.write("\t\tself.{} = {}\n".format(attr, attr))

        f.write("\n")

    f.write("class Iface:\n")

    for name in dir(Iface):
        if name.startswith("_"):
            continue

        func = inspect.getargspec(getattr(Iface, name))

        f.write("\tdef {}({}):\n\t\tpass\n".format(name, ", ".join(func.args)))

    f.write("\n")

    f.close()


if __name__ == "__main__":
    main()
