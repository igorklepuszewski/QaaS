from django.db import migrations

from user.models import Role


def create_roles(apps, schema_editor):
    Role.objects.get_or_create(id=1)
    Role.objects.get_or_create(id=2)
    Role.objects.get_or_create(id=3)


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_role_user_roles"),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
