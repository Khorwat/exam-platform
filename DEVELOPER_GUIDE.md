# Developer Guide

This guide provides information for developers working on the Exam Platform. It covers the project structure, utility scripts, and testing workflows.

## Utility Scripts

The project includes several utility scripts in the root directory to help with debugging and verification. These scripts are standalone and often initialize the Django environment manually.

### Debugging Scripts

These scripts are useful for verifying specific functionalities without running the full server or frontend.

- **`debug_exam_create.py`**: 
  - Simulates an instructor creating an exam via the API.
  - Ensures that questions are correctly linked to the created exam.
  - Usage: `python debug_exam_create.py`

- **`debug_question_create.py`**:
  - Tests the creation of questions (e.g., True/False) via the API.
  - Usage: `python debug_question_create.py`

- **`debug_analytics.py`**:
  - Debugs the analytics generation process.
  - Useful for checking if data for charts/graphs is being calculated correctly.
  - Usage: `python debug_analytics.py`

### Verification Scripts

These scripts are used to verify larger workflows or fixes.

- **`verify_teacher_workflow.py`**:
  - Verifies the end-to-end workflow for a teacher (create question -> create exam -> publish).
- **`verify_exam_edit.py`**:
  - Checks if editing an existing exam works as expected.
- **`verify_results.py`**:
  - Verifies that student results are recorded and displayed correctly.
- **`verify_flow.py`**:
  - Likely verifies the general flow of the application or a specific subsystem.
- **`verify_fix.py`**:
  - A script likely created to verify a specific bug fix (check contents to be sure).
- **`verify_timer.py`**:
  - Checks the exam timer functionality.

### Maintenance Scripts

- **`check_categories.py`**:
  - Lists the total number of question categories and details for each.
  - Usage: `python check_categories.py`

- **`check_exams.py`**:
  - Lists exams and their states (active/inactive, question counts).
  - Usage: `python check_exams.py`

- **`create_superuser.py`**:
  - Helper to quickly create a superuser if one doesn't exist.
  - Usage: `python create_superuser.py`

- **`fix_exam_visibility.py`**:
  - A script to correct issues where exams might not be visible to students (e.g., due to active flags or dates).
- **`show_users.py`**:
  - Lists users in the database (useful for checking test accounts).

## Running Tests

Standard Django tests can be run using:

```bash
python manage.py test
```

## Project Structure Notes

- **`templates/frontend/`**: Contains all the HTML files for the UI.
- **`static/`**: Contains CSS, JS, and images.
- **`manage.py`**: Standard Django entry point.

## Common Issues & Fixes

- **Database Locks**: If using SQLite, be careful running scripts while the server is running write operations.
- **Migrations**: Always run `python manage.py migrate` after pulling changes that affect models.
