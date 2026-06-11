import cv2
import time

class LivenessDetector:
    def __init__(self, movement_threshold=15, check_duration=3):
        """
        movement_threshold: pixels the face must move to be considered live
        check_duration: seconds to wait for movement before failing
        """
        self.movement_threshold = movement_threshold
        self.check_duration = check_duration
        
        # Per-student tracking: student_id -> state
        self._state = {}

    def _get_face_center(self, location):
        top, right, bottom, left = location
        cx = (left + right) // 2
        cy = (top + bottom) // 2
        return cx, cy

    def check(self, student_id, location):
        """
        Call every frame for a detected face.
        Returns:
            'live'    - movement detected, person is live
            'checking' - still waiting for movement
            'failed'  - no movement in check_duration seconds (likely photo)
        """
        cx, cy = self._get_face_center(location)
        now = time.time()

        if student_id not in self._state:
            # First time seeing this student - record initial position
            self._state[student_id] = {
                'start_time': now,
                'initial_pos': (cx, cy),
                'max_movement': 0.0,
                'result': 'checking'
            }
            return 'checking'

        state = self._state[student_id]

        # Already determined
        if state['result'] in ('live', 'failed'):
            return state['result']

        # Calculate movement from initial position
        ix, iy = state['initial_pos']
        movement = ((cx - ix) ** 2 + (cy - iy) ** 2) ** 0.5
        state['max_movement'] = max(state['max_movement'], movement)

        if state['max_movement'] >= self.movement_threshold:
            state['result'] = 'live'
            return 'live'

        elapsed = now - state['start_time']
        if elapsed > self.check_duration:
            # Reset and try again instead of permanently failing
            self._state[student_id] = {
                'start_time': now,
                'initial_pos': (cx, cy),
                'max_movement': 0.0,
                'result': 'checking'
            }
            return 'failed'  # shows red briefly then resets

        return 'checking'

    def reset(self, student_id):
        """Reset liveness state for a student (call after attendance marked)"""
        if student_id in self._state:
            del self._state[student_id]

    def reset_all(self):
        self._state.clear()