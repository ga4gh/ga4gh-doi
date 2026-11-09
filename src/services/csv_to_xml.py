import io
import uuid
import pandas as pd
from src.services.csv_functions import read_json_cell, read_optional_cell
from src.services.suffix_generator import generateSuffix
from src.services.create_records import CreateRecords
from datetime import datetime


def _xml_escape(value):
    """Escape XML-reserved characters so arbitrary user-entered text or URLs
    are safe to embed as element text or attribute values. & must be replaced
    first so the entities it introduces aren't themselves re-escaped.
    """
    text = str(value)
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))


def _doi_batch_open(schema_version, extra_xmlns=""):
    """Build the opening `<doi_batch>` tag for a given Crossref schema version."""
    return '<?xml version="1.0" encoding="UTF-8"?>\n'\
           '<doi_batch xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '\
           'xsi:schemaLocation="http://www.crossref.org/schema/' + schema_version + ' https://www.crossref.org/schemas/crossref' + schema_version + '.xsd" '\
           'xmlns="http://www.crossref.org/schema/' + schema_version + '"' + extra_xmlns + ' version="' + schema_version + '">\n'


def _doi_batch_head(df, timestamp):
    """Build the `<head>` block shared by every doi_type: batch id, timestamp, depositor, registrant."""
    return '<head>\n'\
           '<doi_batch_id>' + str(timestamp) + '</doi_batch_id>\n'\
           '<timestamp>' + str(timestamp) + '</timestamp>\n'\
           '<depositor>\n'\
           '<depositor_name>' + _xml_escape(df["<depositor_name>"].iloc[0]) + '</depositor_name>\n'\
           '<email_address>' + _xml_escape(df["<email_address>"].iloc[0]) + '</email_address>\n'\
           '</depositor>\n'\
           '<registrant>' + _xml_escape(df["<registrant>"].iloc[0]) + '</registrant>\n'\
           '</head>\n'


def _resolve_doi_value(df, j):
    """Resolve a row's final DOI value.

    If the CSV's <doi> cell is still the "10.59756xx" placeholder, generate and
    record a fresh unique suffix. Otherwise normalize the given value to include
    the registrant prefix if it doesn't already have one.
    """
    suffix = str(generateSuffix())

    if df['<doi>'][j] == "10.59756xx":  # TODO: better checks for if doi already has suffix
        if suffix in df['<doi>']:
            while suffix in df['<doi>']:
                suffix = str(generateSuffix())
            df.loc[j, '<doi>'] = suffix
        else:
            df.loc[j, '<doi>'] = suffix

    return ("10.59756/" + suffix if df['<doi>'][j] == "10.59756xx"
            else ("10.59756/" + df['<doi>'][j] if "10.59756/" not in df['<doi>'][j]
                  else df['<doi>'][j]))


def _run_csv_to_xml(inputfile, outputfile, schema_version, extra_xmlns, doi_type, row_builder):
    """Shared CSV-to-XML pipeline used by every doi_type: validate file extensions,
    parse the CSV, wrap the doi_batch head/body around each row_builder(df, j)
    result, and assemble the Batch record.

    row_builder(df, j) must return (xml_string, record_or_none) per row.
    """
    if isinstance(inputfile, str) and not inputfile.lower().endswith('.csv'):
        print('Expected A CSV File')
        return 0
    if outputfile is not None and not outputfile.lower().endswith('.xml'):
        print('Expected a XML file')
        return 0

    try:
        df = pd.read_csv(inputfile)
    except FileNotFoundError:
        print('CSV file not found')
        return 0

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    entireop = _doi_batch_open(schema_version, extra_xmlns) + _doi_batch_head(df, timestamp) + '<body>\n'

    rowop = ''
    records = []
    batch_uuid = uuid.uuid4()

    for j in range(len(df)):
        xml_part, record = row_builder(df, j)
        rowop += xml_part
        if record is not None:
            record.batch_id = batch_uuid
            records.append(record)

    entireop = entireop + rowop + "</body>\n</doi_batch>"

    batch = CreateRecords.create_batch(df, timestamp, doi_type=doi_type)
    batch.xml = entireop

    if outputfile is not None:
        with open(outputfile, 'w') as f:
            f.write(entireop)

    return entireop, batch, records


