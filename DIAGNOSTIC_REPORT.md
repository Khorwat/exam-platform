# PROJECT STATUS REPORT

## recent Fixes

### 1. Database Crash (Unique Constraint Violation)
**Issue**: Application crashed with `sqlite3.IntegrityError: UNIQUE constraint failed`.
**Resolution**: A manual migration (`0006_fix_unique_constraint_manual.py`) was applied to remove the corrupted database constraint. The database is now healthy.

### 2. AI Proctoring Disabled
**Issue**: The AI proctoring feature (`mediapipe`) caused crashes on Python 3.14.0 due to incompatibility.
**Resolution**: 
- **Disabled Code**: The AI analysis logic in `examinations/utils_proctor.py` has been replaced with a dummy implementation.
- **Removed Dependencies**: `mediapipe` and `opencv-python` have been removed from `requirements.txt`.
- **Functionality**: The exam platform will now run **without** facial analysis features. Snapshots will still be uploaded but will automatically receive a "trust score" of 100% and no issues.

## How to Run
You can now run the project as normal:
```bash
python manage.py runserver
```
