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
            graduated_speed = (full_speed // 25 * 25) - 50
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
        speed = self.calculate_speed(
            axis_values
        )  # Adjust the axis used for speed calculation

        motion = ""

        total_spd = [
            round(forward_backward) + (round(left_right)) + (round(rotation)),
            -(up_down * speed),
            round(-forward_backward) + (round(left_right)) + (round(-rotation)),
            round(-forward_backward) + (round(-left_right)) + (round(rotation)),
            -(up_down * speed),
            round(forward_backward) + round((-left_right)) + (round(-rotation)),
        ]

        min_val = -400
        max_value = 400
        total_spd = [sorted([min_val, i * speed, max_value])[1] for i in total_spd]

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