def _institution_block_xml(institution):
    """Build one <institution> element from {name, ids: [{type, value}], acronym, place, department}."""
    if not institution:
        return ""

    ids_xml = "".join(
        '<institution_id type="' + _xml_escape(id_entry.get("type", "")) + '">' + _xml_escape(id_entry.get("value", "")) + '</institution_id>\n'
        for id_entry in institution.get("ids", []) if id_entry.get("type") and id_entry.get("value")
    )
    name_xml = ('<institution_name>' + _xml_escape(institution["name"]) + '</institution_name>\n') if institution.get("name") else ""
    acronym_xml = ('<institution_acronym>' + _xml_escape(institution["acronym"]) + '</institution_acronym>\n') if institution.get("acronym") else ""
    place_xml = ('<institution_place>' + _xml_escape(institution["place"]) + '</institution_place>\n') if institution.get("place") else ""
    department_xml = ('<institution_department>' + _xml_escape(institution["department"]) + '</institution_department>\n') if institution.get("department") else ""

    body = name_xml + ids_xml + acronym_xml + place_xml + department_xml
    return ('<institution>\n' + body + '</institution>\n') if body else ""


def _affiliations_xml(affiliations):
    """Build one contributor's <affiliations> block from a list of
    {ror, name, acronym, place} dicts - each becomes one <institution> entry."""
    if not affiliations:
        return ""

    institutions_xml = ""
    for affiliation in affiliations:
        ror = affiliation.get("ror", "")
        name = affiliation.get("name", "")
        if not ror and not name:
            continue
        institutions_xml += _institution_block_xml({
            "name": name,
            "ids": [{"type": "ror", "value": ror}] if ror else [],
            "acronym": affiliation.get("acronym", ""),
            "place": affiliation.get("place", ""),
        })

    return ('<affiliations>\n' + institutions_xml + '</affiliations>\n') if institutions_xml else ""


def _flat_affiliation_xml(contributor):
    """Standards' simple single-string <affiliation> element (Crossref 4.3.6 style)."""
    affiliation = contributor.get("affiliation", "")
    return ('<affiliation>' + _xml_escape(affiliation) + '</affiliation>\n') if affiliation else ""


def _contributors_xml(contributors, first_sequence="additional", affiliation_xml_builder=_flat_affiliation_xml):
    """Build <person_name> entries shared by every doi_type's contributors block.

    first_sequence: sequence attribute for the first contributor with a name -
    "additional" when an organization already took sequence="first" (standards),
    "first" when contributors are the only entries (posted content).
    affiliation_xml_builder(contributor) -> affiliation XML for one contributor,
    since standards uses a flat <affiliation> string and posted content uses a
    nested <affiliations> block of institutions.
    """
    xml = ""
    is_first = True
    for contributor in contributors:
        given_name = contributor.get("first_name", "")
        surname = contributor.get("last_name", "")
        if not given_name and not surname:
            continue

        affiliation_xml = affiliation_xml_builder(contributor)
        orcid = contributor.get("orcid", "")
        orcid_xml = ('<ORCID authenticated="false">https://orcid.org/' + _xml_escape(orcid) + '</ORCID>\n') if orcid else ""

        sequence = first_sequence if is_first else "additional"
        is_first = False
        xml += '<person_name sequence="' + sequence + '" contributor_role="author">\n'\
               '<given_name>' + _xml_escape(given_name) + '</given_name>\n'\
               '<surname>' + _xml_escape(surname) + '</surname>\n'\
               + affiliation_xml + orcid_xml +\
               '</person_name>\n'
    return xml


def _citation_list_xml(citations):
    """Build the optional <citation_list> block from a list of {key, doi, unstructured_citation} dicts."""
    if not citations:
        return ""

    entries_xml = ""
    for index, citation in enumerate(citations, start=1):
        doi = citation.get("doi", "")
        unstructured = citation.get("unstructured_citation", "")
        if not doi and not unstructured:
            continue
        key = citation.get("key") or f"ref{index}"
        unstructured_xml = ('<unstructured_citation>' + _xml_escape(unstructured) + '</unstructured_citation>\n') if unstructured else ""
        doi_xml = ('<doi>' + _xml_escape(doi) + '</doi>\n') if doi else ""
        entries_xml += '<citation key="' + _xml_escape(key) + '">\n' + unstructured_xml + doi_xml + '</citation>\n'

    return ('<citation_list>\n' + entries_xml + '</citation_list>\n') if entries_xml else ""


