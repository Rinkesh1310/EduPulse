import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_valid_attendance_csv():
    csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,14,15
CEUE203,LAB,8,9
CSUC201,LECT,28,36
CSUC201,LAB,7,11
HSUV201,LECT,8,14"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["rowCount"] == 5
    assert data["importType"] == "attendance"
    assert len(data["records"]) == 5

def test_valid_marks_csv():
    csv_content = """course_code,assessment_type,term,obtained_marks,total_marks
CEUE203,Midterm,T1,15.0,20.0
CSUC201,Midterm,T1,12.0,20.0
HSUV201,Quiz,T1,8.5,10.0"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["rowCount"] == 3
    assert data["importType"] == "marks"
    assert len(data["records"]) == 3

def test_utf8_bom_handling():
    csv_content = "\ufeffcourse_code,component,present_count,total_count\nCEUE203,LECT,14,15\n"
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["rowCount"] == 1

def test_whitespace_in_numeric_values():
    csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,  14  ,  15  
CSUC201,LAB,  7  ,  11  """
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["rowCount"] == 2
    assert data["records"][0]["presentCount"] == 14
    assert data["records"][0]["totalCount"] == 15

def test_unexpected_extra_columns():
    csv_content = """course_code,component,present_count,total_count,instructor,classroom,random_notes
CEUE203,LECT,14,15,Prof Smith,Room 302,Good participation
CSUC201,LAB,7,11,Prof Patel,Lab 4,On track"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["rowCount"] == 2

def test_missing_required_columns():
    csv_content = """course_code,present_count,total_count
CEUE203,14,15"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert any("component" in err.lower() for err in data["errors"])

def test_empty_csv():
    res = client.post("/api/data-workspace/preview-file", json={
        "content": "   \n\n  ",
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 400

def test_invalid_student_name():
    res = client.post("/api/data-workspace/preview-file", json={
        "content": "course_code,component,present_count,total_count\nCEUE203,LECT,14,15",
        "student_name": "   ",
        "program": "B.Tech IT"
    })
    assert res.status_code == 422

def test_invalid_degree_program():
    res = client.post("/api/data-workspace/preview-file", json={
        "content": "course_code,component,present_count,total_count\nCEUE203,LECT,14,15",
        "student_name": "Rinkesh",
        "program": "   "
    })
    assert res.status_code == 422

def test_duplicate_rows():
    csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,14,15
CEUE203,LECT,10,12"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert any("duplicate" in err.lower() for err in data["errors"])

def test_incorrect_data_types():
    csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,fourteen,fifteen"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert any("must be integers" in err.lower() for err in data["errors"])

def test_present_exceeds_total():
    csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,20,15"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert any("exceeds total_count" in err.lower() for err in data["errors"])

def test_negative_counts():
    csv_content = """course_code,component,present_count,total_count
CEUE203,LECT,-5,15"""
    res = client.post("/api/data-workspace/preview-file", json={
        "content": csv_content,
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert any("cannot be negative" in err.lower() for err in data["errors"])
