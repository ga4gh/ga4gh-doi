import msql.connector
from mysql.connector import Error
import pandas as pd
import click
from csv_to_xml import CSVtoXML


@click.group()
def main():
    pass

@main.command(help='run the DOI tool for maintaining and uploading DOIs')
@click.option('--input_csv', '-csv', multiple=False, help="csv containing DOIs")
@click.option('--upload', is_flag=True, help='upload new DOIs from CSV')
@click.option('--output_xml', '-xml', multiple=False, default='suffix-designator-test-output.xml', help='XML file for DOIs to be written to')
def doi(input_csv, upload, output_xml):

    #CSVtoXML("test-csv-output.csv","suffix-designator-test-output.xml")
    CSVtoXML(input_csv, output_xml)
    if upload:
        # TODO: implement upload feature
        pass


if __name__ == "__main__":
    main()