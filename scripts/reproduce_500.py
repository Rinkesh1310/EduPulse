import sys
sys.path.insert(0, ".")
from backend.main import preview_file, FileImportRequest
import traceback

csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,14,15
CEUE203,LAB,8,9
CSUC201,LECT,28,36
CSUC201,LAB,7,11
HSUV201,LECT,8,14"""

req = FileImportRequest(
    content=csv_content,
    student_name='Rinkesh',
    program='B.Tech IT'
)

try:
    res = preview_file(req)
    print('SUCCESS:', res)
except Exception as e:
    print('EXACT EXCEPTION TYPE:', type(e).__name__)
    print('EXACT EXCEPTION STR:', str(e))
    traceback.print_exc()
