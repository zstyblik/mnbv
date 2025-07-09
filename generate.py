#!/usr/bin/env python3
"""Generate workday schedule for given year and month.

Copyright (c) 2023 Zdenek Styblik

This file is part of mnbv which is released under MIT License.
See file LICENSE or go to https://github.com/zstyblik/mnbv for full license
details.
"""
import argparse
import sys
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List

try:
    import requests
except ModuleNotFoundError:
    pass


def get_holidays(year: int, country_code: str | None) -> List:
    """Return list of holidays from Nager Date."""
    if not country_code:
        return []

    if 'requests' not in sys.modules:
        raise ModuleNotFoundError("No module named 'requests'")

    url = "https://date.nager.at/api/v3/publicholidays/{:d}/{:s}".format(
        year, country_code.upper()
    )
    rsp = requests.get(url, timeout=30)
    rsp.raise_for_status()
    return rsp.json()


def main():
    """Generate printout."""
    args = parse_args()
    holidays = get_holidays(args.year, args.country_code)
    holidays = process_holidays(holidays)
    output_cols = {
        'date': '{date:s}',
        'day': '{day:s}',
        'hours': '{hours:d}',
        'description': '{description:s}',
    }
    if not args.include_day_names:
        output_cols.pop('day', None)

    # eg. 'date,day,hours,description'
    output_header = ','.join(output_cols.keys())
    # eg. '{date:s},{day:s},{hours:d},'
    output_fmt = ','.join(output_cols.values())

    dt_ptr = datetime(args.year, args.month, 1)
    delta = timedelta(days=1)
    # Print header
    print('{:s}'.format(output_header))
    workday_count = 0
    # As long as we're within the same year and month
    while dt_ptr.year == args.year and dt_ptr.month == args.month:
        dow = dt_ptr.weekday()
        hdate = dt_ptr.strftime('%Y-%m-%d')

        hours = 0
        description = ''
        if hdate in holidays:
            description = 'public holiday'
        elif dow >= 0 and dow <= 4:  # pylint: disable=chained-comparison
            # Only Monday-Friday count as a working day.
            workday_count = workday_count + 1
            hours = 8

        if dow <= 4 or args.include_weekends:
            print(
                output_fmt.format(
                    date=dt_ptr.strftime('%d.%m.%Y'),
                    day=dt_ptr.strftime('%a'),
                    hours=hours,
                    description=description,
                )
            )

        dt_ptr = dt_ptr + delta

    print('---')
    print(
        'There are {:d} workdays in {:s}. Enjoy!'.format(
            workday_count,
            datetime(args.year, args.month, 1).strftime('%Y/%m')
        )
    )


def parse_args():
    """Return parsed CLI args."""
    dt_now = datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--year',
        type=int,
        default=dt_now.year,
        help='Year',
    )
    parser.add_argument(
        '--month',
        type=int,
        default=dt_now.month,
        help='Month',
    )
    parser.add_argument(
        '--include-day-names',
        action='store_true',
        default=False,
        help='Include name of the day eg. Mon, Tue',
    )
    parser.add_argument(
        '--include-weekends',
        action='store_true',
        default=False,
        help='Include weekends in the output',
    )
    parser.add_argument(
        '--country-code',
        type=str,
        default=None,
        help='Country code according to ISO 3166-1 alpha-2',
    )
    args = parser.parse_args()
    if args.country_code is not None and len(args.country_code) != 2:
        parser.error(
            'Country code "{:s}" seems to be invalid.'.format(
                args.country_code
            )
        )

    return args


def process_holidays(holidays: List) -> Dict[str, str]:
    """Return dates of public holidays."""
    retval = {}
    for holiday in holidays:
        is_public = [
            htype
            for htype in holiday["types"]
            if htype.lower() == "public"
        ]
        if not is_public:
            continue

        hdate = holiday["date"]
        retval[hdate] = holiday["name"]

    return retval


if __name__ == '__main__':
    main()
