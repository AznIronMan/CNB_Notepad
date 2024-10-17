Option Explicit
Function CheckPythonVersion()
    Dim objShell, objExec, strVersion, arrVersion
    Set objShell = CreateObject("WScript.Shell")
    On Error Resume Next
    Set objExec = objShell.Exec("python --version")
    If Err.Number <> 0 Then
        WScript.Echo "Error: Python is not installed or not in PATH."
        WScript.Echo "Please install Python 3 (3.11.8 recommended)."
        WScript.Quit 1
    End If
    On Error GoTo 0    
    strVersion = objExec.StdOut.ReadAll
    arrVersion = Split(strVersion)
    arrVersion = Split(arrVersion(1), ".")
    If CInt(arrVersion(0)) < 3 Or (CInt(arrVersion(0)) = 3 And CInt(arrVersion(1)) < 11) Then
        WScript.Echo "Error: Python 3.11 or higher is required."
        WScript.Echo "Please install Python 3 (3.11.8 recommended)."
        WScript.Quit 1
    End If
End Function
CheckPythonVersion
Dim objNetwork, strHostname, strVenvPath, objFSO, objShell, objFile, jsonContent, objJson, launcherVbs, strForce, strRebuild, strRebuildLauncher
Set objNetwork = CreateObject("WScript.Network")
strHostname = Split(objNetwork.ComputerName, ".")(0)
strVenvPath = ".venv-" & strHostname
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")
strForce = (WScript.Arguments.Count > 0 And WScript.Arguments(0) = "-f")
If objFSO.FolderExists(strVenvPath) And Not strForce Then
    strRebuild = InputBox("Virtual environment already exists. Rebuild? (y/n): ", "Rebuild Virtual Environment")
    If LCase(strRebuild) = "y" Then
        objFSO.DeleteFolder strVenvPath
        objShell.Run "cmd /c python -m venv " & strVenvPath & " && " & _
                     strVenvPath & "\Scripts\activate.bat && " & _
                     "pip install -r requirements.txt && " & _
                     "deactivate", 0, True
    Else
        WScript.Echo "Skipping virtual environment setup."
    End If
ElseIf Not objFSO.FolderExists(strVenvPath) Or strForce Then
    If objFSO.FolderExists(strVenvPath) Then objFSO.DeleteFolder strVenvPath
    objShell.Run "cmd /c python -m venv " & strVenvPath & " && " & _
                 strVenvPath & "\Scripts\activate.bat && " & _
                 "pip install -r requirements.txt && " & _
                 "deactivate", 0, True
End If
Set objFile = objFSO.OpenTextFile("cnb_notepad.rsc", 1)
jsonContent = objFile.ReadAll
objFile.Close
Set objJson = CreateObject("ScriptControl")
objJson.Language = "JScript"
launcherVbs = objJson.Eval("(" & jsonContent & ")").launcher_vbs
launcherVbs = Replace(launcherVbs, "{HOSTNAME}", strHostname)
If objFSO.FileExists("CNB_Notepad.vbs") And Not strForce Then
    strRebuildLauncher = InputBox("Launcher script already exists. Rebuild? (y/n): ", "Rebuild Launcher Script")
    If LCase(strRebuildLauncher) = "y" Then
        Set objFile = objFSO.CreateTextFile("CNB_Notepad.vbs", True)
        objFile.Write launcherVbs
        objFile.Close
    Else
        WScript.Echo "Skipping launcher script creation."
    End If
ElseIf Not objFSO.FileExists("CNB_Notepad.vbs") Or strForce Then
    Set objFile = objFSO.CreateTextFile("CNB_Notepad.vbs", True)
    objFile.Write launcherVbs
    objFile.Close
End If
WScript.Echo "Setup complete. To launch the app, run: CNB_Notepad.vbs"

' Create Windows shortcut
Set objFSO = CreateObject("Scripting.FileSystemObject")
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strShortcutScript = objFSO.OpenTextFile(strScriptPath & "\cnb_notepad.rsc", 1).ReadAll
Execute(Replace(strShortcutScript, "{HOSTNAME}", strComputerName))
