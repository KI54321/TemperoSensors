from crontab import CronTab
# This program will run the cron job to upload all fiels to github
githubCrontab = CronTab(tabfile = "/home/pi/Desktop/Raspberry_Pi_Programs/GithubUpload/GITHUBCRONTAB.tab")
githubCrontab.remove_all()

uploadGithubCron = githubCrontab.new(command="python /home/pi/Desktop/Raspberry_Pi_Programs/GithubUpload/GITMAKE.py")
uploadGithubCron.day.every(1)

githubCrontab.write()