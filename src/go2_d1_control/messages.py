from dataclasses import dataclass
from cyclonedds.idl import IdlStruct
from cyclonedds.idl.types import float32


@dataclass
class ArmString(IdlStruct, typename="unitree_arm::msg::dds_::ArmString_"):
    """
    Send commands to the arm using a JSON string.

    The arm reads the 'funcode' number in the JSON to determine which command to execute, 
    and the 'data' field contains the command parameters.
    

     Example JSON payloads:
      funcode 1 → move single joint
      funcode 2 → move all joints
      funcode 5 → enable/disable joints
      funcode 7 → go to zero position
    """
    data_: str = ""


@dataclass
class PubServoInfo(IdlStruct, typename="unitree_arm::msg::dds_::PubServoInfo_"):
    """
    Get the current angle of each joint from the arm.

    servo0 = base rotation
    servo1 = shoulder pitch
    servo2 = shoulder roll
    servo3 = elbow pitch
    servo4 = wrist pitch
    servo5 = wrist roll
    servo6 = gripper
    """
    servo0_data_: float32 = 0.0
    servo1_data_: float32 = 0.0
    servo2_data_: float32 = 0.0
    servo3_data_: float32 = 0.0
    servo4_data_: float32 = 0.0
    servo5_data_: float32 = 0.0
    servo6_data_: float32 = 0.0

    def as_list(self):
        """Get all joint angles as a list"""
        return [
            self.servo0_data_,
            self.servo1_data_,
            self.servo2_data_,
            self.servo3_data_,
            self.servo4_data_,
            self.servo5_data_,
            self.servo6_data_,
        ]