from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('tests', '0005_auto_20200605_2352')]

    operations = [
        migrations.AddField(
            model_name='test',
            name='base_groups',
            field=models.ManyToManyField(
                blank=True,
                default=None,
                help_text='Доступность теста для базовых групп',
                limit_choices_to={'name__startswith': 'Агент Яндекс.'},
                related_name='base_groups',
                to='auth.Group',
            ),
        ),
    ]
