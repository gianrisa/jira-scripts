__author__ = 'gianfrancorisaliti'
#

# This is pre condition : MAPPING the fields value from the project A_old need a mapping to the project A_new
# This is pre condition : MAPPING the fields value from the project B_old need a mapping to the project B_new
# This is a note : SOURCE the fields mapping shall happen in a XLS or in a simple way.
# This is a note : SOURCE the fields mapping shall happen in a XLS or in a simple way.
# This is a note : SOURCE the fields mapping shall be take into account from 1:1 and N:1 relations
#
# first step get the number of issues from the project A_old and the project B_old
#
# create the empty issues in jira for project A_new and project B_new
#
# read the issue links of the project A_old and create the link in the project A_new ( type link as well )
#
# read the issue links of the project B_old and create the link in the project B_new ( type link as well )
#
# read the issue field in project A_old then read the mapping A_old A_new and update the
#      same issue key corresponding to the mapping in project A_new
#
# repeat the last step for all the mapped fields in A_old to A_new
#
# repeat the last 2 steps for all the issues contained in A_old.
#
# repeat the last 3 steps for the project B_old.
#
# mapping : table with the mapped field and values
#
#   issuetype table mapping
#   A_old          A_new
#   Bug            Defect
#   Information    Defect
#   Change Request Improvement
#

# mapping = { "issuetype" : { "Bug":"Defect", "Information":"Defect"} }
#