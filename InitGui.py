import os
import time



__title__  =   "Python tester looper"
__author__ =   "Hugues DU POUGET DE NADAILLAC"
__url__    = [ "https://github.com/huguesdpdn-aerospace/FreeCADPythonTesterLooper" ]



global gLocalTest
global MonitorFileThreadedFunction



gLocalTest = False
try:
    list_of_objects_in_GUI = dir(Gui)
    import  FreeCADGui
    import  FreeCAD
except Exception:
    print("")
    print("======== WARNING ======== WARNING ======== WARNING ======== WARNING ========")
    print("==     We detected that you are running this module in local for tests    ==")
    print("==    There will be no interactions with any FreeCAD libs or Python API   ==")
    print("======== WARNING ======== WARNING ======== WARNING ======== WARNING ========")
    print("")
    gLocalTest = True
    class FreeCADGui:
        class Workbench:
            pass


def MonitorFileThreadedFunction(python_auto_executor_class):
    import time
    if python_auto_executor_class.IsALocalTestRun():
        max_loops = 15
    else:
        max_loops = 20 #99999999
    try:
        while python_auto_executor_class.getRequestStopStatus() is False and max_loops > 0:
            python_auto_executor_class.Log("Thread: Looping and detecting new files/directories that have been changed")
            python_auto_executor_class.setIfMonitoringThreadIsWorking(True)
            for directory_to_monitor in python_auto_executor_class.getMonitoredDirectoriesPathList():
                python_auto_executor_class.Log("Thread: Checking folder {0}".format(directory_to_monitor))
                for file_that_may_not_be_monitored in os.listdir(directory_to_monitor):
                    path_file_that_may_not_be_monitored = os.path.join(directory_to_monitor, file_that_may_not_be_monitored)
                    if os.path.isfile(path_file_that_may_not_be_monitored):
                        if not python_auto_executor_class.FileOrDirectoryShouldBeIgnored(path_file_that_may_not_be_monitored):
                            python_auto_executor_class.AddFileToMonitor(path_file_that_may_not_be_monitored)
            for file_class in python_auto_executor_class.getMonitoredFilesClassList():
                python_auto_executor_class.Log("Thread: Checking file {0}".format(file_class.GetFilePathName()))
                file_class.RefreshFileStatus()
            time.sleep(python_auto_executor_class.getSleepTime())
            max_loops = max_loops - 1
    except Exception:
        pass
    python_auto_executor_class.setIfMonitoringThreadIsWorking(False)



