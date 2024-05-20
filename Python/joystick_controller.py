import pygame


class JoystickController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No joystick found.")
            pygame.quit()
            exit()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Initialized joystick: {self.joystick.get_name()}")

        self.prev_motion = "00000"
        self.prev_speed = 0
        self.prev_spd_motion = [0, 0, 0, 0, 0, 0]
        self.buttons = [0] * self.joystick.get_numbuttons()

    def is_joystick_at_rest(self, axis_values, rest_threshold=0.3):
        flag = True
        for val in axis_values:
            if abs(val) > rest_threshold:
                flag = False
        return flag

    def calculate_speed(self, axis_values):
        # Exclude the unwanted axis (axis_values[3])
        if not self.is_joystick_at_rest(axis_values):
            valid_axes = axis_values[:3]

            # Find the axis with the greatest absolute value
            max_axis = max(valid_axes, key=abs)

            full_speed = (
                (axis_values[3] * -1) + 1
            ) * 200  # Reverse -> Positive -> Perceentage
            speed = int(abs(max_axis) * full_speed)
            graduated_speed = (full_speed // 25 * 25)
            # Calculate the speed based on the max axis value
            if self.prev_motion[3] == "U" or self.prev_motion[3] == "D":
                return int(full_speed) // 25 * 25
            return graduated_speed
        else:
            return 0

    def detect_motion(self, axis_values, hat_values, threshold=0.3, rest_threshold=0.3):
        if self.is_joystick_at_rest(axis_values, rest_threshold):
            return "00000", 0, [0, 0, 0, 0, 0, 0]  # Return rest motion and speed 0
            

        left_right = axis_values[0]
        forward_backward = axis_values[1]
        rotation = axis_values[2]
        up_down = hat_values[1]
        roll = hat_values[0]
        speed = self.calculate_speed(
            axis_values
        )  # Adjust the axis used for speed calculation

        motion = ""
                # print(total_spd)
        if abs(forward_backward) > threshold:
            if forward_backward > 0:
                motion += "B"
            else:
                motion += "F"
        else:
            motion += "0"

        if abs(left_right) > threshold + 0.1:
            if left_right > 0:
                motion += "R"
            else:
                motion += "L"
        else:
            motion += "0"

        if abs(rotation) > threshold + 0.1:
            if rotation > 0:
                motion += "R"
            else:
                motion += "L"
        else:
            motion += "0"
        if hat_values[1] > 0:
            motion += "U"
        elif hat_values[1] < 0:
            motion += "D"
        else:
            motion += "0"

        if hat_values[0] > 0:
            motion += "R"
        elif hat_values[0] < 0:
            motion += "L"
        else:
            motion += "0"



        total_spd = [
            round(forward_backward) + (round(left_right)) + (round(rotation)),
            -(speed * up_down),
            round(-forward_backward) + (round(left_right)) + (round(-rotation)),
            round(-forward_backward) + (round(-left_right)) + (round(rotation)),
            -(speed * up_down),
            round(forward_backward) + round((-left_right)) + (round(-rotation)),
        ]

        min_val = -400
        max_value = 400
        total_spd = [sorted([min_val, i * speed, max_value])[1] for i in total_spd]

        if motion[0] == "B":
            total_spd[0] -= 100
            total_spd[5] -= 250
            total_spd[2] += 25
        elif motion[0] == "F":
            total_spd[2] -= 40
            total_spd[3] -= 40
            total_spd[5] += 30
        elif motion[1] == "L":
            total_spd[0] -= 5
            total_spd[2] -= 1

            total_spd[3] = 0
            total_spd[5] = 0

        elif motion[1] == "R":
            total_spd[0] = 0
            total_spd[2] = 0

            total_spd[3] +=60
        elif motion[4] == "R":
            total_spd[1] = speed
            total_spd[4] = -speed
        elif motion[4] == "L":
            total_spd[1] = -speed
            total_spd[4] = speed
        total_spd = [sorted([min_val, i, max_value])[1] for i in total_spd]
        return motion, speed, total_spd

    def detect_changed_motion(
        self, axis_values, hat_values, threshold=0.3, rest_threshold=0.1
    ):
        motion_result = self.detect_motion(
            axis_values, hat_values, threshold, rest_threshold
        )

        if (
            motion_result[0] != "00000"
            or motion_result[0] != self.prev_motion
            or motion_result[1] != self.prev_speed
            or motion_result[2] != self.prev_spd_motion
        ):
            self.prev_motion, self.prev_speed, self.prev_spd_motion = motion_result
            if self.prev_motion == "00000":
                self.prev_speed = 0
                self.prev_spd_motion = [0, 0, 0, 0, 0, 0]
            return self.prev_motion, self.prev_speed, self.prev_spd_motion
        else:
            return "00000", 0, [0, 0, 0, 0, 0, 0]

    def get_buttons(self, button_states):
        for i in range(len(button_states)):
            if button_states[i]:
                self.buttons[i] = 1 - self.buttons[i]
        return self.buttons[:3] + self.buttons[4:5]