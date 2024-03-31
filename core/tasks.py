from core.usefuls.processing_file import FileXlsxPreparer, FileXlsxProcessor
from core.models import SourceFile, GenericItem

from celery import shared_task
from celery.utils.log import get_task_logger

from PyPDF2 import PdfReader
import pandas as pd

from io import BytesIO
import boto3
from scraper.settings import AWS_STORAGE_BUCKET_NAME


logger = get_task_logger(__name__)


def get_list_of_inputs_of_composition( pdf_content, page_selected: int ) -> list:
    return pdf_content.pages[page_selected].extract_text().split('\n')

def extract_text_from_xlsx_file( response, type_file, source_file ) -> None:
    preparer = FileXlsxPreparer()
    data_frame = preparer.get_data_frame_prepared( response=response, type_file=type_file, source_file=source_file )
    processor = FileXlsxProcessor( data_frame=data_frame, type_file=type_file, source_file=source_file )

def save_status_file( selected_object: SourceFile ) -> bool:
    try:
        selected_object.status=True
        selected_object.save()
        return True
    except:
        return False

@shared_task
def process_file_in_background( id: int ) -> bool:

    selected_object = SourceFile.objects.get(id=id)
    key_file = str(selected_object.source_file)

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=key_file)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        print(f"Successful S3 get_object response. Status - {status}")
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")
    extract_text_from_xlsx_file( response=response, type_file=selected_object.type_file, source_file=selected_object )

    status_file = save_status_file( selected_object= selected_object )

    return status_file