class PythonAutoExecutor(FreeCADGui.Workbench):
    def __init__(self, run_without_freecad):
        import InitPath
        self.__class__.MenuText      = "Python tester looper"
        self.__class__.ToolTip       = "A workbench that detects code changes and launch your Python script for each new change"
        self.__class__.Icon          = os.path.join(InitPath.getWorkbenchPath(), "images", "PythonLogo.svg")
        self.__run_without_freecad   = run_without_freecad
        self.__cache_file            = "LastFilesAndDirectoriesMonitored.txt"
        self.__last_file_added       = ""
        self.__last_dir__added       = ""
        self.__files_monitored       = []
        self.__directories_monitored = []
        self.__monitoring_time       = 5
        self.__request_stop          = False
        self.__thread_is_wroking     = False
        self.__thread_class          = None
        self.__time_increase_active  = False
        self.__time_decrease_active  = True
        self.__LoadLastMonitoredFilesFromCache()

    def Log(self, message):
        if self.IsALocalTestRun():
            print(message)
        else:
            FreeCAD.Console.PrintMessage(message + "\n")

    def IsALocalTestRun(self):
        return self.__run_without_freecad

    def GetLastAddedFile(self):
        return self.__last_file_added

    def GetLastAddedDirectory(self):
        return self.__last_dir__added

    def FileIsAlreadyMonitored(self, file_path_name):
        for file_class in self.__files_monitored:
            if file_class.GetFilePathName() == file_path_name:
                return True
        return False
    
    def AddFileToMonitor(self, file_path_name):
        import MonitoredObject
        if not self.FileIsAlreadyMonitored(file_path_name):
            self.__files_monitored.append(MonitoredObject.MonitoredObject(True, file_path_name))
            self.__last_file_added = file_path_name

    def AddFolderToMonitor(self, folder_path_name):
        import MonitoredObject
        if not self.FileOrDirectoryShouldBeIgnored(folder_path_name):
            if not self.FileIsAlreadyMonitored(folder_path_name):
                self.__directories_monitored.append(MonitoredObject.MonitoredObject(False, folder_path_name))
                self.__last_dir__added = folder_path_name

    def FileOrDirectoryShouldBeIgnored(self, file_name_to_check):
        list_name_should_not_end_by = [ ".a", ".so", ".out", ".log", ".logs", ".tlog", ".lock", ".python-version", ".pycod", ".pyc", ".pyo", ".obj", ".iobj", ".egg", ".eggs", ".egg-info", ".cover", ".tmp", ".tmp_proj", ".cache", ".bak", ".pot", ".cfg", ".cmake", ".make", ".user",  ".userosscache", ".sln.docstates", ".suo", ".rsuser", ".userprefs", ".VisualState.xml", ".nuget.props", "*.nuget.targets" ]
        list_name_should_not_start_by = [ "mono_crash", "coverage", ".sln", ".pdm" ]
        list_name_to_exclude = [ "__pycache__" "CMakeLists.txt" ".vs" "dlldata.c" ".history" ".vshistory" ".localhistory" "ipython_config.py" "pyenv" ]
        for file_should_not_ending_by in list_name_should_not_end_by:
            if file_name_to_check.lower().endswith(file_should_not_ending_by.lower()):
                return True
        for file_should_not_starting_by in list_name_should_not_start_by:
            if file_name_to_check.lower().endswith(file_should_not_starting_by.lower()):
                return True
        for file_should_not_named in list_name_to_exclude:
            if file_should_not_named.lower() == file_name_to_check.lower():
                return True
        return False

    def __LoadLastMonitoredFilesFromCache(self):
        if os.path.isfile(self.__cache_file):
            try:
                with open(self.__cache_file) as file_descriptor:
                    file_lines = [file_line.rstrip().lstrip() for file_line in file_descriptor]
            except Exception:
                pass
            for file_or_directory in file_lines:
                if self.FileOrDirectoryShouldBeIgnored(file_or_directory):
                    self.Log("[PythonAutoExecutor]: Ignoring file or directory named '{0}' since it is not a code file".format(file_or_directory))
                if os.path.isfile(file_or_directory):
                    self.AddFileToMonitor(file_or_directory)
                elif os.path.isdir(file_or_directory):
                    for file in os.listdir(file_or_directory):
                        self.__directories_monitored.append(file_or_directory)
                        self.AddFileToMonitor.append(file_or_directory)
                else:
                    self.Log("[PythonAutoExecutor]: Ignoring file named '{0}' since it is not a regular file or directory".format(file_or_directory))

    def getSleepTime(self):
        return self.__monitoring_time

    def setSleepTime(self, sleep_time):
        self.__monitoring_time = sleep_time
        if sleep_time <= 5:
            self.__time_increase_active = True
            self.__time_decrease_active = False
        if sleep_time >= 14400:
            self.__time_increase_active = False
            self.__time_decrease_active = True

    def getButtonActivationForTimeIncrease(self):
        return self.__time_increase_active

    def getButtonActivationForTimeDecrease(self):
        return self.__time_decrease_active

    def getMonitoredDirectoriesList(self):
        return self.__directories_monitored

    def getMonitoredDirectoriesPathList(self):
        return [ folder_class.GetDirectoryPathName() for folder_class in self.__directories_monitored ]

    def getMonitoredFilesClassList(self):
        return self.__files_monitored

    def getRequestStopStatus(self):
        return self.__request_stop

    def getIfMonitoringThreadIsWroking(self):
        return self.__thread_is_wroking

    def setIfMonitoringThreadIsWorking(self, is_working):
        self.__thread_is_wroking = is_working

    def ForkAndMonitorFiles(self):
        if self.getIfMonitoringThreadIsWroking() is False:
            import threading
            self.__thread_class = threading.Thread(target=MonitorFileThreadedFunction, args=(self, ))
            self.__thread_class.start()
            #self.__thread_class.join()

    def Initialize(self):
        if not self.IsALocalTestRun():
            self.appendToolbar("My Commands", [ "PAEMonitorFile"     ,
                                                "PAEMonitorFolder"   ,
                                                "PAEExecutionExecute",
                                                "PAEExecutionPause"  ,
                                                "PAETimeDecrease"    ,
                                                "PAETimeIncrease"    ] )
        self.ForkAndMonitorFiles()
        return

    def Activated(self):
        return

    def Deactivated(self):
        return

    def ContextMenu(self):
        if not self.IsALocalTestRun():
            self.appendContextMenu("My commands", [ "PAEExecuteRightNow", "PAEPausePlay" , "PAEStop" ])
        return

    #def GetClassName(self):
    #    return "Gui::PythonAutoExecutor"