def _date_block_xml(tag, date):
    """Build a <tag><month>/<day>/<year></tag> block (approval_date, posted_date, acceptance_date)."""
    return '<' + tag + '>\n'\
           '<month>' + str(date.month) + '</month>\n'\
           '<day>' + str(date.day) + '</day>\n'\
           '<year>' + str(date.year) + '</year>\n'\
           '</' + tag + '>\n'


def _abstract_xml(df, j):
    """Build the optional JATS <abstract> block, or "" if no abstract text was given."""
    abstract_text = read_optional_cell(df, j, "<abstract>")
    if not abstract_text:
        return ""

    abstract_title = read_optional_cell(df, j, "<abstract_title>")
    title_xml = ('<title>' + _xml_escape(abstract_title) + '</title>\n') if abstract_title else ""
    return '<abstract xmlns="http://www.ncbi.nlm.nih.gov/JATS1">\n'\
           + title_xml +\
           '<p>' + _xml_escape(abstract_text) + '</p>\n'\
           '</abstract>\n'


def addStandard(df, j):
    if str(df["<month>"][j])=="nan" or str(df["<day>"][j])=="nan" or str(df["<year>"][j])=="nan" or str(df["<resource>"][j])=="nan":
        return "", None

    doi_value = _resolve_doi_value(df, j)

    publish_date = datetime(int(df["<year>"][j]), int(df["<month>"][j]), int(df["<day>"][j]))

    standard = CreateRecords.create_standard(df, j, doi_value, publish_date)
    std_designator = _xml_escape(df["<std_designator>"][j])
    contributors = read_json_cell(df, j, "<contributors>", [])
    xml = '<standard>\n'\
          '<standard_metadata language="en">\n'\
          '<contributors>\n'\
          '<organization sequence="first" contributor_role="author">' + _xml_escape(df["<organization>"][j]) + '</organization>\n'\
          + _contributors_xml(contributors, first_sequence="additional", affiliation_xml_builder=_flat_affiliation_xml) +\
          '</contributors>\n'\
          '<titles>\n'\
          '<title>'+ _xml_escape(df["<title>"][j]) +'</title>\n'\
          '</titles>\n'\
          + _abstract_xml(df, j) +\
          '<designators>\n'\
          '<std_as_published undated="'+ std_designator +'">\n'\
          '<std_designator>'+ std_designator +'</std_designator>\n'\
          '</std_as_published>\n'\
          '</designators>\n'\
          + _date_block_xml("approval_date", publish_date) +\
          '<publisher>\n'\
          '<publisher_name>'+ _xml_escape(df["<publisher_name>"][j]) +'</publisher_name>\n'\
          '<publisher_place>'+ _xml_escape(df["<publisher_place>"][j]) +'</publisher_place>\n'\
          '</publisher>\n'\
          '<standards_body>\n'\
          '<standards_body_name>'+ _xml_escape(df["<standards_body_name>"][j]) +'</standards_body_name>\n'\
          '<standards_body_acronym>'+ _xml_escape(df["<standards_body_acronym>"][j]) +'</standards_body_acronym>\n'\
          '</standards_body>\n'\
          '<doi_data>\n'\
          '<doi>' + _xml_escape(doi_value) + '</doi>\n'\
          '<resource>'+ _xml_escape(df["<resource>"][j]) +'</resource>\n'\
          '</doi_data>\n'\
          '</standard_metadata>\n'\
          '</standard>\n'

    return xml, standard


def CSVtoXML(inputfile, outputfile=None):
    return _run_csv_to_xml(inputfile, outputfile, "4.3.6", "", "standard", addStandard)


def convert_csv_text_to_xml(csv_text):
    """Convert a standards CSV string to XML.

    Returns the (xml, batch, standards) tuple from CSVtoXML, or 0 on failure.
    """
    return CSVtoXML(io.StringIO(csv_text))


