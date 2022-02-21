#!/bin/bash
#
j=0
for ((i=1; i>j; i++))
do
cpu_idle=$(top -b -n 1 | grep Cpu | awk '{print $8}' |cut -f 1 -d ".")
#-b指的是bath，可以重定向到文件；-n 1指的是一次取1次top数据；-f 1 -d "."指的是一列以.号分割，即输出每一行第一段用户名
cpu_warn='50'
cpu_use=`expr 100 - $cpu_idle`

if [[ ${cpu_use} -lt ${cpu_warn} ]]; then

sleep 1
echo $(date)",当前CPU使用率为 : $cpu_use %"

elif [[ ${cpu_use} -ge ${cpu_warn} ]];then

	echo  "！！！CPU告警-当前使用率为 : $cpu_use %,已达到CPU告警值：$cpu_warn %, 时间：$(date),告警日志在当前目录下 alertlog.txt文本中可查看！！！" | tee -a alertlog.txt
	   ps aux | grep -v USER | sort -rn -k3 | head | tee -a alertlog.txt
	   
fi
done