class PAEMonitorFile:
    def __init__(self, auto_executor_class):
        self.__main_class = auto_executor_class

    def Activated(self):
        if self.__main_class.IsALocalTestRun():
            print("User requested to add a file to monitor")
            return
        py_side_version = None
        try:
            import  PySide2
            from    PySide2         import QtGui
            from    PySide2.QtGui   import QFileDialog
            py_side_version = 2
        except Exception:
            try:
                import  PySide
                from    PySide          import QtGui
                from    PySide.QtGui    import QFileDialog
                py_side_version = 1
            except Exception:
                py_side_version = None
        path_of_last_file_added = ""
        file_dialog_class = None
        if file_dialog_class is None:
            path_of_last_file_added = os.path.dirname(self.__main_class.GetLastAddedFile())
        try:
            if py_side_version is None:
                FreeCAD.Console.PrintError("No PySide detected - You may have to install PySide on your system - Please execute in a terminal\n")
                FreeCAD.Console.PrintError("    pip install PySide\n")
                file_dialog_class = None
            elif py_side_version == 1:
                file_dialog_class = PySide.QtGui.QFileDialog.getOpenFileName(None, u"Add a file to monitor...", path_of_last_file_added, "*.*")
            elif py_side_version == 2:
                file_dialog_class = PySide2.QtGui.QFileDialog.getOpenFileName(None, u"Add a file to monitor...", path_of_last_file_added, "*.*")
            else:
                FreeCAD.Console.PrintError("PySide version {0} not supported".format(py_side_version))
        except Exception:
            file_dialog_class = None
        if file_dialog_class is not None and file_dialog_class and file_dialog_class[0]:
            self.__main_class.AddFileToMonitor(file_dialog_class[0])
        return

    def IsActive(self):
        return True

    def GetResources(self):
        import InitPath
        return {
            "Pixmap"  : os.path.join(InitPath.getWorkbenchPath(), "images", "FileAdd.svg"),
            "Accel"   : "",
            "MenuText": "Add file to monitor",
            "ToolTip" : "Select a file to monitor. When the selected file is updated or changed, we will try to re-execute your main Python script. It can be a Python file or any kind of file. Please be aware that some files should be ignored, such as logs files, project setting files, etc. - If you select them through this command, they will be monitored anyway" }



class PAEMonitorFolder:
    def __init__(self, auto_executor_class):
        self.__main_class = auto_executor_class

    def Activated(self):
        if self.__main_class.IsALocalTestRun():
            print("User requested to add a folder to monitor")
            return
        py_side_version = None
        try:
            import  PySide2
            from    PySide2         import QtGui
            from    PySide2.QtGui   import QFileDialog
            py_side_version = 2
        except Exception:
            try:
                import  PySide
                from    PySide          import QtGui
                from    PySide.QtGui    import QFileDialog
                py_side_version = 1
            except Exception:
                py_side_version = None
        path_of_last_folder_added = ""
        folder_dialog_class = None
        if folder_dialog_class is None:
            path_of_last_folder_added = os.path.dirname(self.__main_class.GetLastAddedDirectory())
        try:
            if py_side_version is None:
                FreeCAD.Console.PrintError("No PySide detected - You may have to install PySide on your system - Please execute in a terminal\n")
                FreeCAD.Console.PrintError("    pip install PySide\n")
                folder_dialog_class = None
            elif py_side_version == 1:
                folder_dialog_class = PySide.QtGui.QFileDialog.getExistingDirectory(None, u"Add a folder to monitor...", path_of_last_folder_added, QtGui.QFileDialog.ShowDirsOnly)
            elif py_side_version == 2:
                folder_dialog_class = PySide2.QtGui.QFileDialog.getExistingDirectory(None, u"Add a folder to monitor...", path_of_last_folder_added, QtGui.QFileDialog.ShowDirsOnly)
            else:
                FreeCAD.Console.PrintError("PySide version {0} not supported".format(py_side_version))
        except Exception:
            folder_dialog_class = None
        if folder_dialog_class is not None and folder_dialog_class:
            self.__main_class.AddFolderToMonitor(folder_dialog_class)
        return

    def IsActive(self):
        return True

    def GetResources(self):
        import InitPath
        return {
            "Pixmap"  : os.path.join(InitPath.getWorkbenchPath(), "images", "FolderAdd.svg"),
            "Accel"   : "",
            "MenuText": "Add folder to monitor",
            "ToolTip" : "Select a folder to monitor. When selected, all existing files (but NOT subfolders) in it will be monitored, including the ones created or deleted. If any of them changed or is updated, we will try to re-execute your main Python script. Please be aware that files, such as logs files, project setting files, etc. will be ignored. If you wish to force the monitoring of such file, please use the 'add file' command (button on the left)" }



