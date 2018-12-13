import csv
import glob
import os
import requests
import forecastcards
from goodtables import validate
from urllib.parse import urljoin

class Cardset:
    '''
    Identify where data is, what schema it should conform to, and return a dictionary with locations.
    '''

    github_example_data = {'username':'e-lo','repository':'forecastcards','branch':'master'}

    github_master_schema_loc = {
                'poi'         : "https://raw.github.com/e-lo/forecast-cards/master/spec/en/poi-schema.json",
                "scenario"    : "https://raw.github.com/e-lo/forecast-cards/master/spec/en/scenario-schema.json",
                "project"     : "https://raw.github.com/e-lo/forecast-cards/master/spec/en/project-schema.json",
                "observations": "https://raw.github.com/e-lo/forecast-cards/master/spec/en/observations-schema.json",
                "forecast"    : "https://raw.github.com/e-lo/forecast-cards/master/spec/en/forecast-schema.json",
                }

    fc_path = os.path.dirname(os.path.realpath(__file__))
    local_example_data_loc = os.path.join(fc_path,'examples')
    #print (local_example_data_loc)

    def __init__(self,
                 data_loc = local_example_data_loc,
                 select_projects = [],
                 exclude_projects = [],
                 schemas = {},
                 schema_locs = github_master_schema_loc,
                ):

        self.card_locs = {'poi'         : [],
                          'scenario'    : [],
                          'observations': [],
                          'forecast'    : [],
                          'project'     : []}


        self.schema_locs = schema_locs # dict by card type of urls to JSON files or schema instances

        # validate schemas
        ### TODO

        # start with none, then fill in as they are validated
        self.data_locs = []

        # list of all projects
        self.projects = []

        # validation status
        self.validated_projects   = []
        self.unvalidated_projects = []
        self.invalid_projects     = []

        # valid project requires following valid components
        self.validity_requires    = ['project','poi','observations','scenario','forecast']

        # add initial projects
        self.add_projects(data_loc, select_projects=select_projects, exclude_projects=exclude_projects)

    def validate_project(self, p_card_locs, schema_locs={}, validity_requires = []):

        if not schema_locs:
            schema_locs = self.schemas_locs

        if not validity_requires:
            validity_requires = self.validity_requires

        ## todo validate against local schemas
        valid        = True
        fail_reports = []

        for card_type, locs in p_card_locs.items():
            #print ("validating",card_type, locs)

            ##todo add other validation checks here
            for card in locs:
                report = validate(card ,schema=requests.get(schema_locs[card_type]).json())
                if not report['valid']:
                    if card_type in validity_requires:
                        valid = False
                    print ("Validation Error:", card)
                    fail_reports.append(report)

        return valid, fail_reports

    def check_project_id(self, project_id, select_projects=[], exclude_projects=[]):
        '''
        :returns: True if project should be added; False if it shouldn't
        '''
        # check to see if project should be added
        if project_id in self.projects:
            print("Excluding", project_id, " already in cardset")
            return False
        elif select_projects and project_id not in select_projects:
            print("Excluding", project_id, " because it isn't in project list")
            return False
        elif exclude_projects and project_id in exclude_projects:
            print("Excluding", project_id, " because it is in the exclusion list")
            return False
        else:
            return True

    def add_github_projects(self, data_loc, select_projects=[], exclude_projects=[], subdirs  = ['forecastcards/examples']):
        '''
        Identifies valid forecast card projects from a github repository and adds them to the Cardset.card_locs
        Updates the Cardset list of validated projects.
        Will not add a project that has already been added to the cardset.

        :param data_loc: A dictionary with info about the github repository to use, with keys username, repository, branch.
        :type data_loc: dict
        :param select_projects: list of project_ids to import, to the exclusion of others
        :type select_projects: list
        :param exclude_projects: list of project_ids NOT to import
        :type exclude_projects: list
        :returns: list of project validation reports that failed
        :param subdirs: list of subdirectory strings to look for cards in
        :type subdirs: list of strings

        Note:
        This is messy right now b/c we have to loop though several times.
        1. to find project IDs and their directories that we want to import
        2. to find all the files in those directories
        3. to validate the project once we have all those files together

        It would be a lot easier if we were able to take the directory names as the project id or similar.
        '''
        import requests
        import re

        repo_loc = forecastcards.api_github_url(
            username = data_loc['username'],
            repository = data_loc['repository'],
            branch = data_loc['branch'])

        repo_raw = forecastcards.raw_github_url(
            username = data_loc['username'],
            repository = data_loc['repository'],
            branch = data_loc['branch'])


        projdirs_to_import = {}
        cards_by_project = {}

        r = requests.get(repo_loc)
        rj = r.json()
        #if verbose: print(rj)
        card_locs = {
               "poi": [],
               "scenario": [],
               "project": [],
               "observations": [],
               "forecast": [],
        }

        # First loop through is to find all the projects that we want to import
        # We need to get their project ids as well as the folders they live in
        for file in rj['tree']:
            #print (file['path'])

            # don't look at things that aren't files
            if file['type']!='blob': continue

            # split path into a list
            path_list = file['path'].split("/")

            # don't look in wrong subdirs
            if subdirs and not any(s in file['path'] for s in subdirs): continue

            # find project*.csv and get project id
            if path_list[-1][-4:].lower()==".csv" and path_list[-1][0:7].lower() == "project":
                print("opening",urljoin(repo_raw,file['path']))
                # open project*csv to see if we have a good project id

                proj_csv = list(forecastcards.get_csv_from_url(urljoin(repo_raw,file['path'])))
                #print(proj_csv)

                assert(proj_csv[0][0] == 'project_id')
                project_id   = proj_csv[1][0].strip().lower()

                project_path = os.path.dirname(file['path'])
                #print(project_path)

                # check to see if we should be adding this project
                if not self.check_project_id(project_id, select_projects=select_projects, exclude_projects=exclude_projects):
                    continue

                # add this directory to the list to import, and to overall project lists
                projdirs_to_import[project_path] = project_id
                cards_by_project[project_id] = {
                    'project' : [urljoin(repo_raw,file['path'])],
                    'scenario': [],
                    'forecast': [],
                    'observations' :[],
                    'poi':[],
                }
                self.projects.append(project_id)
                self.unvalidated_projects.append(project_id)


        # second loop back through files to find the ones in the right project directory
        for file in rj['tree']:

            #make sure you should be importing this file
            if not any( pdirs in file['path'] for pdirs in projdirs_to_import.keys() ):
                continue

            ## don't look at things that aren't files
            if file['type']!='blob': continue

            # split path into a list
            path_list = file['path'].split("/")

            if path_list[-1][-4:].lower()!=".csv": continue

            if path_list[-1][0:8].lower()=="scenario":
                project_path = os.path.dirname(file['path'])
                project_id = projdirs_to_import[project_path]
                cards_by_project[project_id]['scenario'].append(urljoin(repo_raw,file['path']))
                #print("adding scenario:",file['path'])
            if path_list[-1][0:8].lower()=="forecast":
                project_path = os.path.dirname(os.path.dirname(file['path']))
                project_id = projdirs_to_import[project_path]
                cards_by_project[project_id]['forecast'].append(urljoin(repo_raw,file['path']))
                #print("adding forecast:",file['path'])
            if path_list[-1][0:12].lower()=="observations":
                project_path = os.path.dirname(os.path.dirname(file['path']))
                project_id = projdirs_to_import[project_path]
                cards_by_project[project_id]['observations'].append(urljoin(repo_raw,file['path']))
                #print("adding observation:",file['path'])
            if path_list[-1][0:3].lower()=="poi":
                project_path = os.path.dirname(file['path'])
                project_id = projdirs_to_import[project_path]
                cards_by_project[project_id]['poi'].append(urljoin(repo_raw,file['path']))
                #print("adding poi:",file['path'])

        #Third loop is through the cards_by_project, which need to be validated all together
        failed_validation_reports = []
        for project_id, cards in cards_by_project.items():
            p_valid, fail_reports = self.validate_project(cards,self.schema_locs)

            if p_valid:
                self.validated_projects.append(project_id)
                self.unvalidated_projects.remove(project_id)
                print("adding",project_id," - valid")
                for k,v in self.card_locs.items():
                    v += cards[k]
                else:
                    self.invalid_projects.append(project_id)

            failed_validation_reports.append(fail_reports)
        return failed_validation_reports

    def add_local_projects(self, data_loc, select_projects=[], exclude_projects=[]):

        #find projects by searching for the project csv file
        project_loc = os.path.join(data_loc,'**/project*.csv')

        failed_validation_reports = []

        ##todo make more windows safe
        for filepath in glob.iglob(project_loc, recursive=True):
            with open(filepath, 'r') as f:
                proj_csv = list(csv.reader(f))

            assert(proj_csv[0][0] == 'project_id')
            project_id   = proj_csv[1][0].strip().lower()

            project_path = os.path.dirname(filepath)

            #check to see if we should be adding this project
            if not self.check_project_id(project_id, select_projects=select_projects, exclude_projects=exclude_projects):
                continue

            self.projects.append(project_id)
            self.unvalidated_projects.append(project_id)

            p_card_locs = {'poi'         : glob.glob(os.path.join(project_path,'poi*.csv'),recursive=True),
                           'scenario'    : glob.glob(os.path.join(project_path,'scenario*.csv'),recursive=True),
                           'observations': glob.glob(os.path.join(project_path,'**/observations*.csv'),recursive=True),
                           'forecast'    : glob.glob(os.path.join(project_path,'**/forecast*.csv'),recursive=True),
                           'project'     : [filepath]}

            p_valid, fail_reports = self.validate_project(p_card_locs,self.schema_locs)

            if p_valid:
                self.validated_projects.append(project_id)
                self.unvalidated_projects.remove(project_id)
                print("adding",project_id," - valid")
                for k,v in self.card_locs.items():
                    v += p_card_locs[k]
            else:
                self.invalid_projects.append(project_id)

            failed_validation_reports.append(fail_reports)

        return failed_validation_reports


    def add_projects(self, data_loc, select_projects=[], exclude_projects=[],subdirs  = ['forecastcards/examples']):
        '''

        '''
        self.data_locs.append(data_loc)

        if type(data_loc) is dict:
            reports = self.add_github_projects(data_loc,select_projects=select_projects, exclude_projects=exclude_projects, subdirs  = subdirs)

        else:
            reports = self.add_local_projects(data_loc,select_projects=select_projects, exclude_projects=exclude_projects)