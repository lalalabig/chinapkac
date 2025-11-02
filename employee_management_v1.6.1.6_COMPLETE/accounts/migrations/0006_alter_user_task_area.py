# Generated migration to add default value to task_area field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20251016_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='task_area',
            field=models.CharField(
                blank=True, 
                default='', 
                help_text='工作任务区域', 
                max_length=100, 
                verbose_name='任务区'
            ),
        ),
    ]
