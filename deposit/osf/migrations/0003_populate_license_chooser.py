# Generated by Django 2.2.1 on 2019-05-27 11:28

from django.db import migrations

def create_osf_license_choosers(apps, schema_editor):
    """
    Creates LicenseChooser objects for osf repositories as they were hard-coded before introduced model.
    """
    License = apps.get_model('deposit', 'License')
    Repository = apps.get_model('deposit', 'Repository')
    LicenseChooser = apps.get_model('deposit', 'LicenseChooser')

    repos_osf = Repository.objects.filter(protocol='OSFProtocol')
    for repo in repos_osf:
        # Default license
        license = License.objects.get(uri='https://dissem.in/deposit/license/no-license/')
        LicenseChooser.objects.create(repository=repo, license=license, transmit_id='563c1cf88c5e4a3877f9e965', position=0, default=True)

        # Non-default licenses
        license_list = [
            ('https://creativecommons.org/publicdomain/zero/1.0/', '563c1cf88c5e4a3877f9e96c', 0),
            ('https://creativecommons.org/licenses/by/4.0/', '563c1cf88c5e4a3877f9e96a', 1),
        ]
        for license_item in license_list:
            license = License.objects.get(uri=license_item[0])
            LicenseChooser.objects.create(repository=repo, license=license, transmit_id=license_item[1], position=license_item[2], default=False)


def remove_osf_license_choosers(apps, schema_editor):
    """
    Removes license chooser corresponding to osf
    """
    
    LicenseChooser = apps.get_model('deposit', 'LicenseChooser')
    LicenseChooser.objects.filter(repository__protocol='OSFProtocol').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0002_osf_id'),
        ('deposit', '0014_populate_licenses'),
    ]

    operations = [
        migrations.RunPython(create_osf_license_choosers, remove_osf_license_choosers)
    ]