def csv_text_to_standards(csv_text):
    result = convert_csv_text_to_xml(csv_text)
    if result == 0:
        return []
    _, _, standards = result
    return standards


POSTED_CONTENT_SCHEMA_VERSION = "5.4.0"
POSTED_CONTENT_EXTRA_XMLNS = (
    ' xmlns:jats="http://www.ncbi.nlm.nih.gov/JATS1"'
    ' xmlns:fr="http://www.crossref.org/fundref.xsd"'
    ' xmlns:mml="http://www.w3.org/1998/Math/MathML"'
)


def addPostedContent(df, j):
    if str(df["<posted_month>"][j]) == "nan" or str(df["<posted_day>"][j]) == "nan"\
            or str(df["<posted_year>"][j]) == "nan" or str(df["<resource>"][j]) == "nan":
        return "", None

    doi_value = _resolve_doi_value(df, j)
    posted_date = datetime(int(df["<posted_year>"][j]), int(df["<posted_month>"][j]), int(df["<posted_day>"][j]))

    acceptance_date = None
    if str(df["<acceptance_year>"][j]) not in ("nan", ""):
        acceptance_date = datetime(int(df["<acceptance_year>"][j]), int(df["<acceptance_month>"][j]), int(df["<acceptance_day>"][j]))

    posted_content = CreateRecords.create_posted_content(df, j, doi_value, posted_date, acceptance_date)

    group_title = read_optional_cell(df, j, "<group_title>")
    group_title_xml = ('<group_title>' + _xml_escape(group_title) + '</group_title>\n') if group_title else ""

    original_language_title = read_optional_cell(df, j, "<original_language_title>")
    original_language_title_lang = read_optional_cell(df, j, "<original_language_title_lang>")
    original_title_xml = (
        '<original_language_title language="' + _xml_escape(original_language_title_lang) + '">'
        + _xml_escape(original_language_title) + '</original_language_title>\n'
    ) if original_language_title else ""

    acceptance_date_xml = _date_block_xml("acceptance_date", acceptance_date) if acceptance_date is not None else ""

    posted_content_type = read_optional_cell(df, j, "<posted_content_type>") or "preprint"
    contributors = read_json_cell(df, j, "<contributors>", [])
    institution = read_json_cell(df, j, "<institution>", {})
    citations = read_json_cell(df, j, "<citations>", [])

    xml = '<posted_content type="' + _xml_escape(posted_content_type) + '">\n'\
          + group_title_xml +\
          '<contributors>\n'\
          + _contributors_xml(contributors, first_sequence="first", affiliation_xml_builder=lambda c: _affiliations_xml(c.get("affiliations", []))) +\
          '</contributors>\n'\
          '<titles>\n'\
          '<title>' + _xml_escape(df["<title>"][j]) + '</title>\n'\
          + original_title_xml +\
          '</titles>\n'\
          + _date_block_xml("posted_date", posted_date)\
          + acceptance_date_xml\
          + _institution_block_xml(institution) +\
          '<doi_data>\n'\
          '<doi>' + _xml_escape(doi_value) + '</doi>\n'\
          '<resource>' + _xml_escape(df["<resource>"][j]) + '</resource>\n'\
          '</doi_data>\n'\
          + _citation_list_xml(citations) +\
          '</posted_content>\n'

    return xml, posted_content


def PostedContentCSVtoXML(inputfile, outputfile=None):
    return _run_csv_to_xml(inputfile, outputfile, POSTED_CONTENT_SCHEMA_VERSION, POSTED_CONTENT_EXTRA_XMLNS, "posted_content", addPostedContent)


def convert_posted_content_csv_text_to_xml(csv_text):
    """Convert a posted content CSV string to XML.

    Returns the (xml, batch, posted_content) tuple from PostedContentCSVtoXML, or 0 on failure.
    """
    return PostedContentCSVtoXML(io.StringIO(csv_text))


def csv_text_to_posted_content(csv_text):
    result = convert_posted_content_csv_text_to_xml(csv_text)
    if result == 0:
        return []
    _, _, posted_content_rows = result
    return posted_content_rows
