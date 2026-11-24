# pylint: disable=invalid-name

from django.db import migrations


def forwards_clear_comment_pii(apps, schema_editor):
    Comment = apps.get_model("django_comments", "Comment")
    database = schema_editor.connection.alias

    Comment.objects.using(database).update(user_email="", ip_address=None)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_squashed"),
        ("django_comments", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            forwards_clear_comment_pii,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
