' PassingGrade — Silent Windows launcher
' Double-click this file to launch PassingGrade with no CMD/console window.
'
' Launch order:
'   1. dist\PassingGrade.exe  (built standalone — preferred)
'   2. pythonw main.py        (run from source — requires Python 3.11+)

Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")
sDir = oFSO.GetParentFolderName(WScript.ScriptFullName) & "\"

If oFSO.FileExists(sDir & "dist\PassingGrade.exe") Then
    oShell.Run Chr(34) & sDir & "dist\PassingGrade.exe" & Chr(34), 0, False
Else
    On Error Resume Next
    oShell.Run "pythonw " & Chr(34) & sDir & "main.py" & Chr(34), 0, False
    If Err.Number <> 0 Then
        MsgBox "PassingGrade could not start." & vbNewLine & vbNewLine & _
               "To run from source: install Python 3.11+ from https://www.python.org" & vbNewLine & _
               "then run:  pip install -r requirements.txt", _
               vbExclamation, "PassingGrade"
    End If
End If
