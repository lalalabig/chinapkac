# Generated migration for reports application
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0006_alter_user_task_area'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('weekly', '周报'), ('monthly', '月报'), ('summary', '汇总报告')], max_length=20, verbose_name='报告类型')),
                ('report_period', models.CharField(help_text='如：2025-W10 或 2025-M03', max_length=20, verbose_name='报告周期')),
                ('file', models.FileField(upload_to='reports/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'])], verbose_name='报告文件')),
                ('file_size', models.BigIntegerField(default=0, verbose_name='文件大小(字节)')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('submitted', '已提交'), ('reviewed', '已查看'), ('approved', '已批准')], default='submitted', max_length=20, verbose_name='状态')),
                ('is_viewed', models.BooleanField(default=False, verbose_name='是否已查看')),
                ('viewed_at', models.DateTimeField(blank=True, null=True, verbose_name='查看时间')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='审批时间')),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_reports', to='accounts.user', verbose_name='审批人')),
                ('task_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='accounts.taskarea', verbose_name='所属任务区')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_reports', to='accounts.user', verbose_name='上传人')),
                ('viewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='viewed_reports', to='accounts.user', verbose_name='查看人')),
            ],
            options={
                'verbose_name': '报告',
                'verbose_name_plural': '报告',
                'db_table': 'reports_report',
                'ordering': ['-upload_date'],
                'unique_together': {('uploader', 'report_type', 'report_period', 'task_area')},
            },
        ),
        migrations.CreateModel(
            name='ReportDownloadLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_time', models.DateTimeField(auto_now_add=True, verbose_name='下载时间')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('downloader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_downloads', to='accounts.user', verbose_name='下载人')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='download_logs', to='reports.report', verbose_name='关联报告')),
            ],
            options={
                'verbose_name': '下载日志',
                'verbose_name_plural': '下载日志',
                'db_table': 'reports_reportdownloadlog',
                'ordering': ['-download_time'],
            },
        ),
        migrations.CreateModel(
            name='BulkDownloadPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package_name', models.CharField(max_length=200, verbose_name='包名称')),
                ('zip_file', models.FileField(blank=True, null=True, upload_to='download_packages/', verbose_name='ZIP文件')),
                ('status', models.CharField(choices=[('pending', '待处理'), ('processing', '处理中'), ('completed', '已完成'), ('failed', '失败')], default='pending', max_length=20, verbose_name='状态')),
                ('total_reports', models.PositiveIntegerField(default=0, verbose_name='报告总数')),
                ('total_size', models.BigIntegerField(default=0, verbose_name='总大小(字节)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_download_packages', to='accounts.user', verbose_name='创建人')),
            ],
            options={
                'verbose_name': '批量下载包',
                'verbose_name_plural': '批量下载包',
                'db_table': 'reports_bulkdownloadpackage',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PackageReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.bulkdownloadpackage')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.report')),
            ],
            options={
                'verbose_name': '包报告关联',
                'verbose_name_plural': '包报告关联',
                'db_table': 'reports_packagereport',
                'unique_together': {('package', 'report')},
            },
        ),
    ]
