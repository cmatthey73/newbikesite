# Generated by Django 2.2 on 2019-05-28 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BikeTour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Parcours', models.CharField(default=None, max_length=250)),
                ('Variante', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Descriptif', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('Descr_part_1', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_1', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_1', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_2', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_2', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_2', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_3', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_3', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_3', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_4', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_4', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_4', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_5', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_5', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_5', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_6', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_6', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_6', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_7', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_7', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_7', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_8', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_8', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_8', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_9', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_9', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_9', models.FloatField(blank=True, default=None, null=True)),
                ('Descr_part_10', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('Dist_part_10', models.FloatField(blank=True, default=None, null=True)),
                ('Deniv_part_10', models.FloatField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='But',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('But', models.CharField(default=None, max_length=250)),
                ('Descriptif', models.CharField(blank=True, default=None, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Type', models.CharField(default=None, max_length=250)),
                ('Descriptif', models.CharField(blank=True, default=None, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Perfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(default=None)),
                ('Distance', models.FloatField(default=None)),
                ('Temps', models.DurationField(default=None)),
                ('Remarques', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('Dénivelé', models.FloatField(blank=True, default=None, null=True)),
                ('Vitesse_max', models.FloatField(blank=True, default=None, null=True)),
                ('FC_moy', models.FloatField(blank=True, default=None, null=True)),
                ('FC_max', models.FloatField(blank=True, default=None, null=True)),
                ('Temps_part_1', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_2', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_3', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_4', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_5', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_6', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_7', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_8', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_9', models.DurationField(blank=True, default=None, null=True)),
                ('Temps_part_10', models.DurationField(blank=True, default=None, null=True)),
                ('Refparcours', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='biketours.BikeTour')),
            ],
        ),
        migrations.AddField(
            model_name='biketour',
            name='But',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biketours.But'),
        ),
        migrations.AddField(
            model_name='biketour',
            name='Type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biketours.Type'),
        ),
    ]
