# Generated by Django 5.1.6 on 2025-02-12 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnuncioBoib',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_id', models.IntegerField()),
                ('fecha', models.DateField()),
                ('boletin', models.CharField(max_length=20)),
                ('numero_boletin', models.IntegerField()),
                ('administracion', models.CharField(max_length=64)),
                ('entidad', models.CharField(max_length=64)),
                ('texto_resolucion', models.TextField()),
                ('link_pdf', models.URLField(max_length=128)),
                ('link_html', models.URLField(max_length=128)),
                ('link_xml', models.URLField(max_length=128)),
                ('numero_registro', models.IntegerField()),
                ('numero_url', models.IntegerField()),
            ],
            options={
                'db_table': 'anuncios_boib',
            },
        ),
    ]
