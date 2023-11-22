from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import math
import tinyik

class Trajectory(ABC):
    finished: bool
    counter: int

    num_setpoints: int
    leg_center_distance: float

    angles = []
    velocities = []

    def __init__(self, num_setpoints, leg_center_distance) -> None:
        self.counter = 0
        self.num_setpoints = num_setpoints
        self.leg_center_distance = leg_center_distance
        self.finished = False
        self.angles, self.velocities = self.generate_trajectory()

    def get_next_state(self):
        if self.counter == len(self.angles):
            self.finished = True
        
        angle = self.angles[self.counter]
        velocity = self.velocities[self.counter]
        
        if self.finished == False:
            counter += 1
        else:
            counter = 0

        return angle, velocity
    
    @abstractmethod
    def generate_trajectory(self) -> tuple[list[tuple], list[tuple]]:
        pass

    def plot(self):
        zeroes = []
        joint1_x = []
        joint1_y = []
        joint2_x = []
        joint2_y = []
        
        for angle in self.angles:
            joint1_x.append(self.leg_center_distance * math.cos(angle[0]))
            joint1_y.append(self.leg_center_distance * math.sin(angle[0]))
            joint2_x.append(self.leg_center_distance * math.cos(angle[1] + angle[0]))
            joint2_y.append(self.leg_center_distance * math.sin(angle[1] + angle[0]))
            zeroes.append(0)

        plt.quiver(zeroes, zeroes, joint1_x, joint1_y, color='b', angles='xy', scale_units='xy', scale=1)
        plt.quiver(joint1_x, joint1_y, joint2_x, joint2_y, color='b', angles='xy', scale_units='xy', scale=1)

        # TODO: prob should change limits to generalize to any trajectory 

        plt.xlim(-0.15, 0.2) 
        plt.ylim(-0.3, 0.05) 
        plt.show()

class HalfCircleTrajectory(Trajectory):

    num_setpoints_swing: int
    num_setpoints_drag: int
    
    dist_to_ground : float
    swing_radius: float

    leg_ik: tinyik.Actuator

    def __init__(self, num_setpoints, leg_center_distance, dist_to_ground, swing_radius, uniform_velocity) -> None:

        self.num_setpoints_swing = int((math.pi / (2 + math.pi)) * num_setpoints) 
        self.num_setpoints_drag = int((2 / (2 + math.pi)) * num_setpoints)
        
        self.leg_ik = tinyik.Actuator(['z', [leg_center_distance, 0., 0.], 'z', [leg_center_distance, 0., 0.]])
        
        self.dist_to_ground = dist_to_ground
        self.swing_radius = swing_radius

        self.uniform_velocity = uniform_velocity

        super().__init__(self.num_setpoints_drag + self.num_setpoints_swing, leg_center_distance)


    def generate_trajectory(self) -> tuple[list[tuple], list[tuple]]:
        print(self.num_setpoints)
        print(self.num_setpoints_drag + self.num_setpoints_swing)
        print(self.num_setpoints_drag)
        print(self.num_setpoints_swing)

        trajectory_pos_x = 0
        trajectory_pos_y = self.dist_to_ground # init @ dist to ground

        self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]
        
        angle_per_step = math.pi/self.num_setpoints_swing
        theta = 0 

        angles = []
        velocities = []

        for step_counter in range(self.num_setpoints):      
            if step_counter < self.num_setpoints_drag/2 or step_counter > self.num_setpoints_drag/2 + self.num_setpoints_swing: 
                self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]
                
                angles.append((self.leg_ik.angles[0], self.leg_ik.angles[1]))
                velocities.append((self.uniform_velocity, self.uniform_velocity))
                
                trajectory_pos_x += self.swing_radius/(self.num_setpoints_drag/2)
                trajectory_pos_y = self.dist_to_ground
            else:
                theta += angle_per_step
                trajectory_pos_y = self.dist_to_ground + self.swing_radius * math.sin(theta)
                # print('theta: ' + str(theta))
                # print('sin * rad: ' + str(self.swing_radius * math.sin(theta)))
                # print('should be 0: ' + str(math.sin(theta)))
                trajectory_pos_x = self.swing_radius * math.cos(theta)
                self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]
                
                angles.append((self.leg_ik.angles[0], self.leg_ik.angles[1]))
                velocities.append((self.uniform_velocity, self.uniform_velocity))
                
                print(trajectory_pos_y)

            # print(theta)
            # print(self.swing_radius * math.sin(theta))

        return angles, velocities
    
if __name__ == "__main__":
    leg_center_dist_mm = 175.87
    leg_center_dist_m = leg_center_dist_mm / 1000

    swing_radius_m = 0.05

    drag_time = 0.5
    swing_time = 0.5
    refresh_rate = 0.05
    dist_to_ground = -0.25

    # TODO: Fix issue where HalfCircleTrajectory only generates a quarter circle trajectory (ToT)

    trajectory = HalfCircleTrajectory(50, leg_center_dist_m, dist_to_ground, swing_radius_m, 1)
    trajectory.plot()