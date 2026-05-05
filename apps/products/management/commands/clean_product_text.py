from django.core.management.base import BaseCommand

from apps.products.models import Product

# Characters to normalize
_REPLACEMENTS = {
    '\xa0': ' ',   # non-breaking space → regular space
}


def _clean(text):
    for bad, good in _REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text.strip()


class Command(BaseCommand):
    help = 'Replace non-breaking spaces and other scraped artefacts in product text fields.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would change without writing to the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        updated = 0

        for product in Product.objects.only('id', 'name', 'description', 'specifications'):
            new_desc  = _clean(product.description)
            new_specs = _clean(product.specifications)

            if new_desc != product.description or new_specs != product.specifications:
                if not dry_run:
                    product.description    = new_desc
                    product.specifications = new_specs
                    product.save(update_fields=['description', 'specifications'])
                updated += 1
                if options['verbosity'] >= 2:
                    self.stdout.write(f'  {"(dry) " if dry_run else ""}cleaned: {product.name}')

        label = 'Would update' if dry_run else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{label} {updated} product(s).'))
