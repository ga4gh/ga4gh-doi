import pandas as pd


def CSVtoXML(inputfile,outputfile):
    if not inputfile.lower().endswith('.csv'):
        print('Expected A CSV File')
        return 0
    if not outputfile.lower().endswith('.xml'):
        print('Expected a XML file')
        return 0

    try:
        df=pd.read_csv(inputfile)
    except FileNotFoundError:
        print('CSV file not found')
        return 0
    att=df.columns    

    entireop='''<?xml version="1.0" encoding="UTF-8"?>
<doi_batch xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.crossref.org/schema/4.3.6 http://www.crossref.org/schemas/crossref4.3.6.xsd" xmlns="http://www.crossref.org/schema/4.3.6" version="4.3.6">
<head>
<doi_batch_id>''' + str(df[att[16]][1]) + '''</doi_batch_id>
<timestamp>''' + str(df[att[17]][1]) + '''</timestamp>
<depositor>
<depositor_name>''' + str(df[att[14]][1]) + '''</depositor_name>
<email_address>''' + str(df[att[15]][1]) + '''</email_address>
</depositor>
<registrant>''' + str(df[att[13]][1]) + '''</registrant>
</head>
<body>
'''
    rowop=''
    for j in range(1,len(df)):
        rowop += addStandard(df, att, j)

    entireop=entireop+rowop+"</body>\n</doi_batch>"
    with open(outputfile,'w') as f:
        f.write(entireop)


def addStandard(df, att, j):
    return '''<standard>
 <standard_metadata language="en">
 <contributors>
<organization sequence="first" contributor_role="author">''' + str(df[att[0]][j]) + '''</organization>
</contributors>
<titles>
<title>'''+ str(df[att[1]][j]) +'''</title>
</titles>
<designators>
<std_as_published undated="ASTM C1062">
<std_designator>'''+ str(df[att[2]][j]) +'''</std_designator>
</std_as_published>
</designators>
<approval_date>
<month>'''+ str(df[att[3]][j]) +'''</month>
<day>'''+ str(df[att[4]][j]) +'''</day>
<year>'''+ str(df[att[5]][j]) +'''</year>
</approval_date>
<publisher>
<publisher_name>'''+ str(df[att[6]][j]) +'''</publisher_name>
<publisher_place>'''+ str(df[att[7]][j]) +'''</publisher_place>
</publisher>
<standards_body>
<standards_body_name>'''+ str(df[att[8]][j]) +'''</standards_body_name>
<standards_body_acronym>'''+ str(df[att[9]][j]) +'''</standards_body_acronym>
</standards_body>
<doi_data>
<doi>'''+ str(df[att[11]][j]) +'''</doi>
<resource>'''+ str(df[att[12]][j]) +'''</resource>
</doi_data>
</standard_metadata>
</standard>
'''

CSVtoXML("Copy of Product Approval Management - PRC tracker - DOI Tracking.csv","testoutput.xml")