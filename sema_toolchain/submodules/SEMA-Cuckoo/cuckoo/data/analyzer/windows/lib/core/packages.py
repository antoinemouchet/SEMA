import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Copyright (C) 2012-2013 Claudio Guarnieri.
# Copyright (C) 2014-2018 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

def has_com_exports(exports):
    com_exports = [
        "DllInstall",
        "DllCanUnloadNow",
        "DllGetClassObject",
        "DllRegisterServer",
        "DllUnregisterServer",
    ]

    for name in com_exports:
        if name not in exports:
            return False
    return True

def choose_package(file_type, file_name, exports):
    """Choose analysis package due to file type and file extension.
    @param file_type: file type.
    @param file_name: file name.
    @return: package name or None.
    """
    if not file_type:
        return None

    file_name = file_name.lower()

    if "DLL" in file_type:
        if file_name.endswith(".cpl"):
            return "cpl"
        elif has_com_exports(exports):
            return "com"
        else:
            return "dll"
    elif "PE32" in file_type or "MS-DOS" in file_type:
        return "exe"
    elif "PDF" in file_type or file_name.endswith(".pdf"):
        return "pdf"
    elif file_name.endswith(".pub"):
        return "pub"
    elif "Hangul (Korean) Word Processor File 5.x" in file_type or file_name.endswith(".hwp"):
        return "hwp"
    elif "Rich Text Format" in file_type or \
            "Microsoft Word" in file_type or \
            "Microsoft Office Word" in file_type or \
            file_name.endswith((".doc", ".docx", ".rtf", ".docm")):
        return "doc"
    elif "Microsoft Office Excel" in file_type or \
            "Microsoft Excel" in file_type or \
            file_name.endswith((".xls", ".xlsx", ".xlt", ".xlsm", ".iqy", ".slk")):
        return "xls"
    elif "Microsoft Office PowerPoint" in file_type or \
            "Microsoft PowerPoint" in file_type or \
            file_name.endswith((".ppt", ".pptx", ".pps", ".ppsx", ".pptm", ".potm", ".potx", ".ppsm")):
        return "ppt"
    elif file_name.endswith(".jar"):
        return "jar"
    elif file_name.endswith(".hta"):
        return "hta"
    elif "Zip" in file_type:
        return "zip"
    elif file_name.endswith((".py", ".pyc")) or "Python script" in file_type:
        return "python"
    elif file_name.endswith(".vbs"):
        return "vbs"
    elif file_name.endswith(".js"):
        return "js"
    elif file_name.endswith(".jse"):
        return "jse"
    elif file_name.endswith(".msi"):
        return "msi"
    elif file_name.endswith(".ps1"):
        return "ps1"
    elif file_name.endswith((".wsf", ".wsc")):
        return "wsf"
    elif "HTML" in file_type or file_name.endswith((".htm", ".html", ".hta", ".mht", ".mhtml", ".url")):
        return "ie"
    else:
        return "generic"
