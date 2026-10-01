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
        Handles UTF-8 BOM, whitespace, duplicate rows, and missing values.
        Returns preview dict with valid, records, errors, checksum, rowCount, and importType.
        """
        clean_content = file_content.lstrip("\ufeff").strip()
        checksum = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()[:12] if clean_content else ""
        records: list[AttendanceRecord] = []
        errors: list[str] = []

        if not clean_content:
            return {
                "valid": False,
                "records": [],
                "errors": ["Uploaded CSV file is empty. Please select or paste a non-empty CSV file."],
                "checksum": "",
                "rowCount": 0,
                "importType": "attendance",
            }

        try:
            reader = csv.DictReader(io.StringIO(clean_content))
            if not reader.fieldnames:
                return {
                    "valid": False,
                    "records": [],
                    "errors": ["CSV file contains no headers or columns."],
                    "checksum": checksum,
                    "rowCount": 0,
                    "importType": "attendance",
                }

            # Normalize header names (lowercase, stripped)
            fieldnames_map = {col.strip().lower(): col for col in reader.fieldnames if col}
            required_cols = {"course_code", "component", "present_count", "total_count"}
            missing_cols = required_cols - set(fieldnames_map.keys())

            if missing_cols:
                errors.append(f"CSV header missing required columns: {', '.join(sorted(missing_cols))}")
                return {
                    "valid": False,
                    "records": [],
                    "errors": errors,
                    "checksum": checksum,
                    "rowCount": 0,
                    "importType": "attendance",
                }

            seen_components: set[tuple[str, str]] = set()

            for row_idx, row in enumerate(reader, start=2):
                # Map case-insensitive keys
                c_code = (row.get(fieldnames_map["course_code"]) or "").strip()
                comp_raw = (row.get(fieldnames_map["component"]) or "").strip().upper()
                as_of_key = fieldnames_map.get("as_of_date")
                as_of = (row.get(as_of_key) or "").strip() if as_of_key else datetime.now().strftime("%Y-%m-%d")
                if not as_of:
                    as_of = datetime.now().strftime("%Y-%m-%d")

                if not c_code:
                    errors.append(f"Row {row_idx}: Missing course_code.")
                    continue

                if comp_raw not in ("LECT", "LAB", "OTHER"):
                    errors.append(f"Row {row_idx} ({c_code}): Invalid component '{comp_raw}'. Must be LECT, LAB, or OTHER.")
                    continue

                # Check duplicate rows
                comp_key = (c_code, comp_raw)
                if comp_key in seen_components:
                    errors.append(f"Row {row_idx} ({c_code}): Duplicate row detected for component '{comp_raw}'. Each course component must only be listed once.")
                    continue
                seen_components.add(comp_key)

                pres_str = str(row.get(fieldnames_map["present_count"]) or "").strip()
                tot_str = str(row.get(fieldnames_map["total_count"]) or "").strip()

                if pres_str == "" or tot_str == "":
                    errors.append(f"Row {row_idx} ({c_code}): Missing values for present_count or total_count.")
                    continue

                try:
                    present_count = int(pres_str)
                    total_count = int(tot_str)
                except (ValueError, TypeError):
                    errors.append(f"Row {row_idx} ({c_code}): Counts must be integers, got present='{pres_str}', total='{tot_str}'.")
                    continue

                if present_count < 0 or total_count < 0:
                    errors.append(f"Row {row_idx} ({c_code}): Counts cannot be negative ({present_count}/{total_count}).")
                    continue

                if present_count > total_count:
                    errors.append(f"Row {row_idx} ({c_code}): present_count ({present_count}) exceeds total_count ({total_count}).")
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
            "valid": len(errors) == 0 and len(records) > 0,
            "records": records,
            "errors": errors,
            "checksum": checksum,
            "rowCount": len(records),
            "importType": "attendance",
        }

    @classmethod
    def preview_marks_csv(
        cls, file_content: str, student_id: str
    ) -> dict[str, Any]:
        """Parses and validates marks/academics CSV.
        Handles UTF-8 BOM, whitespace, duplicate rows, and missing values.
        Returns preview dict with valid, records, errors, checksum, rowCount, and importType.
        """
        clean_content = file_content.lstrip("\ufeff").strip()
        checksum = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()[:12] if clean_content else ""
        assessments: list[Assessment] = []
        errors: list[str] = []

        if not clean_content:
            return {
                "valid": False,
                "records": [],
                "errors": ["Uploaded CSV file is empty. Please select or paste a non-empty CSV file."],
                "checksum": "",
                "rowCount": 0,
                "importType": "marks",
            }

        try:
            reader = csv.DictReader(io.StringIO(clean_content))
            if not reader.fieldnames:
                return {
                    "valid": False,
                    "records": [],
                    "errors": ["CSV file contains no headers or columns."],
                    "checksum": checksum,
                    "rowCount": 0,
                    "importType": "marks",
                }

            # Normalize header names (lowercase, stripped)
            fieldnames_map = {col.strip().lower(): col for col in reader.fieldnames if col}
            required_cols = {"course_code", "assessment_type", "obtained_marks", "total_marks"}
            missing_cols = required_cols - set(fieldnames_map.keys())

            if missing_cols:
                errors.append(f"CSV header missing required columns: {', '.join(sorted(missing_cols))}")
                return {
                    "valid": False,
                    "records": [],
                    "errors": errors,
                    "checksum": checksum,
                    "rowCount": 0,
                    "importType": "marks",
                }

            seen_assessments: set[tuple[str, str, str]] = set()

            for row_idx, row in enumerate(reader, start=2):
                c_code = (row.get(fieldnames_map["course_code"]) or "").strip()
                ass_type = (row.get(fieldnames_map["assessment_type"]) or "").strip()
                term_key = fieldnames_map.get("term")
                term = (row.get(term_key) or "").strip() if term_key else "T1"
                date_key = fieldnames_map.get("date")
                dt = (row.get(date_key) or "").strip() if date_key else datetime.now().strftime("%Y-%m-%d")
                if not dt:
                    dt = datetime.now().strftime("%Y-%m-%d")

                if not c_code:
                    errors.append(f"Row {row_idx}: Missing course_code.")
                    continue

                if not ass_type:
                    errors.append(f"Row {row_idx} ({c_code}): Missing assessment_type.")
                    continue

                # Check duplicate assessment rows
                ass_key = (c_code, ass_type.lower(), term.lower())
                if ass_key in seen_assessments:
                    errors.append(f"Row {row_idx} ({c_code}): Duplicate assessment row detected for '{ass_type}' in term '{term}'.")
                    continue
                seen_assessments.add(ass_key)

                obt_str = str(row.get(fieldnames_map["obtained_marks"]) or "").strip()
                tot_str = str(row.get(fieldnames_map["total_marks"]) or "").strip()

                if obt_str == "" or tot_str == "":
                    errors.append(f"Row {row_idx} ({c_code}): Missing values for obtained_marks or total_marks.")
                    continue

                try:
                    obtained = float(obt_str)
                    total = float(tot_str)
                except (ValueError, TypeError):
                    errors.append(f"Row {row_idx} ({c_code}): Marks must be numeric numbers, got obtained='{obt_str}', total='{tot_str}'.")
                    continue

                if total <= 0:
                    errors.append(f"Row {row_idx} ({c_code}): total_marks must be strictly greater than 0, got {total}.")
                    continue

                if obtained < 0:
                    errors.append(f"Row {row_idx} ({c_code}): obtained_marks cannot be negative, got {obtained}.")
                    continue

                if obtained > total:
                    errors.append(f"Row {row_idx} ({c_code}): obtained_marks ({obtained}) exceeds total_marks ({total}).")
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
            "valid": len(errors) == 0 and len(assessments) > 0,
            "records": assessments,
            "errors": errors,
            "checksum": checksum,
            "rowCount": len(assessments),
            "importType": "marks",
        }
