import hashlib
import re
from datetime import datetime
from typing import Any

from edupulse.domain.enums import ComponentType, DailyAttendanceStatus
from edupulse.domain.models import AttendanceRecord, DailyAttendance


class PasteImportProvider:
    """Parses attendance and timetable tables directly pasted by students from their browser view."""

    @classmethod
    def parse_attendance_paste(
        cls, pasted_text: str, student_id: str
    ) -> dict[str, Any]:
        """Parses lines like:
        'CEUE203 / OOP | LECT | 14 / 15 | 93.3%'
        or tab/pipe delimited:
        'CSUC201 \t FDSA \t LAB \t 7 \t 11 \t 63%'
        """
        checksum = hashlib.sha256(pasted_text.encode("utf-8")).hexdigest()[:12]
        records: list[AttendanceRecord] = []
        errors: list[str] = []
        lines = [line.strip() for line in pasted_text.strip().splitlines() if line.strip()]

        for idx, line in enumerate(lines, start=1):
            if any(header in line.lower() for header in ["course", "subject", "component", "present", "total"]):
                continue  # skip header lines

            # Normalize delimiters: replace tabs and pipes with spaces or split
            parts = [p.strip() for p in re.split(r"[\t|;,]+", line) if p.strip()]

            # Format A: CourseCode/ShortName, Component, Present/Total (or separate Present, Total), [Percentage]
            if len(parts) >= 3:
                course_token = parts[0]
                comp_token = parts[1].upper()
                counts_token = parts[2]

                # Extract course code (e.g. CEUE203 from CEUE203 / OOP or CEUE203)
                c_code_match = re.search(r"[A-Z]{3,5}\d{3,4}", course_token)
                c_code = c_code_match.group(0) if c_code_match else course_token.split()[0]

                # Component validation
                comp = None
                if "LECT" in comp_token or "THEORY" in comp_token:
                    comp = ComponentType.LECT
                elif "LAB" in comp_token or "PRAC" in comp_token:
                    comp = ComponentType.LAB
                elif "OTHER" in comp_token:
                    comp = ComponentType.OTHER
                else:
                    errors.append(f"Line {idx} ('{course_token}'): Unknown component '{comp_token}'")
                    continue

                # Parse present and total counts
                pres = None
                tot = None

                # Check if counts_token is like "14 / 15" or "14/15"
                slash_match = re.search(r"(\d+)\s*/\s*(\d+)", counts_token)
                if slash_match:
                    pres = int(slash_match.group(1))
                    tot = int(slash_match.group(2))
                elif len(parts) >= 4 and parts[2].isdigit() and parts[3].isdigit():
                    pres = int(parts[2])
                    tot = int(parts[3])
                else:
                    errors.append(f"Line {idx} ('{course_token}'): Could not parse present/total counts from '{counts_token}'")
                    continue

                if pres < 0 or tot < 0:
                    errors.append(f"Line {idx} ('{course_token}'): Negative counts detected ({pres}/{tot})")
                    continue
                if pres > tot:
                    errors.append(f"Line {idx} ('{course_token}'): Present count ({pres}) exceeds total ({tot})")
                    continue

                pct = round((pres / tot) * 100.0, 1) if tot > 0 else None
                records.append(
                    AttendanceRecord(
                        studentId=student_id,
                        courseId=c_code,
                        component=comp,
                        presentCount=pres,
                        totalCount=tot,
                        portalReportedPercentage=pct,
                        asOfDate=datetime.now().strftime("%Y-%m-%d"),
                        source="paste_import",
                        importBatchId=f"paste_{checksum}",
                    )
                )
            else:
                errors.append(f"Line {idx}: Unrecognized line structure: '{line}'")

        return {
            "valid": len(errors) == 0 and len(records) > 0,
            "records": records,
            "errors": errors,
            "checksum": checksum,
            "rowCount": len(records),
        }

    @classmethod
    def parse_daily_timetable_paste(
        cls, pasted_text: str, student_id: str, default_date: str | None = None
    ) -> dict[str, Any]:
        """Parses daily timetable paste lines such as:
        '09:10-10:10 | CEUE203 / OOP | P'
        or:
        '10:15-11:15 \t MSUD203 \t -'
        Note: '-' is mapped to UNMARKED (NOT absent).
        """
        checksum = hashlib.sha256(pasted_text.encode("utf-8")).hexdigest()[:12]
        records: list[DailyAttendance] = []
        errors: list[str] = []
        dt = default_date or datetime.now().strftime("%Y-%m-%d")
        lines = [line.strip() for line in pasted_text.strip().splitlines() if line.strip()]

        for idx, line in enumerate(lines, start=1):
            if any(header in line.lower() for header in ["time", "slot", "status", "subject", "attendance"]):
                continue

            parts = [p.strip() for p in re.split(r"[\t|;,]+", line) if p.strip()]
            if len(parts) >= 2:
                # Slot might be first or second
                time_slot = None
                course_token = None
                status_raw = parts[-1].strip().upper()

                if re.search(r"\d{1,2}[:.]\d{2}", parts[0]):
                    time_slot = parts[0]
                    course_token = parts[1]
                else:
                    course_token = parts[0]
                    if len(parts) >= 3:
                        time_slot = parts[1]

                c_code_match = re.search(r"[A-Z]{3,5}\d{3,4}", course_token)
                c_code = c_code_match.group(0) if c_code_match else course_token.split()[0]

                # Map status: '-' or 'UNMARKED' -> UNMARKED
                if status_raw in ("P", "PRESENT"):
                    status = DailyAttendanceStatus.P
                elif status_raw in ("A", "ABSENT"):
                    status = DailyAttendanceStatus.A
                elif status_raw in ("NT", "NOT TAUGHT"):
                    status = DailyAttendanceStatus.NT
                elif status_raw in ("-", "UNMARKED", ""):
                    status = DailyAttendanceStatus.UNMARKED
                else:
                    errors.append(f"Line {idx} ('{course_token}'): Unknown status '{status_raw}'")
                    continue

                records.append(
                    DailyAttendance(
                        studentId=student_id,
                        courseId=c_code,
                        date=dt,
                        timeSlot=time_slot,
                        status=status,
                        source="paste_import",
                    )
                )
            else:
                errors.append(f"Line {idx}: Unrecognized timetable line format: '{line}'")

        return {
            "valid": len(errors) == 0 and len(records) > 0,
            "records": records,
            "errors": errors,
            "checksum": checksum,
            "rowCount": len(records),
        }
