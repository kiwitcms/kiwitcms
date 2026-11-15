# pylint: disable=invalid-name, unused-argument
from django.db import migrations

CIGE_TEMPLATE_NAME = "Context, Intent, Guardrails, Execution"


def forwards(apps, schema_editor):
    database = schema_editor.connection.alias

    template_model = apps.get_model("testcases", "Template")

    template_model.objects.using(database).create(
        name=CIGE_TEMPLATE_NAME,
        text="""**Context**:
- System / environment / actor:
- Tools:
- Load first / load only on failure:

**Intent**:
- Capability under test:
- Pass requires:
- Fail if:
- Evidence required:

**Guardrails** (must NOT):
- delete resources or change production configuration
- expose tokens or credentials
- mark pass from UI text alone
- change Intent without human approval

**Execution** (first path to try; may be repaired if Intent and Guardrails still hold):
1. step
2. step
3. step
""",
    )


def backwards(apps, schema_editor):
    database = schema_editor.connection.alias

    template_model = apps.get_model("testcases", "Template")
    template_model.objects.using(database).filter(name=CIGE_TEMPLATE_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("testcases", "0025_alter_bugsystem_api_url_alter_bugsystem_base_url"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
