#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

    Alternative Internet Crawler
    Rolf Jagerman, Wendo Sabée, Laurens Versluis, Martijn de Vos
    TU Delft

This crawler reads the projects from the alternative internet github page and finds additional information on Ohloh. It
then writes the information to a bunch of JSON files.


Usage:

To crawl and place the resulting JSON information in a specified directory, use:

    python crawl_readme.py -a [your-ohloh-api-key] -d [the-directory-to-store-in]

To write to the default directory ("projects"), simply omit the -d parameter:

    python crawl_readme.py -a [your-ohloh-api-key]

"""

from argparse import ArgumentParser
import logging
import json
import re
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import urlopen
    from urllib import urlencode
try:
    from elementtree import ElementTree
except ImportError:
    from xml.etree import ElementTree


def get_readme():
    """
    Gets the contents of the README file from the alternative internet github page.
    """
    return urlopen('https://raw.github.com/redecentralize/alternative-internet/master/README.md')


def get_projects():
    """
    Gets a list of projects with name and description that exist on the alternative internet github readme file.
    """
    projects = {}
    current_project = ''
    for line in get_readme():
        if line[:3] == '## ':
            pass
        elif line[:4] == '### ':
            current_project = line[4:].rstrip()
            projects[current_project] = {'name': current_project, 'description': ''}
        elif current_project != '' and line.rstrip() != '':
            projects[current_project]['description'] += line.rstrip()
    return projects


def get_ohloh_api_request(url, api_key, params=None):
    """
    Sends an API request to Ohloh and returns the resulting xml tree or raises an exception if an error occurred.

    Keyword arguments:
    url -- The request url to get
    api_key -- The Ohloh API key to use
    params -- Additional parameters to send
    """
    parameters = {'api_key': api_key}
    if params is not None:
        for key, value in params.iteritems():
            parameters[key] = value

    xml = urlopen('%s?%s' % (url, urlencode(parameters)))

    tree = ElementTree.parse(xml)
    error = tree.getroot().find("error")
    if error is not None:
        raise Exception(ElementTree.tostring(error))
    return tree


def get_ohloh_project_information(project_name, api_key):
    """
    Gets basic information about a project by using Ohloh's API

    Keyword arguments:
    project_name -- The project name to look for
    api_key -- The Ohloh API key to use
    """
    results = get_ohloh_api_request('https://www.ohloh.net/p.xml', api_key, {'query': project_name, 'sort': 'relevance'})
    if results.find('result/project/id') is None:
        raise Exception("Could not find project %s on Ohloh" % project_name)

    project = results.find('result/project')
    return {'ohloh_id': project.findtext('id'),
            'ohloh_name': project.findtext('name'),
            'ohloh_description': project.findtext('description'),
            'ohloh_analysis': project.findtext('analysis_id'),
            'tags': [tag.text for tag in project.iterfind('tags/tag')]}


def get_ohloh_code_analysis(project_id, api_key):
    """
    Gets more advanced code analysis about a project using Ohloh's API

    Keyword arguments:
    project_id -- The Ohloh project id of the project
    api_key -- The Ohloh API key to use
    """
    results = get_ohloh_api_request('https://www.ohloh.net/p/%s/analyses/latest.xml' % project_id, api_key)
    analysis = results.find("result/analysis")
    if analysis is None:
        raise Exception("Could not get Ohloh code analysis for project id %s" % project_id)

    return {'total_code_lines': analysis.findtext('total_code_lines'),
            'total_commit_count': analysis.findtext('total_commit_count'),
            'total_contributor_count': analysis.findtext('total_contributor_count'),
            'twelve_month_commit_count': analysis.findtext('twelve_month_commit_count'),
            'twelve_month_contributor_count': analysis.findtext('twelve_month_contributor_count'),
            'updated_at': analysis.findtext('updated_at'),
            'min_month': analysis.findtext('min_month'),
            'max_month': analysis.findtext('max_month'),
            'factoids': [f.text.strip() for f in analysis.iterfind('factoids/factoid')],
            'main_language': analysis.findtext('main_language_name')}


def get_ohloh_information(project, api_key):
    """
    Gets additional information about a project from Ohloh if it exists.

    Keyword arguments:
    project -- The project name to get the information for
    api_key -- The Ohloh API key to use
    """
    information = {}
    try:
        information.update(get_ohloh_project_information(project, api_key))
        if information['ohloh_analysis'] != '':
            information.update(get_ohloh_code_analysis(information['ohloh_id'], api_key))
    except Exception as e:
        logging.error(e.message)
    return information


def run_crawler(api_key, directory='projects'):
    """
    Extracts the projects from the alternative internet page on github and downloads additional data from Ohloh.

    Keyword arguments:
    api_key -- The Ohloh API key to use
    directory -- The directory to store the resulting JSON files in
    """
    projects = get_projects()
    for idx, (project, information) in enumerate(projects.iteritems()):
        filtered_name = re.sub(r'[^a-zA-Z0-9 \-\(\)]*', '', project)
        logging.info('Processing %d/%d: %s' % (idx+1, len(projects), project))
        information.update(get_ohloh_information(project, api_key))
        json.dump(information, open('%s/%s.json' % (directory, filtered_name), 'w'))


def main():
    """
    Main entry point of the application, execution starts here
    """
    logging.getLogger().setLevel(logging.INFO)
    description = 'Crawls the projects on the alternative internet github page and adds additional data from Ohloh.'
    parser = ArgumentParser(description=description)

    parser.add_argument('-a', '--api', action='store', dest='api', metavar="api", default='', required=True,
                        help='Your Ohloh API key.')

    parser.add_argument('-d', '--directory', action='store', dest='directory', metavar="directory",
                        default='projects', required=False, help='Directory to store the resulting JSON files in.')

    args = parser.parse_args()

    run_crawler(api_key=args.api, directory=args.directory)


if __name__ == "__main__":
    main()