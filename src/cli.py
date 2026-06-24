from datetime import datetime
import click
from services.csvToXml import CSVtoXML
from client.submitDoi import submitDoi
from repositories.dbFunctions import DBFunctions
from config.session import get_session


@click.group()
def main():
    pass

@main.command(help='run the DOI tool for maintaining and uploading DOIs')
@click.option('--input_csv', '-csv', multiple=False, help="csv containing DOIs")
@click.option('--upload', is_flag=True, help='upload new DOIs from CSV')
@click.option('--output_xml', '-xml', multiple=False, default='xml/suffix-designator-test-output.xml', help='XML file for DOIs to be written to')
def doi(input_csv, upload, output_xml):
    _, batch, standards = CSVtoXML(input_csv, output_xml)
    if upload:
        #submitDoi(output_xml)
        batch.submitted = True
        batch.submitted_at = datetime.now()
        with get_session() as session:
            repo = DBFunctions(session)
            repo.insert(batch)
            for standard in standards:
                repo.insert(standard)


if __name__ == "__main__":
    main()