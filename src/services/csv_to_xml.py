import uuid
import pandas as pd
from src.services.suffix_generator import generateSuffix
from src.services.create_records import CreateRecords
from datetime import datetime

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

    # Check if first header contains <>
    if "<" not in str(df.columns[0]) and ">" not in str(df.columns[0]):
        df = df[1:]

    timestamp = datetime.now().strftime("%Y%m%d%H%M")

    entireop='<?xml version="1.0" encoding="UTF-8"?>\n'\
             '<doi_batch xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.crossref.org/schema/4.3.6 http://www.crossref.org/schemas/crossref4.3.6.xsd" xmlns="http://www.crossref.org/schema/4.3.6" version="4.3.6">\n'\
             '<head>\n'\
             '<doi_batch_id>' + str(timestamp) + '</doi_batch_id>\n'\
             '<timestamp>' + str(timestamp) + '</timestamp>\n'\
             '<depositor>\n'\
             '<depositor_name>' + str(df["<depositor_name>"][1]) + '</depositor_name>\n'\
             '<email_address>' + str(df["<email_address>"][1]) + '</email_address>\n'\
             '</depositor>\n'\
             '<registrant>' + str(df["<registrant>"][1]) + '</registrant>\n'\
             '</head>\n'\
             '<body>\n'\

    rowop=''
    standards = []
    batch_uuid = uuid.uuid4()

    for j in range(1,len(df)):  #add suffix if no suffix also check if suffix exists
        xml_part, standard = addStandard(df, j)
        rowop += xml_part
        if standard is not None:
            standard.batch_id = batch_uuid
            standards.append(standard)

    entireop=entireop+rowop+"</body>\n</doi_batch>"

    batch = CreateRecords.create_batch(df, timestamp)
    batch.xml = entireop

    with open(outputfile,'w') as f:
        f.write(entireop)

    return entireop, batch, standards


def addStandard(df, j):
    suffix = str(generateSuffix())

    if str(df["<month>"][j])=="nan" or str(df["<day>"][j])=="nan" or str(df["<year>"][j])=="nan" or str(df["<resource>"][j])=="nan":
        return "", None

    if df['<doi>'][j] == "10.59756xx": #TODO: better checks for if doi already has suffix
        if suffix in df['<doi>']:
            while suffix in df['<doi>']:
                suffix = str(generateSuffix())
            df.loc[j, '<doi>'] = suffix
        else:
            df.loc[j, '<doi>'] = suffix

    doi_value = ("10.59756/" + suffix if df['<doi>'][j]=="10.59756xx"
                 else ("10.59756/" + df['<doi>'][j] if "10.59756/" not in df['<doi>'][j]
                       else df['<doi>'][j]))

    publish_date = datetime(int(df["<year>"][j]), int(df["<month>"][j]), int(df["<day>"][j]))

    standard = CreateRecords.create_standard(df, j, doi_value, publish_date)
    standard.std_designator = str(df["<standards_body_acronym>"][j]) + " " + df['<doi>'][j]
    xml = '<standard>\n'\
          '<standard_metadata language="en">\n'\
          '<contributors>\n'\
          '<organization sequence="first" contributor_role="author">' + str(df["<organization>"][j]) + '</organization>\n'\
          '</contributors>\n'\
          '<titles>\n'\
          '<title>'+ str(df["<title>"][j]).replace("&", "&amp;") +'</title>\n'\
          '</titles>\n'\
          '<designators>\n'\
          '<std_as_published undated="'+ str(df["<std_designator>"][j]) +'">\n'\
          '<std_designator>'+ str(df["<standards_body_acronym>"][j]) + " " + df['<doi>'][j] +'</std_designator>\n'\
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
          '<doi>' + doi_value + '</doi>\n'\
          '<resource>'+ str(df["<resource>"][j]) +'</resource>\n'\
          '</doi_data>\n'\
          '</standard_metadata>\n'\
          '</standard>\n'

    return xml, standard
