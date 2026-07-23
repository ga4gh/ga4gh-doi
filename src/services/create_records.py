from datetime import datetime

from src.models.batch import Batch
from src.models.doi import Doi, Standard, Article, Conference, Grant, PostedContent, ReportWorkingPaper


class CreateRecords:
    def __init__(self) -> None:
        self.string = ""

    def create_batch(df, timestamp):
        return Batch(
            doi_batch_id=timestamp,
            deposited_by=str(df["<depositor_name>"][1]),
            depositor_email=str(df["<email_address>"][1]),
            doi_type='standard',
            xml=None,
            approved=False,
            submitted=False,
            submitted_at=None,
            successful=False,
            created_by="",
            created_at=datetime.now(),
            updated_by="",
            updated_at=datetime.now(),
        )

    def create_doi():
        return Doi(
            doi="",
            doi_batch_id="",
            approver="",
            approver_email="",
            person_responsible="",
            person_responsible_email="",
            doi_type=None,
            status=None,
            successful=False,
            created_by="",
            created_at=datetime.now(),
            updated_by="",
            updated_at=datetime.now(),
        )

    def create_standard(df, j, doi_value, publish_date):
        return Standard(
            doi=doi_value,
            resource_url=str(df["<resource>"][j]),
            publish_date=publish_date,
            item_number=None,
            publisher_place=str(df["<publisher_place>"][j]),
            std_designator=str(df["<std_designator>"][j]),
            standards_body_acronym=str(df["<standards_body_acronym>"][j]),
            depositor_name=str(df["<depositor_name>"][1]),
            registrant=str(df["<registrant>"][1]),
            publisher_name=str(df["<publisher_name>"][j]),
            standards_body_name=str(df["<standards_body_name>"][j]),
            organization=str(df["<organization>"][j]),
            title=str(df["<title>"][j]),
            resource_link=str(df["<resource>"][j]),
            email_address=str(df["<email_address>"][1]),
            batch_id=None,
        )

    def create_article():
        return Article(
            doi="",
            full_title="",
            abbrev_title="",
            issn="",
            coden="",
            publication_date=datetime.now(),
            journal_volume=0,
            journal_issue=0,
            article_title="",
            contributors=[],
            pages=0,
            resource="",
            batch_id=None,
        )

    def create_conference():
        return Conference(
            doi="",
            resource_url="",
            given_name="",
            surname="",
            conference_name="",
            conference_theme="",
            conference_acronym="",
            conference_sponsor="",
            conference_number=0,
            conference_location="",
            conference_start_date=datetime.now(),
            conference_end_date=datetime.now(),
            proceedings_title="",
            proceedings_subject="",
            publisher_name="",
            publisher_place="",
            publication_year=0,
            isbn="",
            timestamp=datetime.now(),
            resource="",
            batch_id=None,
        )

    def create_grant():
        return Grant(
            doi="",
            project_title="",
            recipients=[],
            description="",
            statement="",
            identifier="",
            award_amount=None,
            award_number=None,
            funding_amount=None,
            funder_name="",
            funder_id="",
            funding_scheme="",
            start_date=datetime.now(),
            end_date=datetime.now(),
            resource="",
            batch_id=None,
        )

    def create_posted_content():
        return PostedContent(
            doi="",
            group_title="",
            contributors=[],
            title="",
            posted_date=datetime.now(),
            acceptance_date=datetime.now(),
            institution="",
            funders=[],
            program="",
            resource="",
            citations=[],
            batch_id=None,
        )

    def create_report():
        return ReportWorkingPaper(
            doi="",
            contributors=[],
            title="",
            edition_number="",
            publication_date=datetime.now(),
            publisher_name="",
            publisher_place="",
            institution=[],
            report_number="",
            contract_number="",
            resource="",
            batch_id=None,
        )
