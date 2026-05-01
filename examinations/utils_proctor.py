
def analyze_snapshot(image_file, client_data=None):
    """
    Analyze image for proctoring (dummy implementation)
    - Returns: (trust_score, issue_type, face_data)
    """
    # If client provides explicit analysis, trust it (Client-side AI)
    if client_data:
        return (
            client_data.get('trust_score', 1.0), 
            client_data.get('issue_type', None), 
            client_data.get('face_data', None)
        )

    # AI Proctoring is disabled on server side due to constraints
    # Always return full trust score
    return 1.0, None, None

def _extract_face_box(landmarks, w, h):
    """
    Dummy implementation
    """
    return None
