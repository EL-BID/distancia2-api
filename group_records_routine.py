# sudo crontab -e
# 5,35 * * * * cd /opt/dist2/distancia2-api && /opt/dist2/env/bin/python /opt/dist2/distancia2-api/group_records_routine.py

import os
import logging
import datetime as dt

import django
from django.conf import settings
import numpy as np
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "distancia2.settings")
django.setup()

from cams.models import Record, GroupedRecord

LOGGING_FORMAT = '%(asctime)s %(funcName)s|%(lineno)d [%(threadName)s]: %(message)s'
file_handler = logging.handlers.TimedRotatingFileHandler('/opt/dist2/logs/group_records', 'midnight')

logging.basicConfig(level=logging.INFO,
    format=LOGGING_FORMAT, handlers=[file_handler],
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def get_distances(graphical):
    return [line[4] for line in graphical['distance_lines']]

def percentile(n):
    def percentile_(array):
        return np.percentile(array, n)
    return percentile_

def calculate_average(distances_array):
    return sum(distances_array.apply(sum)) / sum(distances_array.apply(len))

def count_people_breaking_distance(graphical):
    return len(set([box
        for line in graphical['distance_lines']
        if line[4] < settings.SECURE_DISTANCE
        for box in [line[0], line[1]]
    ]))

def init_routine():
    utcnow = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    today = utcnow.replace(hour=0, minute=0, second=0, microsecond=0)

    # TODO: change date sorter on database
    first_record = Record.objects.last()
    first_date = first_record.date.replace(hour=0, minute=0, second=0, microsecond=0)

    if today == first_date:
        logger.warning('La rutina inicializará despues del primer dia de procesamiento')
        return

    logger.info(f'Se inciara la primera rutina de procesamiento desde {first_date} hasta {today}')

    for delta in range((today - first_date).days):
        group_records(first_date + dt.timedelta(days=delta))

def group_records(first_date=None):
    utcnow = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

    if not first_date:
        last_record = GroupedRecord.objects.first()

        if last_record is None:
            return init_routine()
        first_date = last_record.group_date + dt.timedelta(minutes=30)

    if first_date.date() < utcnow.date():
        last_date = first_date + dt.timedelta(days=1)
        last_date = last_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        last_date = utcnow.replace(minute=(utcnow.minute // 30) * 30, second=0, microsecond=0)

    if first_date == last_date:
        logger.warning('La rutina debe correr cada media hora')
        return

    logger.error(f'Se agrupara desde la fecha {first_date} hasta {last_date}')
    queryset = Record.objects.filter(date__gte=first_date, date__lt=last_date)

    if not queryset:
        logger.warning('No hay registros para agrupar')
        return

    columns = ['date', 'channel_id', 'amount_people', 'graphical']
    records = pd.DataFrame.from_records(
        queryset.values(*columns)
    )

    records.rename(columns={'date': 'group_date'}, inplace=True)

    fields_to_group = ['channel_id', pd.Grouper(key='group_date', freq='30min')]

    all_records_operators = {
        'amount_records': ('amount_people', 'count'),
    }

    more_than_zero_people_operators = {
        'amount_people': ('amount_people', 'sum'),
        'percentile90_amount_people': ('amount_people', percentile(90))
    }

    more_than_one_people_operators = {
        'minimal_distance': ('minimal_distance', 'min'),
        'average_distance': ('distances', calculate_average),
        'amount_people_breaking_secure_distance': ('amount_people_breaking_secure_distance', 'sum'),
    }

    grouped_records_0 = records \
        .groupby(fields_to_group).aggregate(**all_records_operators)

    grouped_records_1 = records[records['amount_people'] > 0] \
        .groupby(fields_to_group).aggregate(**more_than_zero_people_operators)


    more_than_one_people = records[records['amount_people'] > 1].copy()
    more_than_one_people['distances'] = more_than_one_people['graphical'].apply(get_distances)
    more_than_one_people['minimal_distance'] = more_than_one_people['distances'].apply(min)
    more_than_one_people['amount_people_breaking_secure_distance'] = more_than_one_people['graphical'].apply(count_people_breaking_distance)

    grouped_records_2 = more_than_one_people \
        .groupby(fields_to_group).aggregate(**more_than_one_people_operators)

    result_grouped = pd.concat(
        [grouped_records_0, grouped_records_1, grouped_records_2],
        axis=1).fillna(0).reset_index()

    GroupedRecord.objects.bulk_create(
        [GroupedRecord(**data) for data in result_grouped.to_dict('records')]
    )


if __name__ == "__main__":
    group_records()
