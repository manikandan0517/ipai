import json
from config import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,AWS_S3_REGION_NAME
from db_manager import DBManager, PDFStatus
from s3_manager import S3Manager
from deficiency_report import DeficiencyReportGenerator

def lambda_handler(event, context):
        
    db_manager = DBManager()
    s3_manager = S3Manager(AWS_STORAGE_BUCKET_NAME,AWS_SECRET_ACCESS_KEY,AWS_ACCESS_KEY_ID,AWS_S3_REGION_NAME)
    report_generator = DeficiencyReportGenerator()

    pdfs_to_process = db_manager.fetch_not_processed_pdfs()

    if not pdfs_to_process:
        return {"statusCode": 200, "body": json.dumps({"message": "No PDFs to process."})}

    results = []
    for pdf in pdfs_to_process:
        pdf_id, pdf_url = str(pdf["id"]), str(pdf["url"])
        db_manager.update_pdf_status(pdf_id,PDFStatus.PROCESSING)

        try:
            local_pdf_path = s3_manager.download_file(pdf_url)

            report = report_generator.generate_report(local_pdf_path, pdf_id)
            
            report_json = json.dumps(report, indent=4)

            report_filename = f"{pdf_id}/{pdf_id}_report.json"
            
            s3_manager.upload_file(report_json, report_filename)
            
            db_manager.update_deficiency_response(pdf_id, report_filename, PDFStatus.PROCESS_SUCCESS)
            
            results.append({"id": pdf_id, "status": "Success", "report_s3_path": report_filename})
            
        except Exception as e:
            
            db_manager.update_deficiency_response(pdf_id, None, PDFStatus.PROCESS_FAILED)

            results.append({"id": pdf_id, "status": "Failed", "error": str(e)})

    return {"statusCode": 200, "body": json.dumps({"processed": results})}

