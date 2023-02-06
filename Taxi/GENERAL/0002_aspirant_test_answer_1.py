from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('recruiting', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='aspirant',
            name='test_answer_1',
            field=models.TextField(
                blank=True,
                default=None,
                help_text='Развернутый ответ на вопрос',
                null=True,
            ),
        ),
    ]
