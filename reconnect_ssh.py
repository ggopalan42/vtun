#!/usr/bin/python

import os
import time
import boto
import boto.manage.cmdshell
import sys
import argparse

# Setup Usage and args
parser = argparse.ArgumentParser(description='Connect to running isntances via SSH')

parser.add_argument('-n', '--num', metavar='InstanceCount',
                                            dest='instance_num',
                                            action='store',
                                            default=0,
                                            type=int,
                                            help='AWS Instance number to connect to')
args = parser.parse_args()

key_name='lakitufirstserver-ec2-key'
key_extension='.pem'
key_dir='~/.ssh'

# Create a connection to EC2 service.
# You can pass credentials in to the connect_ec2 method explicitly
# or you can use the default credentials in your ~/.boto config file
# as we are doing here.
ec2 = boto.connect_ec2()

# Get the instances
reservation=ec2.get_all_instances()

# Then get the instance ID of the last running instance
if reservation[args.instance_num].instances[0].state == 'running':  
  instance=reservation[args.instance_num].instances[0]
else:
 sys.exit('Instance number specified is not running!') 

key_path = os.path.join(os.path.expanduser(key_dir), key_name+key_extension)
print key_path
print instance

print "Trying to connect"
cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                        key_path,
                                                        user_name='root')
print "Connected, trying to start shell"
print cmd
cmd.shell()

time.sleep(1)
