from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('tests', '0006_test_base_groups')]

    operations = [
        migrations.AddField(
            model_name='testlogs',
            name='answered_number',
            field=models.PositiveSmallIntegerField(
                default=0, help_text='Количество прохождений теста',
            ),
        ),
    ]
