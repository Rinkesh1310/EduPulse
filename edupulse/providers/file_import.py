import csv
import hashlib
import io
import uuid
from datetime import datetime
from typing import Any

from edupulse.domain.enums import ComponentType
from edupulse.domain.models import (
    Assessment,
    AttendanceRecord,
)


class FileImportProvider:
    """Handles structured CSV/JSON file imports with strict validation and preview->commit workflow."""

    @staticmethod
    def generate_attendance_csv_template() -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["course_code", "course_short_name", "component", "present_count", "total_count", "as_of_date"])
        writer.writerow(["CEUE203", "OOP", "LECT", 14, 15, "2026-09-30"])
        writer.writerow(["CEUE203", "OOP", "LAB", 8, 9, "2026-09-30"])
        writer.writerow(["CSUC201", "FDSA", "LECT", 28, 36, "2026-09-30"])
        writer.writerow(["CSUC201", "FDSA", "LAB", 7, 11, "2026-09-30"])
        writer.writerow(["HSUV201", "CPI", "LECT", 8, 14, "2026-09-30"])
        return output.getvalue()

    @staticmethod
    def generate_marks_csv_template() -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["course_code", "assessment_type", "term", "date", "obtained_marks", "total_marks"])
        writer.writerow(["CEUE203", "Midterm", "T1", "2026-09-15", 15.0, 20.0])
        writer.writerow(["CSUC201", "Midterm", "T1", "2026-09-16", 12.0, 20.0])
        writer.writerow(["HSUV201", "Midterm", "T1", "2026-09-17", 9.0, 20.0])
        return output.getvalue()

    @staticmethod
    def generate_daily_csv_template() -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["course_code", "date", "time_slot", "component", "status"])
        writer.writerow(["CEUE203", "2026-09-29", "09:10-10:10", "LECT", "P"])
        writer.writerow(["CSUC201", "2026-09-29", "10:15-11:15", "LECT", "P"])
        writer.writerow(["ITUC201", "2026-09-30", "09:10-10:10", "LECT", "P"])
        writer.writerow(["MSUD203", "2026-09-30", "10:15-11:15", "LECT", "-"])
        return output.getvalue()

    @classmethod
    def preview_attendance_csv(
        cls, file_content: str, student_id: str
    ) -> dict[str, Any]:
        """Parses and validates attendance summary CSV.
        Returns preview dict with valid_records, errors, and checksum.
        """
        checksum = hashlib.sha256(file_content.encode("utf-8")).hexdigest()[:12]
        records: list[AttendanceRecord] = []
        errors: list[str] = []

        try:
            reader = csv.DictReader(io.StringIO(file_content))
            required_cols = {"course_code", "component", "present_count", "total_count"}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                errors.append(f"CSV header missing required columns: {required_cols - set(reader.fieldnames or [])}")
                return {"valid": False, "records": [], "errors": errors, "checksum": checksum}

            for row_idx, row in enumerate(reader, start=2):
                c_code = (row.get("course_code") or "").strip()
                comp_raw = (row.get("component") or "").strip().upper()
                as_of = (row.get("as_of_date") or "").strip() or datetime.now().strftime("%Y-%m-%d")

                if not c_code:
                    errors.append(f"Row {row_idx}: Missing course_code")
                    continue

                if comp_raw not in ("LECT", "LAB", "OTHER"):
                    errors.append(f"Row {row_idx} ({c_code}): Invalid component '{comp_raw}'. Must be LECT, LAB, or OTHER.")
                    continue

                try:
                    present_count = int(row.get("present_count", 0))
                    total_count = int(row.get("total_count", 0))
                except ValueError:
                    errors.append(f"Row {row_idx} ({c_code}): present_count and total_count must be integers")
                    continue

                if present_count < 0 or total_count < 0:
                    errors.append(f"Row {row_idx} ({c_code}): Counts cannot be negative ({present_count}/{total_count})")
                    continue

                if present_count > total_count:
                    errors.append(f"Row {row_idx} ({c_code}): present_count ({present_count}) exceeds total_count ({total_count})")
                    continue

                records.append(
                    AttendanceRecord(
                        studentId=student_id,
                        courseId=c_code,
                        component=ComponentType(comp_raw),
                        presentCount=present_count,
                        totalCount=total_count,
                        portalReportedPercentage=round((present_count / total_count) * 100.0, 1) if total_count > 0 else None,
                        asOfDate=as_of,
                        source="file_import_csv",
                        importBatchId=f"batch_{checksum}",
                    )
                )

        except Exception as e:
            errors.append(f"Failed to parse CSV: {e!s}")

        return {
            "valid": len(errors) == 0,
            "records": records,
            "errors": errors,
            "checksum": checksum,
            "rowCount": len(records),
        }

    @classmethod
    def preview_marks_csv(
        cls, file_content: str, student_id: str
    ) -> dict[str, Any]:
        """Parses and validates marks CSV."""
        checksum = hashlib.sha256(file_content.encode("utf-8")).hexdigest()[:12]
        assessments: list[Assessment] = []
        errors: list[str] = []

        try:
            reader = csv.DictReader(io.StringIO(file_content))
            required_cols = {"course_code", "assessment_type", "obtained_marks", "total_marks"}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                errors.append(f"CSV header missing required columns: {required_cols - set(reader.fieldnames or [])}")
                return {"valid": False, "records": [], "errors": errors, "checksum": checksum}

            for row_idx, row in enumerate(reader, start=2):
                c_code = (row.get("course_code") or "").strip()
                ass_type = (row.get("assessment_type") or "").strip()
                term = (row.get("term") or "").strip() or None
                dt = (row.get("date") or "").strip() or datetime.now().strftime("%Y-%m-%d")

                if not c_code or not ass_type:
                    errors.append(f"Row {row_idx}: course_code and assessment_type cannot be empty")
                    continue

                try:
                    obtained = float(row.get("obtained_marks", 0))
                    total = float(row.get("total_marks", 0))
                except ValueError:
                    errors.append(f"Row {row_idx} ({c_code}): Marks must be numeric numbers")
                    continue

                if total <= 0:
                    errors.append(f"Row {row_idx} ({c_code}): total_marks must be strictly greater than 0, got {total}")
                    continue

                if obtained < 0:
                    errors.append(f"Row {row_idx} ({c_code}): obtained_marks cannot be negative, got {obtained}")
                    continue

                if obtained > total:
                    errors.append(f"Row {row_idx} ({c_code}): obtained_marks ({obtained}) exceeds total_marks ({total})")
                    continue

                assessments.append(
                    Assessment(
                        id=f"imp_{c_code}_{uuid.uuid4().hex[:8]}",
                        studentId=student_id,
                        courseId=c_code,
                        type=ass_type,
                        term=term,
                        date=dt,
                        obtainedMarks=obtained,
                        totalMarks=total,
                    )
                )

        except Exception as e:
            errors.append(f"Failed to parse CSV: {e!s}")

        return {
            "valid": len(errors) == 0,
            "records": assessments,
            "errors": errors,
            "checksum": checksum,
            "rowCount": len(assessments),
        }
