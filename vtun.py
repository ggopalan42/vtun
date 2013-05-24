#!/usr/bin/python

import os
import time
import boto.ec2
import boto.manage.cmdshell
import sys
import argparse

from ec2_launch_instance import launch_instance

# Define functions
def write_cfg (cmd, tp_src_ip, tp_end_ip, file_name):
  ret=cmd.run("cd /root/vtun/vtun-3.0.3")
  ret=cmd.run("pwd")
  ret=cmd.run("echo options {port 5000\;syslog daemon\;ppp /usr/sbin/pppd\;ifconfig /sbin/ifconfig\;route /sbin/route\;firewall /sbin/ipchains\;ip /sbin/ip\;} > " + file_name)
  ret=cmd.run("echo default {compress no\; speed 0\;} >> " + file_name)
  ret=cmd.run("echo cobra {passwd abcd\;type tun\;proto tcp\;compress no\;encrypt no\;keepalive yes\; >> " + file_name)
  ret=cmd.run("""echo up { ifconfig \\"%% """ + tp_src_ip + " pointopoint " + tp_end_ip + """ mtu 1450\\"\\; }\\;} >> """ + file_name)



# Setup Usage and args
parser = argparse.ArgumentParser(description='Connect to AWS isntance via SSH')

parser.add_argument('-i', '--ins', metavar='InstanceType', 
                                            dest='instance', 
                                            action='store', 
                                            default='m1.small', 
                                            help='AWS Instance type to run on')
# Using lakitufirstserver AMI ID registered as default
parser.add_argument('-a', '--ami', metavar='AMI_ID', 
                                            dest='ami_id', 
                                            action='store', 
                                            default='ami-29644b6c', 
                                            help='AWS AMI ID to use')
parser.add_argument('-n', '--no_terminate', dest='no_term', 
                                            action='store_true', 
                                            help='Do not terminate instance \
                                                          after exiting shell')
args = parser.parse_args()

# Get AMI ID and Instance Type from argument parser
ami=args.ami_id
instance_type=args.instance

# Fire off first instance
instance1,cmd1 = launch_instance(ami=ami, instance_type=instance_type)

print ("Instance1 parameters are:")
print ("DNS Name: %s" %(instance1.dns_name))
print ("IP Address: %s" %(instance1.ip_address))
print ("Private DNS Name: %s" %(instance1.private_dns_name))
print ("Private IP Address: %s" %(instance1.private_ip_address))
private_ip_address1=instance1.private_ip_address.encode("ascii")

# Fire off second instance
instance2,cmd2 = launch_instance(ami=ami, instance_type=instance_type)

print ("Instance2 parameters are:")
print ("DNS Name: %s" %(instance2.dns_name))
print ("IP Address: %s" %(instance2.ip_address))
print ("Private DNS Name: %s" %(instance2.private_dns_name))
print ("Private IP Address: %s" %(instance2.private_ip_address))

private_ip_address2=instance2.private_ip_address.encode("ascii")

# Write Instance1 (Server) cfg file
write_cfg (cmd1, "172.16.0.1", "172.16.0.2", "aws.server")
# Write Instance2 (Client) cfg file
write_cfg (cmd2, "172.16.0.2", "172.16.0.1", "aws.client")

# Start off vtund on server
print "Starting vtund on server"
ret = cmd1.run("vtund -s -f aws.server")
print ret

# Start off vtund on client
print "Starting vtund on client"
ret = cmd2.run("vtund -f aws.client cobra " + private_ip_address1 )
print ret

# Sleep for a bit so tunnels can get setup
time.sleep(2)

# Add lo:1 interface to server
ret=cmd1.run("""ifconfig lo:1 192.168.10.1 netmask 255.255.255.255 up""")
print ret
ret=cmd1.run("""route add -host 192.168.10.2 tun0""")
print ret

# Add lo:1 interface to client
ret=cmd2.run("""ifconfig lo:1 192.168.10.2 netmask 255.255.255.255 up""")
print ret
ret=cmd2.run("""route add -host 192.168.10.1 tun0""")
print ret


