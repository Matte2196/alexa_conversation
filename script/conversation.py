#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

rospy.init_node('Alexa Conversation')
rate = rospy.Rate(1000) # 1000hz

nome_pub = rospy.Publisher('nome_publisher', String, queue_size=1)

while not rospy.is_shutdown():

    hello_str = "hello world %s" % rospy.get_time()
    rospy.loginfo(hello_str)
    nome_pub.publish(hello_str)
    rate.sleep()
