import os
import time

import python_minifier


class MonitoredObject:
    def __init__(self, path_file_name: str):
        self.__path_file_name              = path_file_name
        self.__file_exist                  = None
        self.__directory_exist             = None
        self.__is_file                     = os.path.isfile(self.GetFilePathAndName())
        self.__is_dir                      = os.path.isdir(self.GetFilePathAndName())
        self.__last_modification_timestamp = None
        self.__hash_file                   = None
        self.__hash_code                   = None

    def isFile(self):
        return self.__is_file

    def isDirectory(self):
        return self.__is_dir

    def fileStillExist(self):
        if self.isFile():
            self.__file_exist = os.path.isfile(self.GetFilePathAndName())
            return self.__file_exist
        return False

    def directoryStillExist(self):
        if self.isDirectory():
            self.__directory_exist = os.path.isdir(self.GetFilePathAndName())
            return self.__directory_exist
        return False

    def GetFileName(self):
        if self.isFile():
            return os.path.basename(self.__path_file_name)
        return None

    def GetDirectoryName(self):
        if self.isDirectory():
            return os.path.dirname(self.__path_file_name)

    def GetFilePathAndName(self):
        return self.__path_file_name

    def GetLastModificationTimestamp(self):
        return self.__last_modification_timestamp

    def GetLastHashFile(self):
        return self.__hash_file

    def GetLastHashCode(self):
        return self.__hash_code

    def __FilterNonCodeStuffForPython(self, file_content):
        return file_content

    def __ComputeFileHashes(self):
        old_hash_file = self.GetLastHashFile()
        file_hash     = ""
        file_content  = ""
        try:
            with open(self.__path_file_name, "r") as file_descriptor:
                file_content = file_descriptor.read()
        except Exception:
            file_content = ""
        self.__hash_file = hash(file_content)
        if old_hash_file is None or self.__hash_file != old_hash_file:
            try:
                with open(self.__path_file_name, "r") as file_descriptor:
                    print(python_minifier.minify(file_descriptor.read(), rename_locals=True, combine_imports=True, ))
            except Exception:
                file_content = ""
            else:
                if self.__path_file_name.endswith(".py"):
                    file_content = self.__FilterNonCodeStuffForPython(file_content)
                    self.__hash_code = hash(file_content)

    def __CheckIfStillExists(self):
        if self.isFile():
            return self.fileStillExist()
        elif self.isDirectory():
            return self.directoryStillExist()
        else:
            return False

    def __ComputeLastModificationDate(self):
        try:            
            self.__last_modification_timestamp = os.path.getmtime(self.GetFilePathAndName())
        except Exception:
            pass

    def LogicCodeChanged(self):
        old_timestamp = self.GetLastModificationTimestamp()
        old_hash_code = self.GetLastHashCode()
        if self.__CheckIfStillExists():            
            self.__ComputeLastModificationDate()
            if old_timestamp is None or self.GetLastModificationTimestamp() > old_timestamp: 
                if self.isFile():
                    self.__ComputeFileHashes()
                    if self.GetLastHashCode() != old_hash_code:
                        return True
        return False
