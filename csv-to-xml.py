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

    df.columns = df.iloc[0]
    att=df.columns    

    # Check if first header contains <>
    if "<" not in str(df.columns[0]) and ">" not in str(df.columns[0]):
        df = df[1:]

    entireop='<?xml version="1.0" encoding="UTF-8"?>\n'\
             '<doi_batch xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.crossref.org/schema/4.3.6 http://www.crossref.org/schemas/crossref4.3.6.xsd" xmlns="http://www.crossref.org/schema/4.3.6" version="4.3.6">\n'\
             '<head>\n'\
             '<doi_batch_id>' + str(df["<doi_batch_id>"][1]) + '</doi_batch_id>\n'\
             '<timestamp>' + str(df["<timestamp>"][1]) + '</timestamp>\n'\
             '<depositor>'\
             '<depositor_name>' + str(df["<depositor_name>"][1]) + '</depositor_name>\n'\
             '<email_address>' + str(df["<email_address>"][1]) + '</email_address>\n'\
             '</depositor>\n'\
             '<registrant>' + str(df["<registrant>"][1]) + '</registrant>\n'\
             '</head>\n'\
             '<body>\n'\

    rowop=''
    for j in range(1,len(df)):
        rowop += addStandard(df, att, j)

    entireop=entireop+rowop+"</body>\n</doi_batch>"
    with open(outputfile,'w') as f:
        f.write(entireop)


def addStandard(df, att, j):
    return '<standard>\n'\
           '<standard_metadata language="en">\n'\
           '<contributors>'\
           '<organization sequence="first" contributor_role="author">' + str(df["<organization>"][j]) + '</organization>\n'\
           '</contributors>\n'\
           '<titles>'\
           '<title>'+ str(df["<title>"][j]) +'</title>\n'\
           '</titles>\n'\
           '<designators>\n'\
           '<std_as_published undated="ASTM C1062">\n'\
           '<std_designator>'+ str(df["<std_designator>"][j]) +'</std_designator>\n'\
           '</std_as_published>\n'\
           '</designators>\n'\
           '<approval_date>\n'\
           '<month>'+ str(df["<month>"][j]) +'</month>\n'\
           '<day>'+ str(df["<day>"][j]) +'</day>\n'\
           '<year>'+ str(df["<year>"][j]) +'</year>\n'\
           '</approval_date>\n'\
           '<publisher>\n'\
           '<publisher_name>'+ str(df["<publisher_name>"][j]) +'</publisher_name>\n'\
           '<publisher_place>'+ str(df["<publisher_place>"][j]) +'</publisher_place>\n'\
           '</publisher>\n'\
           '<standards_body>\n'\
           '<standards_body_name>'+ str(df["<standards_body_name>"][j]) +'</standards_body_name>\n'\
           '<standards_body_acronym>'+ str(df["<standards_body_acronym>"][j]) +'</standards_body_acronym>\n'\
           '</standards_body>\n'\
           '<doi_data>\n'\
           '<doi>'+ str(df["<doi>"][j]) +'</doi>\n'\
           '<resource>'+ str(df["<resource>"][j]) +'</resource>\n'\
           '</doi_data>\n'\
           '</standard_metadata>\n'\
           '</standard>\n'

#CSVtoXML("Copy of Product Approval Management - PRC tracker - DOI Tracking.csv","testoutput.xml")
