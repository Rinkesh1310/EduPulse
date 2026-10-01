# Scholarship Verification Guide & JSON Schema

This guide provides instructions for verifying scholarship schemes (specifically **Mukhyamantri Yuva Swavalamban Yojana (MYSY)**) and updating the schema definitions in `edupulse/config/scholarship/`.

---

## 1. Why Human Verification is Required
Secondary educational sites report renewal rules consistently, but **fresh applicant entrance rules conflict**:
- Some sources specify **80th percentile** in 12th Science / Board examinations.
- Other portals report **80% aggregate marks**.
- Some recent notifications indicate revised income limits or specific professional degree quotas.

To guarantee that students receive accurate guidance, EduPulse flags unverified or conflicting schemes with `SECONDARY_ONLY` or `CONFLICTING` badges, withholds fresh-track verdicts, and provides transparent tri-state statuses (`MET`, `NOT_MET`, `UNKNOWN`).

---

## 2. Verification Steps for MYSY

1. **Access the Official Portal**:
   - Official Gujarat Government Portal: [https://mysy.guj.nic.in](https://mysy.guj.nic.in)
2. **Review Renewal Track Criteria**:
   - Confirm minimum attendance requirement (typically 75% certified by Head of Institute).
   - Confirm minimum qualifying marks in preceding year (typically 50% on first attempt).
   - Confirm income ceiling (typically ₹6,00,000 per annum).
3. **Review Fresh Applicant Track Criteria**:
   - Verify whether eligibility requires 80th percentile or 80% aggregate board marks.
   - Note down the exact notification number and publication date.
4. **Update the JSON Configuration**:
   - Open `edupulse/config/scholarship/mysy_2026_27.json`.
   - Set `"verificationLevel": "OFFICIAL_VERIFIED"`.
   - Populate `"officialSourceUrl"` with the live URL (e.g. `https://mysy.guj.nic.in/Notice_2026.pdf`).
   - Populate `"officialSourceTitle"` with the official document title.
   - Populate `"lastVerifiedAt"` with today's ISO date (e.g. `2026-10-01`).
   - Replace the `"conflicting_track"` criterion with the confirmed rule.

---

## 3. Scholarship Scheme JSON Schema

Any scholarship scheme can be added or updated without modifying Python code by placing a JSON file into `edupulse/config/scholarship/<scheme_id>.json`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ScholarshipScheme",
  "type": "object",
  "required": ["schemeId", "name", "academicYear", "version", "verificationLevel", "criteria"],
  "properties": {
    "schemeId": { "type": "string" },
    "name": { "type": "string" },
    "academicYear": { "type": "string", "example": "2026-27" },
    "version": { "type": "string", "example": "1.0" },
    "verificationLevel": {
      "type": "string",
      "enum": ["OFFICIAL_VERIFIED", "SECONDARY_ONLY", "CONFLICTING", "UNVERIFIED"]
    },
    "officialSourceUrl": { "type": ["string", "null"] },
    "officialSourceTitle": { "type": ["string", "null"] },
    "lastVerifiedAt": { "type": ["string", "null"], "format": "date" },
    "notes": { "type": ["string", "null"] },
    "criteria": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "track", "type", "operator", "value", "unit", "verification", "notes"],
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "track": { "type": "string", "enum": ["fresh", "renewal", "all"] },
          "type": {
            "type": "string",
            "enum": [
              "attendance_certified",
              "previous_year_marks",
              "annual_family_income",
              "domicile_state",
              "prior_recipient",
              "sgpa",
              "conflicting_track"
            ]
          },
          "operator": { "type": "string", "enum": [">=", "<=", "==", "!="] },
          "value": {},
          "unit": { "type": "string" },
          "requiredDataFields": { "type": "array", "items": { "type": "string" } },
          "verification": { "type": "string" },
          "notes": { "type": "string" }
        }
      }
    }
  }
}
```
