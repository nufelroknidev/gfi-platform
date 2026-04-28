import django.contrib.postgres.search
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from django.db import migrations, models


def backfill_search_vector(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    Product = apps.get_model('products', 'Product')
    Product.objects.update(
        search_vector=(
            SearchVector('name',              weight='A') +
            SearchVector('cas_number',        weight='B') +
            SearchVector('e_number',          weight='B') +
            SearchVector('alternative_names', weight='B') +
            SearchVector('description',       weight='C') +
            SearchVector('available_forms',   weight='D') +
            SearchVector('specifications',    weight='D')
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='alternative_names',
            field=models.CharField(blank=True, help_text='Synonyms and trade names for this product. Improves search.', max_length=500),
        ),
        migrations.AddIndex(
            model_name='product',
            index=GinIndex(fields=['search_vector'], name='product_search_vector_gin'),
        ),
        migrations.RunPython(backfill_search_vector, migrations.RunPython.noop),
    ]
