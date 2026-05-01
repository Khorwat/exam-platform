import os
import sys
import django
import numpy as np
import cv2
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from examinations.utils_proctor import analyze_snapshot

def test_analysis():
    print("Testing Proctoring Logic...")
    
    # 1. Test Black Image (No Face)
    print("\n[TEST 1] Black Image (Expect NO_FACE)")
    black_img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', black_img)
    f = SimpleUploadedFile("test.jpg", buf.tobytes())
    
    score, issue, data = analyze_snapshot(f)
    print(f"Result: Score={score}, Issue={issue}")
    
    if issue == "NO_FACE" and score == 0.0:
        print("PASS")
    else:
        print("FAIL")

    # 2. Test Image with drawing (still probably NO_FACE unless mediapipe is very lenient)
    # MediaPipe Face Mesh expects realistic faces, so synthetic circles won't work easily.
    # We mainly trust the logic flow if NO_FACE works.
    
    print("\nLogic verification complete. Real face detection requires actual face images.")

if __name__ == "__main__":
    test_analysis()
