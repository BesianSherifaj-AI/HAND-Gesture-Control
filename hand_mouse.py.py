import cv2
import mediapipe as mp
import pyautogui
import math

class HandFaceControl:
    def __init__(self):
        # ---------- Mediapipe setups ----------
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # ---------- Screen info ----------
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

        # ---------- Mouse movement ----------
        self.mouse_locked = False
        self.last_finger_x = None
        self.last_finger_y = None

        # Base speed used if index–middle distance is zero (fallback)
        self.base_speed = 4.5

        # Much bigger speed range and smaller scale divisor
        self.min_speed = 2.0
        self.max_speed = 20.0
        self.scale_divisor = 2.0  # smaller => bigger speed jumps for the same finger spread

        self.dead_zone = 3
        self.PINCH_THRESHOLD = 10
        self.CLICK_THRESHOLD = 10

        # ---------- For color coding ----------
        self.left_color = (255, 0, 0)   # Blue for left
        self.right_color = (0, 0, 255)  # Red for right

        # ---------- Track click states to avoid repeated clicks ----------
        self.left_click_active = False
        self.right_click_active = False

    def process_frame(self, frame):
        """ Process BGR frame for hand detection. """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb_frame)
        return hand_results

    def run_detection(self, hand_results, frame):
        """ Main logic that draws hand boxes and performs mouse control. """
        if not hand_results.multi_hand_landmarks:
            return

        for hand_landmarks in hand_results.multi_hand_landmarks:
            box = self.get_hand_bounding_box(hand_landmarks, frame)
            if not box:
                continue

            hx1, hy1, hx2, hy2, cx, cy = box
            frame_center_x = frame.shape[1] // 2
            is_left_side = (cx < frame_center_x)

            # Draw bounding box
            color = self.left_color if is_left_side else self.right_color
            cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), color, 2)

            # Draw landmarks
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=color, thickness=2)
            )

        # Now do the actual controlling
        for hand_landmarks in hand_results.multi_hand_landmarks:
            box = self.get_hand_bounding_box(hand_landmarks, frame)
            if not box:
                continue

            hx1, hy1, hx2, hy2, cx, cy = box
            frame_center_x = frame.shape[1] // 2
            is_left_side = (cx < frame_center_x)

            if is_left_side:
                self.handle_clicks(hand_landmarks, frame)
            else:
                self.move_mouse(hand_landmarks, frame)

    def get_hand_bounding_box(self, hand_landmarks, frame):
        ih, iw, _ = frame.shape
        x_coords, y_coords = [], []

        for lm in hand_landmarks.landmark:
            x_coords.append(int(lm.x * iw))
            y_coords.append(int(lm.y * ih))

        if not x_coords or not y_coords:
            return None

        x1, x2 = min(x_coords), max(x_coords)
        y1, y2 = min(y_coords), max(y_coords)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return (x1, y1, x2, y2, cx, cy)

    def move_mouse(self, hand_landmarks, frame):
        ih, iw, _ = frame.shape

        thumb = hand_landmarks.landmark[4]
        pinky = hand_landmarks.landmark[20]
        index_finger = hand_landmarks.landmark[8]
        middle_finger = hand_landmarks.landmark[12]

        thumb_x, thumb_y = int(thumb.x * iw), int(thumb.y * ih)
        pinky_x, pinky_y = int(pinky.x * iw), int(pinky.y * ih)
        index_x, index_y = int(index_finger.x * iw), int(index_finger.y * ih)
        middle_x, middle_y = int(middle_finger.x * iw), int(middle_finger.y * ih)

        # Lock/unlock by thumb–pinky pinch
        dist_thumb_pinky = math.hypot(thumb_x - pinky_x, thumb_y - pinky_y)
        if dist_thumb_pinky < self.PINCH_THRESHOLD:
            self.mouse_locked = True
        else:
            if self.mouse_locked:
                # reset last finger
                self.last_finger_x = index_x
                self.last_finger_y = index_y
            self.mouse_locked = False

        if not self.mouse_locked:
            if self.last_finger_x is None or self.last_finger_y is None:
                self.last_finger_x = index_x
                self.last_finger_y = index_y
                return

            # Dynamic speed calculation
            dist_index_middle = math.hypot(index_x - middle_x, index_y - middle_y)
            speed = self.get_dynamic_speed(dist_index_middle)

            dx = index_x - self.last_finger_x
            dy = index_y - self.last_finger_y

            if abs(dx) < self.dead_zone and abs(dy) < self.dead_zone:
                return

            move_x = int(dx * speed)
            move_y = int(dy * speed)

            current_mouse_x, current_mouse_y = pyautogui.position()
            new_x = max(0, min(self.screen_width - 1, current_mouse_x + move_x))
            new_y = max(0, min(self.screen_height - 1, current_mouse_y + move_y))

            pyautogui.moveTo(new_x, new_y)

            self.last_finger_x = index_x
            self.last_finger_y = index_y

    def get_dynamic_speed(self, dist_index_middle):
        if dist_index_middle <= 0:
            return self.base_speed
        raw_speed = dist_index_middle / self.scale_divisor
        speed = max(self.min_speed, min(self.max_speed, raw_speed))
        return speed

    def handle_clicks(self, hand_landmarks, frame):
        ih, iw, _ = frame.shape
        thumb = hand_landmarks.landmark[4]
        index_finger = hand_landmarks.landmark[8]
        pinky = hand_landmarks.landmark[20]

        thumb_x, thumb_y = int(thumb.x * iw), int(thumb.y * ih)
        index_x, index_y = int(index_finger.x * iw), int(index_finger.y * ih)
        pinky_x, pinky_y = int(pinky.x * iw), int(pinky.y * ih)

        dist_thumb_index = math.hypot(thumb_x - index_x, thumb_y - index_y)
        dist_thumb_pinky = math.hypot(thumb_x - pinky_x, thumb_y - pinky_y)

        # Left-click hold
        if dist_thumb_index < self.CLICK_THRESHOLD:
            if not self.left_click_active:
                pyautogui.mouseDown()
                self.left_click_active = True
        else:
            if self.left_click_active:
                pyautogui.mouseUp()
                self.left_click_active = False

        # Right-click once
        if dist_thumb_pinky < self.CLICK_THRESHOLD:
            if not self.right_click_active:
                pyautogui.click(button='right')
                self.right_click_active = True
        else:
            self.right_click_active = False

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    controller = HandFaceControl()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip horizontally
            frame = cv2.flip(frame, 1)

            # Detect hands
            hand_results = controller.process_frame(frame)

            # Main logic
            controller.run_detection(hand_results, frame)

            cv2.imshow('Hand Control w/ Big Speed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
