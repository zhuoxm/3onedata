#!/bin/bash
DIR="/data/tmp"
if [ -f "$DIR/count.txt" ];then
  var1=$(cat $"$DIR/count.txt")
  var2=`expr $var1 + 1`
else
  mkdir /data/tmp
  var2=1
fi

echo $var2 > $DIR/count.txt

time=$(date "+%Y-%m-%d %H:%M:%S")
ipa=$(ip a)

value=()
failcounts=0
failinfo=''

model=$(ls /boot | grep tcu | awk -F '-' '{print $3}' | awk -F '.' '{print $1}')

if [ $model == 'tcu2000' ];then
  ports=(ge1 ge2 ge3 ge4 ge5 ge6 ge7 ge8 gs9 gs10 gs11 gs12)
elif [ $model == 'tcu200' ];then
  ports=(fe1 fe2 fe3 fe4 fe5 fe6 fe7 fe8 gs9 gs10)
elif [ $model == 'tcu300' ];then
  ports=(fe1 fe2 fe3 fe4 fe5 fe6 fe7 fe8 gs9 gs10 cans0p1)
elif [ $model == 'tcu1000' ];then
  ports=(ge1 ge2 ge3 ge4 cans0p1) 
elif [ $model == 'tcu100' ];then
  ports=(ge1 ge2)
fi
  
len=${#ports[*]}
for ((i=0;i<$len;i++));do
  value[i]=$(ip a | grep ${ports[$i]} | grep -v 'grep' | wc -l)
  echo ${ports[$i]}
  if [ ${value[$i]} == 0 ];then
    let failcounts++
        if [ $failcounts == 1 ];then
          failinfo=$failinfo' '$var2' '$time' port check fail: '${ports[$i]}
        else
          failinfo=$failinfo' '${ports[$i]}
    fi
  fi
done

echo $len ' ' ${ports[*]} 

if [ $failcounts -gt 0 ];then
  echo $failinfo >> $DIR/log.txt
else
  echo $var2 $time 'allport check pass!' >> $DIR/log.txt
fi

pingfails=0
for ((i=1;i<=3;i++));do
  if ping -c 1 $1 > /dev/null;then
    echo "ping $1 is success" >> $DIR/log.txt
        break
  else
    let pingfails++
  fi
done
if [ $pingfails -eq 3 ];then
  echo "ping $1 is failure" >> $DIR/log.txt
fi
