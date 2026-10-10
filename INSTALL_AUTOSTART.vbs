Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
startupFolder = WshShell.SpecialFolders("Startup")

shortcutPath = startupFolder & "\TelegramBotTaskRunner.lnk"
targetPath = currentDir & "\RUN_BOT_BACKGROUND.vbs"

Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = targetPath
shortcut.WorkingDirectory = currentDir
shortcut.Save

WshShell.Run """" & targetPath & """", 0, False
