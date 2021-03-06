# Generated by Django 2.0.1 on 2018-05-09 09:00

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contest', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_id', models.CharField(db_index=True, max_length=24)),
                ('is_public', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=128)),
                ('description', utils.models.RichTextField()),
                ('input_description', utils.models.RichTextField()),
                ('output_description', utils.models.RichTextField()),
                ('samples', django.contrib.postgres.fields.jsonb.JSONField()),
                ('test_case_id', models.CharField(max_length=32)),
                ('test_case_score', django.contrib.postgres.fields.jsonb.JSONField()),
                ('hint', utils.models.RichTextField(blank=True, null=True)),
                ('languages', django.contrib.postgres.fields.jsonb.JSONField()),
                ('template', django.contrib.postgres.fields.jsonb.JSONField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(blank=True, null=True)),
                ('time_limit', models.IntegerField()),
                ('memory_limit', models.IntegerField()),
                ('spj', models.BooleanField(default=False)),
                ('spj_language', models.CharField(blank=True, max_length=32, null=True)),
                ('spj_code', models.TextField(blank=True, null=True)),
                ('spj_version', models.CharField(blank=True, max_length=32, null=True)),
                ('spj_compile_ok', models.BooleanField(default=False)),
                ('rule_type', models.CharField(max_length=32)),
                ('visible', models.BooleanField(default=True)),
                ('difficulty', models.CharField(max_length=32)),
                ('source', models.CharField(blank=True, max_length=200, null=True)),
                ('total_score', models.IntegerField(blank=True, default=0)),
                ('submission_number', models.BigIntegerField(default=0)),
                ('accepted_number', models.BigIntegerField(default=0)),
                ('statistic_info', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('contest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contest.Contest')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'problem',
                'ordering': ('create_time',),
            },
        ),
        migrations.CreateModel(
            name='ProblemTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'problem_tag',
            },
        ),
        migrations.CreateModel(
            name='SmallProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_id', models.CharField(db_index=True, max_length=24)),
                ('type', models.CharField(max_length=32)),
                ('title', models.CharField(max_length=128)),
                ('description', utils.models.RichTextField()),
                ('options', django.contrib.postgres.fields.jsonb.JSONField(default=list, null=True)),
                ('answer', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('visible', models.BooleanField(default=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(blank=True, null=True)),
                ('submission_number', models.BigIntegerField(default=0)),
                ('accepted_number', models.BigIntegerField(default=0)),
                ('statistic_info', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('is_public', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'small_problem',
                'ordering': ('create_time',),
            },
        ),
        migrations.CreateModel(
            name='SmallTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'small_tag',
            },
        ),
        migrations.AddField(
            model_name='smallproblem',
            name='tags',
            field=models.ManyToManyField(to='problem.SmallTag'),
        ),
        migrations.AddField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(to='problem.ProblemTag'),
        ),
        migrations.AlterUniqueTogether(
            name='smallproblem',
            unique_together={('_id',)},
        ),
        migrations.AlterUniqueTogether(
            name='problem',
            unique_together={('_id', 'contest')},
        ),
    ]
