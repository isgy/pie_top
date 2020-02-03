# pie_top
a tiny memory monitor and logger

## Usage
 * This script monitors the overall memory usage (RSS) of a linux based system - it reads from /proc/meminfo every 15 seconds,
   and if the % in use is recorded as > 80% it will log this event, with additional information such as per process memory usage and 
   the top n processes with the most increase in memory
   

## Installing
 * choose a directory for pie_top.py and copy the absolute path to the ExecStart variable in the pie_top service file
 * copy the service file to /etc/systemd/system/pie_top.service
 * enable and start the systemd service - $ sudo systemctl enable pie_top.service
                                          $ sudo systemctl start pie_top.service
 * check that it's running correctly - $ sudo systemctl status pie_top.service
