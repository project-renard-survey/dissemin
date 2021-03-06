# Generated by Django 2.2.10 on 2020-02-27 10:07

import caching.base
import datetime
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django_countries.fields
import papers.baremodels
import papers.models

# Populate OaiSources
def populate_oai_sources(apps, schema_editor):
    OaiSource = apps.get_model('papers', 'OaiSource')

    oai_sources = [
        ('arxiv', 'arXiv', False, 10, 'preprint', 'http://export.arxiv.org/oai2'),
        ('hal', 'HAL', False, 10, 'preprint', 'https://api.archives-ouvertes.fr/oai/hal/'),
        ('cairn', 'Cairn', False, 10, 'preprint', None),
        ('pmc', 'PubMed Central', False, 10, 'preprint', 'https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi'),
        ('doaj', 'DOAJ', True, 10, 'journal-article', None),
        ('persee', 'Persée', True, 10, 'preprint', None),
        ('zenodo', 'Zenodo', False, 15, 'preprint', None),
        ('numdam', 'Numdam', False, 10, 'journal-article', None),
        ('base', 'BASE', False, -2, 'preprint', None),
        ('researchgate', 'ResearchGate', False, -10, 'journal-article', None),
        ('crossref', 'Crossref', False, 20, 'journal-article', None),
        ('orcid', 'ORCID', False, 1, 'other', None),
        ]

    # Auto-create all the Oai Sources when this module is imported
    for identifier, name, oa, priority, pubtype, endpoint in oai_sources:
        OaiSource.objects.get_or_create(
            identifier=identifier,
            defaults={
                'name' : name,
                'oa' : oa,
                'priority' : priority,
                'default_pubtype' : pubtype,
                'endpoint' : endpoint,
            }
        )

