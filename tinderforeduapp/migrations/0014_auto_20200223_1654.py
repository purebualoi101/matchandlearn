# Generated by Django 3.0 on 2020-02-23 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tinderforeduapp', '0013_auto_20200223_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='whocomment',
            field=models.CharField(max_length=200, null=True, verbose_name='username'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tinderforeduapp.Userinfo'),
        ),
    ]