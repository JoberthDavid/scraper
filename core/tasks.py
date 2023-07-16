from core.usefuls.processing_file import FileProcessor
from core.models import ModelFileCost

from celery import shared_task
from celery.utils.log import get_task_logger

from PyPDF2 import PdfReader

from io import BytesIO
import boto3
from scraper.settings import AWS_STORAGE_BUCKET_NAME


logger = get_task_logger(__name__)


def get_list_of_inputs_of_composition( pdf_content, page_selected: int ) -> list:
    return pdf_content.pages[page_selected].extract_text().split('\n')

def extract_text_from_pdf_file( selected_object: ModelFileCost, page_dict: dict, num_pages: int ) -> None:
    FileProcessor( selected_object=selected_object, page_dict=page_dict, num_pages=num_pages )

def save_status_file( selected_object: ModelFileCost ) -> bool:
    try:
        selected_object.status=True
        selected_object.save()
        return True
    except:
        return False

@shared_task
def process_file_in_background( id: int ) -> bool:

    selected_object = ModelFileCost.objects.get(id=id)
    key_file = str(selected_object.file)

    #streaming from AWS
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=key_file)
    pdf_content = PdfReader(BytesIO(obj['Body'].read()))

    num_pages = len(pdf_content.pages)
    page_dict = {}

    for page_selected in range(num_pages):
        page_dict[page_selected] = get_list_of_inputs_of_composition( pdf_content, page_selected )

    extract_text_from_pdf_file( selected_object=selected_object, page_dict=page_dict, num_pages=num_pages )

    status_file = save_status_file( selected_object= selected_object )

    return status_file