from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('examinations', '0005_update_grading_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DROP INDEX IF EXISTS examination_exam_id_fef13f_idx;",
                # In some sqlite versions/django versions, the unique_together might have created a different index.
                # We attempt to drop it by name if it persists.
            ],
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
