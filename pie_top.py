#!/usr/bin/env python3

import threading, time, os, subprocess
from sys import platform, exit
from optparse import OptionParser

mempath = '/proc/meminfo'
meminfo = {}
logdata = {}
counter = 0
logfile = '/var/log/pie_top.log'

def main():
    if not platform.startswith("linux"):
        print("this script only runs on linux platforms")
        exit()

    global logfile
    global counter


    if counter == 0:
        print("\n")
        print("                 A TINY MEMORY MONITOR AND LOGGER\n")
        print("------------------------------------------------------------------\n")
        print("                 systemd service: pie_top.service\n")
        print("\n")
        print(" This script checks the overall memory usage of the system (RSS)\n")
        print(" every 15 seconds and logs additional information about the current\n")
        print(" system to /var/log/pie_top.log when the RSS exceeds\n")
        print(" 80%\n")
        print("\n")
        print("____________________________________________________________________\n")
        print("\n ")
        print(" For the script to run at startup, the systemd service pie_top.service\n")
        print(" must be enabled - $ sudo systemctl enable pie_top.service\n")
        print("\n")

    with open(mempath) as f:
        for line in f.readlines():
            k = line.split()[0].rstrip(':')
            v = int(line.split()[1])
            meminfo.update({k:v})

    memcurr = meminfo['MemTotal'] - meminfo['MemFree']
    memperc = (memcurr / meminfo['MemTotal']) * 100
    t = time.time()
    timestr = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(t))

    top_proc = subprocess.run("ps axo rss,pid,comm | sort -n | tail -n 25 | sort -rn", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    logdata.update({counter:[timestr,memperc,top_proc.stdout]})
    changed = []
    if memperc >= 80:
       with open(logfile,"a+") as f:
           #num_lines = sum(1 for line in f)
           #if num_lines == 0:
           f.write("DATE AND TIME (where RSS > 80%)  |  OVERALL MEMORY USAGE %\n")
           f.write(timestr + "          |  " + str(memperc) + '      \n')
           f.write('\n')
           f.write("PROCESSES WITH THE HIGHEST MEMORY USAGE ------------------\n")
           f.write("OVER THE LAST 3 MINUTES (12 SAMPLES) ---------------------\n")
           f.write('\n')
           f.write("MEM USED (M)     PID             NAME\n")
           f.write('\n')
           formatted = top_proc.stdout.split('\n')[:-1]
           firsttwo = [x.split()[0:2] for x in formatted]
           names = [' '.join(x.split()[2:]) for x in formatted]
           for i in range(len(names)):
               fstr = str(int(firsttwo[i][0])/1000)
               sstr = firsttwo[i][1]
               padd = ' '*(17 - len(fstr))
               pad2 = ' '*(16 - len(sstr))
               print(fstr + padd + sstr + pad2 + names[i] + '\n')
               f.write(fstr + padd + sstr + pad2 + names[i] + '\n')
           f.write('\n')
           f.write("------------------------------------------------------------\n")
           dlen = len(logdata)
           if dlen > 12:
              currdata = logdata[counter][2].split('\n')    #get the list of processes
              prevdata = logdata[counter-12][2].split('\n')    #get the data from 3 minutes ago (4 samples per minute * 3)
              currdata = currdata[:-1]    #needed because of the extra \n
              prevdata = prevdata[:-1]
              print(currdata)
              print(prevdata)
              for i in currdata:
                  for j in prevdata:
                      ei = i.split()
                      ej = j.split()
                      if ei[1] == ej[1]:     #if the PIDs match
                          memdiff = int(ei[0]) - int(ej[0])
                          tup = (memdiff, ei[1], ei[2])
                          changed.append(tup)
              changed.sort()
              chg = [x for x in changed if x[0] > 0]
              chg.reverse()
              print(chg)
              f.write("PROCESSES WITH HIGHEST INCREASE IN MEMORY USAGE ------------\n")
              f.write('\n')
              f.write("MEM INCREASE      PID            NAME\n")
              f.write('\n')
              for i in chg:
                  mstr = str(i[0])
                  padd = ' '*(17 - len(mstr))
                  pad2 = ' '*(16 - len(i[1]))
                  f.write(str(i[0]) + padd + i[1] + pad2 + i[2] + '\n')
                  f.write('\n')
              f.write("-----------------------------------------------------------\n")
              f.write("___________________________________________________________\n")
              f.write("___________________________________________________________\n")
              f.write('\n')


    #starttime = t
    counter += 1
    t = threading.Timer(15,main).start()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
        help="write log to FILE", metavar="FILE")
    (options, args) = parser.parse_args()
    if options.filename:
        logfile = options.filename
    main()
