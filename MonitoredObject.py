import os
import time



class MonitoredObject:
    def __init__(self, file_or_dir, path_file_name):
        self.__file_or_path                = file_or_dir
        self.__path_file_name              = path_file_name
        self.__last_test_modification_time = time.time()
        self.__last_test_hash_value        = hash("")
        self.__last_test_file_exist        = True
        self.__last_run__modification_time = time.time()
        self.__last_run__hash_value        = hash("")
        self.__last_run__file_exist        = True

    def isFile(self):
        return self.__file_or_path

    def isDirectory(self):
        return not self.__file_or_path

    def GetFileName(self):
        return os.path.basename(self.__path_file_name)

    def GetFilePathName(self):
        return self.__path_file_name

    def GetDirectoryName(self):
        return os.path.basename(self.__path_file_name)

    def GetDirectoryPathName(self):
        return self.__path_file_name

    def GetLastTestedModificationTimestamp(self):
        return self.__last_test_modification_time

    def GetLastTestedHashValue(self):
        return self.__last_test_hash_value

    def GetLastTestedFileExistence(self):
        return self.__last_test_file_exist

    def GetFromLastRunModificationTimestamp(self):
        return self.__last_run__modification_time

    def GetFromLastRunHashValue(self):
        return self.__last_run__hash_value

    def GetFromLastRunFileExistence(self):
        return self.__last_run__file_exist

    def __FilterNonCodeStuffForPython(self, file_content):
        return file_content

    def __ComputeFileCheckSum(self):
        file_hash    = ""
        file_content = ""
        try:
            with open(self.__path_file_name, "r") as file_descriptor:
                file_content = file_descriptor.read()
        except Exception:
            file_content = ""
        if self.__path_file_name.endswith(".py"):
            file_content = self.__FilterNonCodeStuffForPython(file_content)
        file_hash = hash(file_content)
        self.__last_test_hash_value = file_hash

    def __CheckIfFileExists(self):
        self.__last_test_file_exist = os.path.isfile(self.__path_file_name)

    def __ComputeLastModificationDate(self):
        try:
            self.__last_test_modification_time = os.path.getmtime(self.__path_file_name)
        except Exception:
            pass

    def RefreshFileStatus(self):
        self.__CheckIfFileExists()
        self.__ComputeLastModificationDate()
        self.__ComputeFileCheckSum()
