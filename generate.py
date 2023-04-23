#!/usr/bin/env python3
"""Generate workday schedule for given year and month.

Copyright (c) 2023 Zdenek Styblik

This file is part of mnbv which is released under MIT License.
See file LICENSE or go to https://github.com/zstyblik/mnbv for full license
details.
"""
import argparse
from datetime import datetime
from datetime import timedelta


def main():
    """Generate printout."""
    args = parse_args()
    dt_ptr = datetime(args.year, args.month, 1)
    delta = timedelta(days=1)
    print('date,hours,description')
    workday_count = 0
    # As long as we're within the same year and month
    while dt_ptr.year == args.year and dt_ptr.month == args.month:
        dow = dt_ptr.weekday()
        if dow >= 0 and dow <= 4:  # pylint: disable=chained-comparison
            # Monday-Friday only
            workday_count = workday_count + 1
            print('{:s},8,'.format(dt_ptr.strftime('%d.%m.%Y')))

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
    return parser.parse_args()


if __name__ == '__main__':
    main()
