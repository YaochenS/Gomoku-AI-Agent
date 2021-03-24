使用下列command命令生成名为ouragent的可执行程序

pyinstaller.exe toexe.py pisqpipe.py --name pbrain-ouragent.exe --onefile

注：不知出于何原因，本exe file在本地运行时可以100%击败Mushroom，并也可以一定次数击败另外的agent（例如fiverows如果先手的话）
但每次upload 收到的result都是loss，本次midterm的30%分值可从击败mushroom获得，如果使用代理网络运行结果不佳拜托本地尝试一下。已与李泽君助教交流。