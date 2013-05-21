import os
import time
import boto.ec2
import boto.manage.cmdshell
import sys

def launch_instance(ami='ami-29644b6c',
                    availability_zone='us-west-1a',
                    instance_type='t1.micro',
                    key_name='lakitufirstserver-ec2-key',
                    key_extension='.pem',
                    key_dir='~/.ssh',
                    group_name='lakitufirstserver-security-group',
                    ssh_port=22,
                    cidr='0.0.0.0/0',
                    tag='Lakitu',
                    user_data=None,
                    cmd_shell=True,
                    login_user='root',
                    ssh_passwd=None):
    cmd = None
    
    # Connect to the AWS region
    ec2 = boto.ec2.connect_to_region(availability_zone[:-1])

    # Now start up the instance.  The run_instances method
    # has many, many parameters but these are all we need
    # for now.
    reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    placement=availability_zone,
                                    user_data=user_data)

    # Find the actual Instance object inside the Reservation object
    # returned by EC2.
    instance = reservation.instances[0]

    print ("Starting %s Instance Type, id= %s" %(instance_type,instance.id))

    # The instance has been launched but it's not yet up and
    # running.  Let's wait for it's state to change to 'running'.
    print ('Waiting for instance'),
    while instance.state != 'running':
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)
        instance.update()
    print 'done'

    # Let's tag the instance with the specified label so we can
    # identify it later.
    instance.add_tag(tag)

    # The reason to sleep is looks like the SSH daemon in the instance
    # starts up rather slowly
    print "Going to sleep for 60 sec"
    time.sleep(60)
    print "Outta sleep"
    
    if cmd_shell:
        key_path = os.path.join(os.path.expanduser(key_dir),
                                key_name+key_extension)
        print 'Starting SSH Command Shell'
        cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                        key_path,
                                                        user_name=login_user)
        # Not too sure why I have to call ...sshclient twice.
        # But first one always fails.
        cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                        key_path,
                                                        user_name=login_user)
    return (instance, cmd)

