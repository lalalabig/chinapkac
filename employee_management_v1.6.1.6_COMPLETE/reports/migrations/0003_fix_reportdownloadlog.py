# Fixed migration for ReportDownloadLog model
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.core.validators
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_bulkdownloadpackage_reports_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportDownloadLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_time', models.DateTimeField(auto_now_add=True, verbose_name='下载时间')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('downloader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_downloads', to=settings.AUTH_USER_MODEL, verbose_name='下载人')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='download_logs', to='reports.report', verbose_name='关联报告')),
            ],
            options={
                'verbose_name': '下载日志',
                'verbose_name_plural': '下载日志',
                'ordering': ['-download_time'],
            },
        ),
    ]
