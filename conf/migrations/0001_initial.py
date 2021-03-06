# Generated by Django 2.0.1 on 2018-04-26 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JudgeServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=128)),
                ('ip', models.CharField(blank=True, max_length=32, null=True)),
                ('judger_version', models.CharField(max_length=32)),
                ('cpu_core', models.IntegerField()),
                ('memory_usage', models.FloatField()),
                ('cpu_usage', models.FloatField()),
                ('last_heartbeat', models.DateTimeField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('task_number', models.IntegerField(default=0)),
                ('service_url', models.CharField(blank=True, max_length=256, null=True)),
                ('is_disabled', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'judge_server',
            },
        ),
    ]