class PAETimeIncrease:
    def __init__(self, auto_executor_class):
        self.__main_class = auto_executor_class

    def Activated(self):
        current_sleep_time = self.__main_class.getSleepTime()
        self.__activated = True
        if current_sleep_time < 5:
            current_sleep_time = current_sleep_time + 1
        elif current_sleep_time < 15:
            current_sleep_time = current_sleep_time - (current_sleep_time % 5)
            current_sleep_time = current_sleep_time + 5
        elif current_sleep_time < 60:
            current_sleep_time = current_sleep_time - (current_sleep_time % 15)
            current_sleep_time = current_sleep_time + 15
        elif current_sleep_time < 300:
            current_sleep_time = current_sleep_time - (current_sleep_time % 60)
            current_sleep_time = current_sleep_time + 60
        elif current_sleep_time < 1500:
            current_sleep_time = current_sleep_time - (current_sleep_time % 300)
            current_sleep_time = current_sleep_time + 300
        elif current_sleep_time <= 13500:
            current_sleep_time = current_sleep_time - (current_sleep_time % 900)
            current_sleep_time = current_sleep_time + 900
        self.__main_class.setSleepTime(current_sleep_time)
        return

    def IsActive(self):
        return self.__main_class.getButtonActivationForTimeIncrease()

    def GetResources(self):
        import InitPath
        return {
            "Pixmap"  : os.path.join(InitPath.getWorkbenchPath(), "images", "TimeIncrease.svg"),
            "Accel"   : "",
            "MenuText": "Increase time",
            "ToolTip" : "Increase time before reexcuting your Python script again" }



class PAETimeDecrease:
    def __init__(self, auto_executor_class):
        self.__main_class = auto_executor_class

    def Activated(self):
        current_sleep_time = self.__main_class.getSleepTime()
        if current_sleep_time <= 5:
            current_sleep_time = 5
        elif current_sleep_time <= 15:
            current_sleep_time = current_sleep_time + (current_sleep_time % 5)
            current_sleep_time = current_sleep_time - 5
        elif current_sleep_time <= 60:
            current_sleep_time = current_sleep_time + (current_sleep_time % 15)
            current_sleep_time = current_sleep_time - 15
        elif current_sleep_time <= 300:
            current_sleep_time = current_sleep_time + (current_sleep_time % 60)
            current_sleep_time = current_sleep_time - 60
        elif current_sleep_time <= 1500:
            current_sleep_time = current_sleep_time + (current_sleep_time % 300)
            current_sleep_time = current_sleep_time - 300
        else:
            current_sleep_time = current_sleep_time + (current_sleep_time % 900)
            current_sleep_time = current_sleep_time - 900
        self.__main_class.setSleepTime(current_sleep_time)
        return

    def IsActive(self):
        return self.__main_class.getButtonActivationForTimeDecrease()

    def GetResources(self):
        import InitPath
        return {
            "Pixmap"  : os.path.join(InitPath.getWorkbenchPath(), "images", "TimeDecrease.svg"),
            "Accel"   : "",
            "MenuText": "Decrease time",
            "ToolTip" : "Decrease time before reexcuting your Python script again" }



class PAEExecutionExecute:
    def __init__(self, auto_executor_class):
        self.__main_class = auto_executor_class

    def Activated(self):
        self.__main_class.ForkAndMonitorFiles()
        return

    def IsActive(self):
        return self.__main_class.getIfMonitoringThreadIsWroking()

    def GetResources(self):
        import InitPath
        return {
            "Pixmap"  : os.path.join(InitPath.getWorkbenchPath(), "images", "MonitorExecute.svg"),
            "Accel"   : "",
            "MenuText": "Execute right now your script",
            "ToolTip" : "Will try, across all monitored files, to find where is your main and will launch your script (without customized arguments)" }



class PAEExecutionPause:
    def __init__(self, auto_executor_class):
        self.__main_class = auto_executor_class

    def Activated(self):
        return

    def IsActive(self):
        return not self.__main_class.getIfMonitoringThreadIsWroking()

    def GetResources(self):
        import InitPath
        return {
            "Pixmap"  : os.path.join(InitPath.getWorkbenchPath(), "images", "MonitorPause.svg"),
            "Accel"   : "",
            "MenuText": "Pause",
            "ToolTip" : "Pause the monitored files/directories and wait until you press the 'Play' button - While in Pause, no Python files monitored by this workbench will be executed" }



auto_executor_class = PythonAutoExecutor(gLocalTest)
if gLocalTest is False:
    Gui.addWorkbench(auto_executor_class)
    FreeCADGui.addCommand("PAEMonitorFile"     , PAEMonitorFile     (auto_executor_class))
    FreeCADGui.addCommand("PAEMonitorFolder"   , PAEMonitorFolder   (auto_executor_class))
    FreeCADGui.addCommand("PAEExecutionExecute", PAEExecutionExecute(auto_executor_class))
    FreeCADGui.addCommand("PAEExecutionPause"  , PAEExecutionPause  (auto_executor_class))
    FreeCADGui.addCommand("PAETimeDecrease"    , PAETimeDecrease    (auto_executor_class))
    FreeCADGui.addCommand("PAETimeIncrease"    , PAETimeIncrease    (auto_executor_class))
else:
    auto_executor_class.Initialize()
