
__author__ = 'risalgia'

from jira.client import JIRA
import pprint

import time                                                

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result
    return timed


issue_mapping_old_new = {
    "Data Quality"      : "Defect",
    "Performance"       : "Defect",
    "Change Request"    : "Improvement",
    "Functional defect" : "Defect",
    "UI"                : "Defect"
    }

fields_mapping_old_new = {
    "priority"          : "priority",
    "project"           : "project",
    "summary"           : "summary",
    "description"       : "description",
    "issuetype"         : "issuetype",
    "reporter"          : "reporter"
}


standard_minimum_defect = """{  'customfield_10001': %(phase)s,
                                'customfield_10022': %(Severity)s,
                                'description'      : %(description)s,
                                'environment'      : %(environment)s,
                                'issuetype'        : {'name': %(issuetype)s},
                                'project'          : {'key' : %(project)s},
                                'reporter'         : %(reporter)s,
                                'summary'          : %(summary)s
                            }"""

standard_minimum_uti = """{ 'description': %(description)s,
                            'issuetype'  : {'name': %(issuetype)s},
                            'project'    : {'key' : %(project)s},
                            'reporter'   : %(reporter)s,
                            'summary'    : %(summary)s
                          }"""


standard_minimum_epic = """{  'customfield_10014': 'Epic Name',
                               'description' : %(description)s,
                               'issuetype'   : {'name': %(issuetype)s},
                               'project'     : {'key' : %(project)s},
                               'reporter'    : %(reporter)s,,
                               'summary'     :  %(summary)s
                            }"""

new_standard_fields = {'Defect': {  'customfield_10001': 'Phase',
                                     'customfield_10022': 'Severity',
                                     'description': 'Description',
                                     'environment': 'Environment',
                                     'issuetype': 'Issue Type',
                                     'project': 'Project',
                                     'reporter': 'Reporter',
                                     'summary': 'Summary'},
                       'EPIC': {  'customfield_10014': 'Epic Name',
                                   'description': 'Description',
                                   'issuetype': 'Issue Type',
                                   'project': 'Project',
                                   'reporter': 'Reporter',
                                   'summary': 'Summary'},
                       'Improvement': {  'description': 'Description',
                                          'issuetype': 'Issue Type',
                                          'project': 'Project',
                                          'reporter': 'Reporter',
                                          'summary': 'Summary'},
                       'Sub-task': {  'description': 'Description',
                                       'issuetype': 'Issue Type',
                                       'parent': 'Parent',
                                       'project': 'Project',
                                       'reporter': 'Reporter',
                                       'summary': 'Summary'},
                       'Task': {  'description': 'Description',
                                   'issuetype': 'Issue Type',
                                   'project': 'Project',
                                   'reporter': 'Reporter',
                                   'summary': 'Summary'},
                       'User Story': {  'description': 'Description',
                                         'issuetype': 'Issue Type',
                                         'project': 'Project',
                                         'reporter': 'Reporter',
                                         'summary': 'Summary'}}


# jira connector
def jconnect(jira_param):
    jcon = JIRA(options={'server': jira_param[0]},basic_auth=(jira_param[1], jira_param[2]))
    return jcon

# issues selector
def jissue_query(jinstance, jproj, startAt=0, maxResults=10):
    jquery = '''project=%s'''%(jproj)
    issues = jinstance.search_issues('''project=%s'''%(jproj), startAt=startAt, maxResults=maxResults)
    return issues

# total issue count in project A - Max Key
def jissue_get_last(j_old, project_old):
    j_issues_old_count = jissue_query(j_old, project_old)
    j_issue_max_key = int(j_issues_old_count[0].key.split("-")[1])
    return j_issue_max_key