class Migration(migrations.Migration):

    replaces = [('papers', '0001_initial_squashed_0038_add_index_on_last_modified'), ('papers', '0039_populate_oai_sources'), ('papers', '0040_institutions_for_orcid'), ('papers', '0041_institution_country'), ('papers', '0042_increase_homepage_length'), ('papers', '0043_institutions_multiple_identifiers'), ('papers', '0044_country_and_no_cascading_deletion'), ('papers', '0045_institution_coords'), ('papers', '0046_cleanup_countries'), ('papers', '0047_cleanup_orcid_researchers'), ('papers', '0048_remove_paper_researchers'), ('papers', '0049_filter_future_dates'), ('papers', '0050_rename_last_update'), ('papers', '0051_alter_last_update'), ('papers', '0052_researcher_visible'), ('papers', '0053_add_endpoint_to_oai_sources'), ('papers', '0054_populate_oai_endpoints'), ('papers', '0055_remove_namevariant'), ('papers', '0056_remove_unused_fields'), ('papers', '0057_todolist'), ('papers', '0058_correct_crossref_pub_types'), ('papers', '0059_remove_django_geojson')]

    initial = True

    dependencies = [
        ('publishers', '0001_initial'),
        ('statistics', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('identifiers', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, null=True, size=None)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('stats', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='statistics.AccessStatistics')),
            ],
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first', models.CharField(max_length=256)),
                ('last', models.CharField(max_length=256)),
                ('full', models.CharField(db_index=True, max_length=513)),
                ('best_confidence', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ['last', 'first'],
                'unique_together': {('first', 'last')},
            },
            bases=(models.Model, papers.baremodels.BareName),
        ),
        migrations.CreateModel(
            name='OaiSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=300, unique=True)),
                ('endpoint', models.URLField(max_length=300, null=True)),
                ('restrict_set', models.CharField(max_length=300, null=True)),
                ('name', models.CharField(max_length=100)),
                ('oa', models.BooleanField(default=False)),
                ('priority', models.IntegerField(default=1)),
                ('default_pubtype', models.CharField(choices=[('journal-article', 'Journal article'), ('proceedings-article', 'Proceedings article'), ('book-chapter', 'Book chapter'), ('book', 'Book'), ('journal-issue', 'Journal issue'), ('proceedings', 'Proceedings'), ('reference-entry', 'Entry'), ('poster', 'Poster'), ('report', 'Report'), ('thesis', 'Thesis'), ('dataset', 'Dataset'), ('preprint', 'Preprint'), ('other', 'Other document')], max_length=64)),
                ('last_update', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc))),
            ],
            options={
                'verbose_name': 'OAI source',
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Researcher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('homepage', models.URLField(blank=True, max_length=1024, null=True)),
                ('role', models.CharField(blank=True, max_length=128, null=True)),
                ('orcid', models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ('empty_orcid_profile', models.NullBooleanField()),
                ('last_harvest', models.DateTimeField(blank=True, null=True)),
                ('harvester', models.CharField(blank=True, max_length=512, null=True)),
                ('current_task', models.CharField(blank=True, choices=[('init', 'Preparing profile'), ('orcid', 'Fetching publications from ORCID'), ('crossref', 'Fetching publications from CrossRef'), ('base', 'Fetching publications from BASE'), ('core', 'Fetching publications from CORE'), ('oai', 'Fetching publications from OAI-PMH'), ('clustering', 'Clustering publications'), ('stats', 'Updating statistics')], max_length=64, null=True)),
                ('visible', models.BooleanField(default=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='papers.Department')),
                ('institution', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='papers.Institution')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.Name')),
                ('stats', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='statistics.AccessStatistics')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaperWorld',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stats', models.ForeignKey(default=papers.models.create_default_stats, on_delete=django.db.models.deletion.SET_DEFAULT, to='statistics.AccessStatistics')),
            ],
            options={
                'verbose_name': 'Paper World',
            },
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024)),
                ('fingerprint', models.CharField(max_length=64, unique=True)),
                ('pubdate', models.DateField()),
                ('authors_list', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('last_modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('visible', models.BooleanField(default=True)),
                ('doctype', models.CharField(blank=True, choices=[('journal-article', 'Journal article'), ('proceedings-article', 'Proceedings article'), ('book-chapter', 'Book chapter'), ('book', 'Book'), ('journal-issue', 'Journal issue'), ('proceedings', 'Proceedings'), ('reference-entry', 'Entry'), ('poster', 'Poster'), ('report', 'Report'), ('thesis', 'Thesis'), ('dataset', 'Dataset'), ('preprint', 'Preprint'), ('other', 'Other document')], max_length=64, null=True)),
                ('oa_status', models.CharField(blank=True, default='UNK', max_length=32, null=True)),
                ('pdf_url', models.URLField(blank=True, max_length=2048, null=True)),
                ('task', models.CharField(blank=True, max_length=512, null=True)),
                ('todolist', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, papers.baremodels.BarePaper),
        ),
        migrations.CreateModel(
            name='OaiRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=512, unique=True)),
                ('splash_url', models.URLField(blank=True, max_length=1024, null=True)),
                ('pdf_url', models.URLField(blank=True, max_length=1024, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('keywords', models.TextField(blank=True, null=True)),
                ('contributors', models.CharField(blank=True, max_length=4096, null=True)),
                ('pubtype', models.CharField(blank=True, choices=[('journal-article', 'Journal article'), ('proceedings-article', 'Proceedings article'), ('book-chapter', 'Book chapter'), ('book', 'Book'), ('journal-issue', 'Journal issue'), ('proceedings', 'Proceedings'), ('reference-entry', 'Entry'), ('poster', 'Poster'), ('report', 'Report'), ('thesis', 'Thesis'), ('dataset', 'Dataset'), ('preprint', 'Preprint'), ('other', 'Other document')], max_length=64, null=True)),
                ('journal_title', models.CharField(blank=True, max_length=512, null=True)),
                ('container', models.CharField(blank=True, max_length=512, null=True)),
                ('publisher_name', models.CharField(blank=True, max_length=512, null=True)),
                ('issue', models.CharField(blank=True, max_length=64, null=True)),
                ('volume', models.CharField(blank=True, max_length=64, null=True)),
                ('pages', models.CharField(blank=True, max_length=64, null=True)),
                ('pubdate', models.DateField(blank=True, null=True)),
                ('doi', models.CharField(blank=True, db_index=True, max_length=1024, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('priority', models.IntegerField(default=1)),
                ('about', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.Paper')),
                ('journal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='publishers.Journal')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='publishers.Publisher')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.OaiSource')),
            ],
            options={
                'verbose_name': 'OAI record',
            },
            bases=(models.Model, papers.baremodels.BareOaiRecord),
        ),
        migrations.AddField(
            model_name='department',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.Institution'),
        ),
        migrations.AddField(
            model_name='department',
            name='stats',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='statistics.AccessStatistics'),
        ),
        migrations.RunPython(
            code=populate_oai_sources
        ),
    ]
