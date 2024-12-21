# HAND-Gesture-Control
## Gesture Summary Table

| **Gesture**               | **Action**                  | **Side**  | **Description**                                                                 |
|---------------------------|-----------------------------|-----------|---------------------------------------------------------------------------------|
| **Thumb–Index Pinch**     | Left Click (hold/release)  | Left Hand | If thumb–index distance < `CLICK_THRESHOLD`, calls `mouseDown()`. Release on separation. |
| **Thumb–Pinky Pinch**     | Right Click (single)       | Left Hand | If thumb–pinky distance < `CLICK_THRESHOLD`, performs one right-click.          |
| **Thumb–Pinky Pinch**     | Lock/Unlock Mouse          | Right Hand| If thumb–pinky distance < `PINCH_THRESHOLD`, lock mouse; separate to unlock.    |
| **Index–Middle Distance** | Dynamic Mouse Speed        | Right Hand| Closer fingers => slower speed, farther => faster.                             |
| **Index Finger (dx, dy)** | Actual Mouse Movement      | Right Hand| Moves cursor by `(dx, dy) * speed`, ignoring tiny jitter (`dead_zone`).         |



# Below is a concise list of all the “commands” or gestures the code supports, along with how they work. The script essentially splits hand usage into two zones:

Left side of the screen → Left hand → Clicks
Right side of the screen → Right hand → Mouse movement
1) Left-Hand Commands (Clicks)
Thumb–Index Pinch (Thumb tip near Index tip)

Triggers a “Left Click”.
As soon as they come close (within the CLICK_THRESHOLD distance), the code does pyautogui.mouseDown().
When you separate them, it does pyautogui.mouseUp(), effectively releasing the left click.
Thumb–Pinky Pinch (Thumb tip near Pinky tip)

Triggers a single “Right Click”.
As soon as they come close, the code calls pyautogui.click(button='right') once, then waits until they separate again before allowing another right click.
2) Right-Hand Commands (Mouse Movement)
Thumb–Pinky Pinch (Thumb tip near Pinky tip)

Locks the mouse movement.
If the distance between thumb and pinky is below the PINCH_THRESHOLD, the mouse “freezes” at its current position and will not move until you un-pinch (thumb–pinky distance goes above threshold).
This is useful if you want to hold the mouse still while you rest or reposition your hand.
Index–Middle Distance (Used for Speed Control)

The code measures how far apart your Index finger tip (landmark 8) and Middle finger tip (landmark 12) are.
A smaller distance means slower movement, a larger distance means faster movement.
In code, this is the dist_index_middle; it’s used to compute a dynamic speed factor speed = clamp(raw_speed, min_speed, max_speed).
By default, you can tweak parameters like min_speed, max_speed, and scale_divisor to adjust how quickly speed scales.
Moving the Mouse

With the mouse “unlocked” (thumb–pinky not pinched):
The code checks how much the Index finger has moved since the last frame (dx, dy).
It multiplies that by the dynamic speed factor (based on Index–Middle distance).
It calls pyautogui.moveTo(new_x, new_y) to move the mouse on screen.
3) Additional Details
Dead Zone

A small threshold (dead_zone) that ignores minor jitter in finger movement. If |dx| < dead_zone and |dy| < dead_zone, the mouse won’t move. This helps stabilize the cursor if your hand trembles slightly.
Press ‘q’ to Quit

In the code, if you press the q key, the loop breaks and the webcam window closes.
Resolution & FPS

The script sets the camera to 1280×720 at 60 FPS if supported. You can tweak it if your camera or PC struggles with that resolution.
Left vs. Right Side

The code checks the bounding box center of the detected hand.
If the center is left of the webcam’s frame center, the code treats it as “Left Hand” (click commands). If it’s right, it’s “Right Hand” (mouse commands).

That’s it! These are all the commands and how the code handles them.
