import os
from datetime import date
import subprocess

os.system("cd /home/pi/Desktop/Raspberry_Pi_Programs")
os.system("git add .")
os.system("git commit -m \"New Upload: " + str(date.today()) + "\"")
githubPushCommand = os.popen("git push origin main", "w")
githubPushCommand.write("AKRSApps\n")
githubPushCommand.write("ghp_ERXtqxDOLcqE2ZQuJltipuZF1qxddv2TTdPp\n")

# subprocess.Popen(["AKRSApps", "ghp_ERXtqxDOLcqE2ZQuJltipuZF1qxddv2TTdPp"], universal_newlines=True, stdin=subprocess.PIPE).communicate(input="\n")