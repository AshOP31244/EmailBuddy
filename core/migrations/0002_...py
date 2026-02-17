from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        # Add new fields to Customer
        migrations.AddField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='company',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='status',
            field=models.CharField(
                choices=[
                    ('Interested', 'Interested'),
                    ('Not Interested', 'Not Interested'),
                    ('Busy', 'Busy'),
                    ('Follow-up Later', 'Follow-up Later'),
                ],
                default='Interested',
                max_length=50,
            ),
        ),

        # Update EmailLog
        migrations.AddField(
            model_name='emaillog',
            name='to_email',
            field=models.EmailField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emaillog',
            name='cc_emails',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='bcc_emails',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='subject',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='body_sent',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='template',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='core.template',
            ),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='customer',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='core.customer',
            ),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='status',
            field=models.CharField(
                choices=[('Sent', 'Sent'), ('Failed', 'Failed'), ('Pending', 'Pending')],
                default='Sent', max_length=100,
            ),
        ),
    ]