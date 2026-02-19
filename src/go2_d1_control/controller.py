import json
import time
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import DataWriter
from cyclonedds.sub import DataReader

from .messages import ArmString, PubServoInfo


class D1ArmController:
    """
    Control the Unitree D1 robotic arm.

    Joint numbers:
        0 = Base rotation
        1 = Shoulder pitch
        2 = Shoulder roll
        3 = Elbow pitch
        4 = Wrist pitch
        5 = Wrist roll
        6 = Gripper

    Angles are in degrees.
    """

    # Message topics
    CMD_TOPIC      = "rt/arm_Command"      # Where to send commands
    ANGLE_TOPIC    = "current_servo_angle" # Where to get joint angles
    FEEDBACK_TOPIC = "arm_Feedback"        # Where to get arm status

    # Joint names for output
    JOINT_NAMES = [
        "Base rotation",
        "Shoulder pitch",
        "Shoulder roll",
        "Elbow pitch",
        "Wrist pitch",
        "Wrist roll",
        "Gripper",
    ]

    def __init__(self, domain_id: int = 0):
        """
        Start up the D1 arm controller.

        Args:
            domain_id: DDS domain ID (defaults to 0).
            Change domain id if there are multiple arms or other DDS devices on the same network to avoid conflicts.
        """
        print("Initializing D1 Arm Controller...")

        self.participant = DomainParticipant(domain_id)

        # Set up command sender
        cmd_topic = Topic(self.participant, self.CMD_TOPIC, ArmString)
        self.cmd_writer = DataWriter(self.participant, cmd_topic)

        # Set up angle reader
        angle_topic = Topic(self.participant, self.ANGLE_TOPIC, PubServoInfo)
        self.angle_reader = DataReader(self.participant, angle_topic)

        # Set up feedback reader
        feedback_topic = Topic(self.participant, self.FEEDBACK_TOPIC, ArmString)
        self.feedback_reader = DataReader(self.participant, feedback_topic)

        # Track command count
        self._seq = 0

        # Wait for connection to be ready
        time.sleep(0.5)

        print("D1 Arm Controller ready.")

    # Helper method

    def _send(self, payload: dict):
        """
        Send a command to the arm as a JSON message.
        """
        payload["seq"] = self._seq
        payload["address"] = 1
        msg = ArmString(data_=json.dumps(payload))
        self.cmd_writer.write(msg)
        self._seq += 1

    # Commands

    def move_joint(self, joint_id: int, angle: float, delay_ms: int = 0):
        """
        Move a single joint to a target angle.
        one joint to a specific angle.

        Args:
            joint_id:  Joint number (0-6).
            angle:     Target angle in degrees.
            delay_ms:  Wait time before moving 
        """
        if joint_id < 0 or joint_id > 6:
            print(f"Error: joint_id must be 0-6, got {joint_id}")
            return

        self._send({
            "funcode": 1,
            "data": {
                "id": joint_id,
                "angle": angle,
                "delay_ms": delay_ms,
            }
        })
        print(f"Joint {joint_id} ({self.JOINT_NAMES[joint_id]}) -> {angle} deg")

    def move_all_joints(self, angles: list):
        """
        Move all 7 joints simultaneously to target angles.

        Args:
            angles: List of 7 angles in degrees [j0, j1, j2, j3, j4, j5, j6].
        """
        if len(angles) != 7:
            print(f"Error: expected 7 angles, got {len(angles)}")
            return

        self._send({
            "funcode": 2,
            "data": {
                "mode": 1,
                "angle0": angles[0],
                "angle1": angles[1],
                "angle2": angles[2],
                "angle3": angles[3],
                "angle4": angles[4],
                "angle5": angles[5],
                "angle6": angles[6],
            }
        })
        print(f"All joints -> {angles}")

    def enable_joints(self, mode: int = 0):
        """
        Enable or disable joints

        Args:
            mode: 0 = enable, 1 = disable
        """
        self._send({
            "funcode": 5,
            "data": {"mode": mode}
        })
        print(f"Joints {'enabled' if mode == 0 else 'disabled'}")

    def go_to_zero(self):
        """
        Move arm to zero position
        """
        self._send({"funcode": 7})
        print("Moving to zero position...")
