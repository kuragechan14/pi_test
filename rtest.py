from random import randint
import time

task_list=["aa","bb","cc","dd"]
while True:
	num=randint(0,3)
	print(num,task_list[num])
	time.sleep(0.5)	
