#!/usr/bin/env python

import rospy
import tf2_ros
from geometry_msgs.msg import Pose

rospy.init_node('tf_listener_node')
rate = rospy.Rate(100)

tfBuffer = tf2_ros.Buffer()
tf_listener = tf2_ros.TransformListener(tfBuffer)
TF_pub = rospy.Publisher('tf_URBase_RightWrist', Pose, queue_size=1)

while not rospy.is_shutdown():

    try:
        trans = tfBuffer.lookup_transform('URBase', 'right_wrist', rospy.Time())
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rate.sleep()
        continue
    
    msg = Pose()
    msg.position.x = trans.transform.translation.x
    msg.position.y = trans.transform.translation.y
    msg.position.z = trans.transform.translation.z
    msg.orientation.x = trans.transform.rotation.x
    msg.orientation.y = trans.transform.rotation.y
    msg.orientation.z = trans.transform.rotation.z
    msg.orientation.w = trans.transform.rotation.w

    TF_pub.publish(msg)

    print(trans)
    print('---------------------')

    rate.sleep()
