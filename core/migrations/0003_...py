from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_emaillog_and_customer_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='template_type',
            field=models.CharField(
                choices=[('text', 'Plain Text'), ('html', 'HTML')],
                default='text',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='is_html',
            field=models.BooleanField(default=False),
        ),
    ]