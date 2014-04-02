#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

    Alternative Internet Readme Generator
    Rolf Jagerman, Wendo Sabée, Laurens Versluis, Martijn de Vos
    TU Delft

This project reads the JSON files generated by the crawler and generates a table from the statistics.


Usage:

To generate and write a table to a specific and read from a specific directory, use:

    python generate_readme.py -o [the-file-to-write-to] -d [the-directory-to-read-from]

Otherwise, to use "readme.md" and "projects" as defaults, use:

    python generate_readme.py

"""

from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime, timedelta
import logging
import json
import os
import codecs

DESCRIPTION_MAX_LENGTH = 400


def get_projects(path):
    """
    Gets a list of projects with name and description that exist in the specified directory.
    """

    project_files = filter(lambda x: x.endswith('.json'), os.listdir(path))

    projects = []
    for project_file in project_files:
        project_file = '%s%s%s' % (path, os.sep, project_file)
        logging.debug('Loading %s' % project_file)

        project_data = open(project_file)
        current_project = json.load(project_data)
        projects.append(current_project)

    return projects


def get_markdown_page_header():
    header = '# Alternative Internet\n' + \
             'Project statistics fetched from [Ohloh](https://www.ohloh.net).\n' +\
             '\n' + \
             '[< Back to list](README.md)\n' + \
             '\n'
    return header


def get_markdown_table_header(columns, add_links, sort_on=None):
    if add_links:
        linked_columns = columns.copy()
        for key in linked_columns.keys():
            if not key == sort_on:
                linked_columns[key] = '[%s](TABLE_%s.md)' % (linked_columns[key], linked_columns[key].replace(' ', '_').upper())
        return get_markdown_table_header(linked_columns, add_links=False)
    else:
        return '%s%s%s\n' % ('| ', ' | '.join(columns.values()), ' |')


def get_markdown_table_divider(columns, columns_align_right=[]):
    divider = columns.copy()
    for key in divider.keys():
        if key in columns_align_right:
            divider[key] = '-' * (len(divider[key]) - 1) + ':'
        else:
            divider[key] = '-' * len(divider[key])

    return get_markdown_table_header(divider, add_links=False)


def get_markdown_table_totals(columns, projects):
    total_entry = {}
    for key in columns.keys():
        entries = filter(lambda k: key in k.keys(), projects)

        if key == 'min_month':
            total_time = timedelta(0)

            for x in entries:
                entry_time = (datetime.utcnow() - datetime.strptime(x[key], '%Y-%m-%dT%H:%M:%SZ')) if not x[key] is None else timedelta(0)
                total_time = total_time + entry_time

            # datetime.strftime() doesn't like years before 1900, so we'll just use a modified isotime() instead
            total_entry[key] = "%sZ" % ((datetime.utcnow() - total_time).isoformat().strip().split(".")[0])
        else:
            try:
                total_entry[key] = sum(int(project[key]) if (not project[key] is None and project[key].isdigit()) else 0 for project in entries)
            except:
                total_entry[key] = 0

        if total_entry[key] == 0:
            total_entry[key] = '-'

    total_entry['name'] = '**Total:**'

    return get_markdown_table_entry(columns, total_entry, False)


def get_markdown_table_entry_format_name(entry):
    project_anchor = filter(lambda c: c.isalpha() or c == " ", entry).replace(' ', '-').lower()
    return '[%s](README.md#%s)' % (entry, project_anchor)


def get_markdown_table_entry_format_timedelta(td):
    sday = 60 * 60 * 24  # one day
    if td.total_seconds() < sday * 30:  # ~one month
        return '<1 month'
    elif td.total_seconds() < sday * 356:  # ~one year
        return '%s month(s)' % int(td.total_seconds() / (sday * 30))
    else:
        return '%s year(s)' % int(td.total_seconds() / (sday * 356))


def get_markdown_table_entry(columns, project, add_links):
    format_functions = {'name': lambda s, l: get_markdown_table_entry_format_name(s) if l else s,
                        'updated_at': lambda s, l: datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d'),
                        'total_contributor_count': lambda s, l: '{:,}'.format(int(s)),
                        'total_commit_count': lambda s, l: '{:,}'.format(int(s)),
                        'total_code_lines': lambda s, l: '<{:,} K'.format(1) if (int(s) / 1000) <= 1 else '{:,} K'.format(int(s) / 1000),
                        'min_month': lambda s, l: '%s' % get_markdown_table_entry_format_timedelta(datetime.utcnow() - datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')),
                        'description': lambda s, l: '%s...' % s[:DESCRIPTION_MAX_LENGTH] if len(s) > DESCRIPTION_MAX_LENGTH else s,
                        'factoids': lambda s, l: ', '.join(s) if not s is None else '-'
                        }

    entry = []
    for key in columns.keys():
        try:
            entry.append(format_functions[key](project[key], add_links))
        except:
            entry.append(project[key] if key in project.keys() and not project[key] is None else '-')

    return '%s%s%s\n' % ('| ', ' | '.join(entry), ' |')


def get_sorted_list(dictionary, sort_on='name', sort_reverse=False):
    unknown_entry = -99999 if sort_reverse else 'zzzzz'

    if len(filter(lambda k: sort_on in k.keys(), dictionary)) < 1:
        raise Exception('Column \'%s\' not found in any of the entries' % sort_on)

    logging.info('Sorting on \'%s\'' % sort_on)

    try:
        sorted_list = sorted(dictionary, key=lambda k: (int(k[sort_on]) if (not k[sort_on] is None and k[sort_on].isdigit()) else k[sort_on]) if sort_on in k.keys() and not k[sort_on] is None else unknown_entry)
    except:
        sorted_list = dictionary
        
    if sort_reverse:
        sorted_list.reverse()

    return sorted_list


def write_output(projects, table_columns, output='readme.md', sort_on='name', sort_reverse=False, add_links=False, add_totals=False, columns_align_right=[]):

    with codecs.open(output, 'w', 'utf-8-sig') as output_file:
        if add_links:
            header = get_markdown_page_header()
            output_file.write(header)

        header = get_markdown_table_header(table_columns, add_links, sort_on)
        output_file.write(header)

        header = get_markdown_table_divider(table_columns, columns_align_right)
        output_file.write(header)

        for project in get_sorted_list(projects, sort_on, sort_reverse):
            try:
                logging.debug('Parsing %s' % project['name'])
                entry = get_markdown_table_entry(table_columns, project, add_links)
                output_file.write(entry)
            except:
                logging.warning('Parsing entry failed (%s)' % project)

        if add_totals:
            header = get_markdown_table_totals(table_columns, projects)
            output_file.write(header)

    logging.info('Wrote table to %s' % output)


def run_parser(directory='projects', output='readme.md', sort_on='name', sort_reverse=False, add_links=False, generate_all=False, add_totals=False):
    # Proposed by Pouwelse (Project name, #commits, #LinesOfCode, Age in years, Description)
    table_columns = OrderedDict([('name', 'Name'), ('total_commit_count', 'Commits'), ('total_code_lines', 'LOC'),
                                 ('min_month', 'Age'), ('description', 'Description')])

    # Original table columns
    # table_columns = OrderedDict([('name', 'Name'), ('main_language', 'Language'), ('min_month', 'Age'),
    #                              ('updated_at', 'Last activity'), ('total_code_lines', 'LOC'),
    #                              ('total_commit_count', 'Commits'), ('total_contributor_count', 'Contributors')])

    table_columns_default_reverse = ['updated_at', 'total_code_lines', 'total_commit_count', 'total_contributor_count']
    table_columns_align_right = ['total_code_lines', 'total_commit_count', 'total_contributor_count', 'min_month',
                                 'updated_at']

    projects = get_projects(directory)
    logging.info('Loaded %s projects' % len(projects))

    if generate_all:
        for key in table_columns.keys():
            write_output(projects=projects, table_columns=table_columns,
                         output='TABLE_%s.md' % table_columns[key].upper().replace(' ', '_'), sort_on=key,
                         sort_reverse=(key in table_columns_default_reverse), add_links=add_links, add_totals=add_totals,
                         columns_align_right=table_columns_align_right)
    else:
        write_output(projects=projects, table_columns=table_columns, output=output, sort_on=sort_on,
                     sort_reverse=sort_reverse, add_links=add_links, add_totals=add_totals,
                     columns_align_right=table_columns_align_right)


def main():
    """
    Main entry point of the application, execution starts here
    """
    description = 'Parses JSON files generated by the alternative internet crawler and generates a markdown table.'
    parser = ArgumentParser(description=description)

    parser.add_argument('-d', '--directory', action='store', dest='directory', metavar='directory/',
                        default='projects', required=False, help='Directory to read the JSON files from')
    parser.add_argument('-o', '--output', action='store', dest='output', metavar='output.md', default='readme.md',
                        required=False, help='File to write the generated table to')
    parser.add_argument('-s', '--sort', action='store', dest='sort', metavar='column', default='name', required=False,
                        help='Column to sort on (named as used in the JSON files)')
    parser.add_argument('-r', '--reverse', action='store_true', dest='sort_reverse', required=False,
                        help='Sort in reverse order')
    parser.add_argument('-l', '--add-links', action='store_true', dest='add_links', required=False,
                        help='Link from header to sorted versions, plus link from entries to readme.md')
    parser.add_argument('-a', '-all', action='store_true', dest='generate_all', required=False,
                        help='Generate all files as TABLE_COLUMN_NAME.md (-s, -r, -o are ignored)')
    parser.add_argument('-t', '--totals', action='store_true', dest='add_totals', required=False,
                        help='Add totals of all columns as the last entry')
    parser.add_argument('--debug', action='store_true', dest='debug', required=False, help='Enable debug output')

    args = parser.parse_args()
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    logging.debug(args)

    run_parser(directory=args.directory, output=args.output, sort_on=args.sort, sort_reverse=args.sort_reverse,
               add_links=args.add_links, generate_all=args.generate_all, add_totals=args.add_totals)


if __name__ == "__main__":
    main()