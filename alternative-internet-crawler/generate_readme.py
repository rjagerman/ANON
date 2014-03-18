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
import logging
import json
import os
import codecs


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


def get_markdown_table_header(columns, add_links):
    if add_links:
        linked_columns = columns
        for key in linked_columns.keys():
            linked_columns[key] = '[%s](TABLE_%s.md)' % (linked_columns[key], linked_columns[key].replace(' ', '_').upper())
        return get_markdown_table_header(linked_columns, add_links=False)
    else:
        return '%s%s%s\n' % ('| ', ' | '.join(columns.values()), ' |')


def get_markdown_table_divider(columns):
    divider = columns
    for key in divider.keys():
        divider[key] = '-' * len(divider[key])
    return get_markdown_table_header(divider, add_links=False)


def get_markdown_table_entry(columns, project, add_links):
    entry = []
    for key in columns.keys():
        try:
            if add_links and key == 'name':
                project_anchor = filter(lambda c: c.isalpha() or c == " ", project[key]).replace(' ', '-').lower()
                entry.append('[%s](README.md#%s)' % (project[key], project_anchor))
            else:
                entry.append(project[key])
        except:
            entry.append('unknown')

    return '%s%s%s\n' % ('| ', ' | '.join(entry), ' |')


def get_sorted_list(dictionary, sort_on='name', sort_reverse=False):
    unknown_entry = -99999 if sort_reverse else 'zzzzz'

    if len(filter(lambda k: sort_on in k.keys(), dictionary)) < 1:
        raise Exception('Column \'%s\' not found in any of the entries' % sort_on)

    sorted_list = sorted(dictionary, key=lambda k: (int(k[sort_on]) if k[sort_on].isdigit() else k[sort_on]) if sort_on in k.keys() else unknown_entry)
    if sort_reverse:
        sorted_list.reverse()

    return sorted_list


def run_parser(directory='projects', output='readme.md', sort_on='name', sort_reverse=False, add_links=False):
    table_columns = OrderedDict([('name', 'Name'), ('updated_at', 'Last activity'),
                                 ('total_contributor_count', 'Contributors'), ('total_code_lines', 'LOC')])

    projects = get_projects(directory)
    logging.info('Loaded %s projects' % len(projects))

    with codecs.open(output, 'w', 'utf-8-sig') as output_file:
        header = get_markdown_table_header(table_columns, add_links)
        output_file.write(header)

        header = get_markdown_table_divider(table_columns)
        output_file.write(header)

        for project in get_sorted_list(projects, sort_on, sort_reverse):
            try:
                logging.debug('Parsing %s' % project['name'])
                entry = get_markdown_table_entry(table_columns, project, add_links)
                output_file.write(entry)
            except:
                logging.warning('Parsing entry failed (%s)' % project)

    logging.info('Wrote table to %s' % output)


def main():
    """
    Main entry point of the application, execution starts here
    """
    logging.getLogger().setLevel(logging.INFO)
    description = 'Parses JSON files generated by the alternative internet crawler and generates a markdown table.'
    parser = ArgumentParser(description=description)

    #parser.add_argument('-a', '--api', action='store', dest='api', metavar="api", default='', required=True,
    #                    help='Your Ohloh API key.')

    parser.add_argument('-d', '--directory', action='store', dest='directory', metavar='directory/',
                        default='projects', required=False, help='Directory to read the JSON files from')
    parser.add_argument('-o', '--output', action='store', dest='output', metavar='output.md', default='readme.md',
                        required=False, help='File to write the generated table to')
    parser.add_argument('-s', '--sort', action='store', dest='sort', metavar='column', default='name', required=False,
                        help='Column to sort on (named as used in the JSON files)')
    parser.add_argument('-r', '--reverse', action='store_true', dest='sort_reverse', required=False,
                        help='Sort in reverse order')
    parser.add_argument('-l', '--add-links', action='store_true', dest='add_links', required=False,
                        help='Link from header to sorted versions, plus link from entried to readme.md')

    args = parser.parse_args()

    run_parser(directory=args.directory, output=args.output, sort_on=args.sort, sort_reverse=args.sort_reverse, add_links=args.add_links)


if __name__ == "__main__":
    main()