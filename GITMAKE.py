import os
from datetime import date
import subprocess

os.system("cd /home/pi/Desktop/Raspberry_Pi_Programs")
os.system("git add .")
os.system("git commit -m \"New Upload: " + str(date.today()) + "\"")
os.system("git push origin main")

subprocess.Popen(["AKRSApps", "ghp_ERXtqxDOLcqE2ZQuJltipuZF1qxddv2TTdPp"], universal_newlines=True, stdin=subprocess.PIPE).communicate(input="\n")