"""File to import postcode csv data, create a new table with 
averaged lat and long coordinates for a given postcode to facilitate 
a search by distance function later"""

import csv

from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from shoes.models import Postcode

class Command(BaseCommand):
    #load australian postcodes with an average coordiante for each
    def add_arguments(self, parser):
        parser.add_argument('csv_path', nargs= '?', default = None)
        parser.add_argument('--force', action = "store_true", help = "Reload even if data exists")
    def handle(self, *args, **options):

        if Postcode.objects.exists() and not options['force']:
            self.stdout.write('Postcodes already loaded. Use --force to reload.')
            return

        default = Path(__file__).resolve().parents[2] / 'data' / 'australian_postcodes.csv'
        path = Path(options['csv_path']) if options['csv_path'] else default
        if not path.exists():
            raise CommandError(f'CSV not found: {path}')

        groups = defaultdict(lambda: {'state': '', 'lat': [], 'lng': [], 'names': []})

        with path.open(newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            needed = {'postcode', 'locality', 'state', 'lat', 'long'}
            missing = needed - set(reader.fieldnames or []) #check that these csv columns exist
            if missing:
                raise CommandError(
                    f'Missing columns {sorted(missing)}. Columns found: {reader.fieldnames}')

            for row in reader:
                code = row['postcode'].strip().zfill(4)   # some files drop the leading 0
                if len(code) != 4 or not code.isdigit():
                    continue
                try:
                    lat, lng = float(row['lat']), float(row['long'])
                except ValueError:
                    continue
                if lat == 0 or lng == 0:                   # dataset uses 0 for "unknown"
                    continue

                g = groups[code]
                g['state'] = row['state'].strip()
                g['lat'].append(lat)
                g['lng'].append(lng)
                name = row['locality'].strip().title()
                if name and name not in g['names']:
                    g['names'].append(name)

        rows = [
            Postcode(
                code=code,
                state=g['state'],
                latitude=sum(g['lat']) / len(g['lat']), #average lat
                longitude=sum(g['lng']) / len(g['lng']), #average long
                suburbs=', '.join(g['names'][:5])[:300],
            )
            for code, g in groups.items()
        ]

        Postcode.objects.all().delete()
        Postcode.objects.bulk_create(rows, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(rows)} postcodes'))   

#make a new dataframe with only the columns i want (or just access these)
#postcode/ locality, state, long, lat,