@timeit
def jissue_get_fields(jira_dict):
    fields = jira_dict['projects'][0]['issuetypes'][0]['fields']    #pprint(fields,indent=2)
    issue_id = jira_dict['projects'][0]['issuetypes'][0]['id']
    project_id = {'id':jira_dict['projects'][0]['id']}
    project_key = {'key':str(jira_dict['projects'][0]['key'])}

    custom_fields_map = {}
    all_fields_map = {}
    required_map = {}

    for field in fields:
        if fields[field].has_key('required'):
            if fields[field]['required']:
                required_map.update({field:fields[field]['name']})
            custom_fields_map.update({field:fields[field]['name']})
    return required_map

@timeit
def jissue_get_mandatory_fields(jira, project):
    issuetype_mandatory = {}
    jproject = jira.project(project)
    for i in jproject.issueTypes:
        j_issue_dict = jira.createmeta(project, issuetypeIds=i.id, expand='projects.issuetypes.fields')
        required_map = jissue_get_fields(j_issue_dict)
        issuetype_mandatory.update({i.name:required_map})
    return issuetype_mandatory

@timeit
# this method is used to get the issue list with references, in case the number of issues is more than 1000
def jissue_get_chunked(jira, project, issue_max_count, chunks=100):
    # list for result.
    result = []
    # step and rest simple calc
    step = issue_max_count/chunks
    rest = issue_max_count%chunks
    # iterate the issue gathering
    for i in range(step):
        result.extend(jissue_query(jira, project, chunks*i, chunks))
    result.extend(jissue_query(jira, project, issue_max_count-rest, rest))
    return result


if __name__ == "__main__":

# first stage issue creation in project from project reference.

    # connect to the old jira server parameters
    j_old_param = ('https://tools.adidas-group.com/jiraold','risalgia','vf4vu15a')
    # the project name shall be given as external parameter
    project = "DIT"
    # perform jira connection
    j_old = jconnect(j_old_param)
    # get the max issues and the issue list - issue contains the issue pointer to the old jira - it can be used to check the needed data.
    # to be migrated like .. links .. attachment .. status.. this is pretty big anyway 
    issue_max_key =  jissue_get_last(j_old, project)    
    # get all the issues in the project pretty expensive operation, this will take a while
    issues_old = jissue_get_chunked(j_old, project, issue_max_key)
    # list older for the issues that need to be created in jira_new empty vector
    issues_list = ['']*issue_max_key+1
    
    # place the value in the right position
    for issue in issues_old:
        issues_list[int(issue.key.split("-")[1])]=issue

    # check and create the list of issue that need to be copying 
    for issue in issues_list:
        # create the issues in jira with reference list
        if issue:
            print "copy from the old jira : - ", issue
        else:
            print "create dummy issue : - ", issue
        
        # issues_list.append(jira.create_issue(fields={'project':{'key': i.project},
        #                                 'summary':i.summary,
        #                                    'description':'',
        #                                    'issuetype':{'name': i.issuetype},
        #                                   }, prefetch=True))

    # jira new server parameters
    j_new_param = ('https://tools.adidas-group.com/jira','risalgia','F@r0nte17')  
    # connect to the new jira and create the issues with empty dummy values
    project = "DIT"
    # perform jira connection
    j_new = jconnect(j_new_param)



def jissue_filed_mapping_controller(j_new, j_old, project_new, project_old, issue_old, issue_new):
    # discover the mandatory fields to be further mapped new project
    new_mandatory_fields = jissue_get_mandatory_fields(j_new, project_new)  

    # discover the mandatory fields to be further mapped old project
    old_mandatory_fields = jissue_get_mandatory_fields(j_old, project_old) 


    # get the relative value of the custom field or of the fields of those issue automatically
    # from the mandatory fields
    for i in issue_old:
        for ii in old_mandatory_fields[i.fields.issuetype.name]:
            print "i.fields.%s"%(ii), eval("i.fields.%s"%(ii))

    # prepare the named dictionary
    for i in new_standard_fields:
        for j in new_standard_fields[i]:
            new_standard_fields[i][j]='%('+j+')s'
