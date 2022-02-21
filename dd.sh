#!/bin/bash
#for i in `seq 1 $(cat /proc/cpuinfo |grep "processor" |wc -l)`
for i in `seq 1 1`
do 
  dd if=/dev/zero of=/dev/null bs=1024k & 
done
