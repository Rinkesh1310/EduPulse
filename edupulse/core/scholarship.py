from typing import Any

from edupulse.core.attendance import calculate_attendance_recovery
from edupulse.domain.enums import (
    CriterionResultStatus,
    EvidenceBasis,
    VerificationLevel,
)
from edupulse.domain.models import (
    ScholarshipCriterion,
    ScholarshipScheme,
    SemesterResult,
)


class EvaluatedCriterion:
    def __init__(
        self,
        criterion: ScholarshipCriterion,
        status: CriterionResultStatus,
        basis: EvidenceBasis,
        details: str,
        target_info: dict[str, Any] | None = None,
        missing_input_label: str | None = None,
    ):
        self.criterion = criterion
        self.status = status
        self.basis = basis
        self.details = details
        self.target_info = target_info
        self.missing_input_label = missing_input_label

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.criterion.id,
            "label": self.criterion.label,
            "track": self.criterion.track,
            "status": self.status.value,
            "basis": self.basis.value,
            "details": self.details,
            "targetInfo": self.target_info,
            "missingInputLabel": self.missing_input_label,
            "verification": self.criterion.verification,
            "notes": self.criterion.notes,
        }


def evaluate_scholarship_scheme(
    scheme: ScholarshipScheme,
    selected_track: str,
    overall_attendance_pct: float | None,
    total_present: int,
    total_classes: int,
    semester_results: list[SemesterResult],
    attested_facts: dict[str, Any],
    planned_remaining_classes: int = 30,
) -> dict[str, Any]:
    """Evaluates a scholarship scheme against current student data and attested facts.
    
    Adheres strictly to Master Spec Section 7:
      - Returns tri-state: MET, NOT_MET, UNKNOWN.
      - NEVER converts SGPA to marksheet percentage.
      - Midterm attendance evaluated as UNKNOWN with 'on track' or 'needs attention' trajectory hint.
      - NOT_MET on attendance projection only when mathematically unreachable within remaining classes.
      - Expired, unverified, or conflicting schemes display a top warning banner and no summary verdict.
      - Never says 'eligible' or 'not eligible'; returns summary counts 'n met · n not met · n unknown'.
    """
    evaluated_criteria: list[EvaluatedCriterion] = []

    is_conflicting_or_unverified = (
        scheme.verificationLevel in (VerificationLevel.SECONDARY_ONLY, VerificationLevel.CONFLICTING, VerificationLevel.UNVERIFIED)
        or scheme.officialSourceUrl is None
    )

    for crit in scheme.criteria:
        # Check track applicability
        if crit.track not in ("all", selected_track):
            continue

        # Conflicting track guard
        if crit.type == "conflicting_track":
            evaluated_criteria.append(
                EvaluatedCriterion(
                    criterion=crit,
                    status=CriterionResultStatus.UNKNOWN,
                    basis=EvidenceBasis.SELF_DECLARED,
                    details="Evaluation withheld: secondary sources conflict between 80 percentile and 80% board marks. Requires confirmed rules.",
                    missing_input_label="Official entrance criteria verification",
                )
            )
            continue

        # 1. Attendance Certified Criterion
        if crit.type == "attendance_certified":
            target_val = float(crit.value)
            if overall_attendance_pct is None or total_classes == 0:
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=CriterionResultStatus.UNKNOWN,
                        basis=EvidenceBasis.OFFICIAL_IMPORT,
                        details="No attendance records available to evaluate trajectory.",
                        missing_input_label="Term attendance record",
                    )
                )
            else:
                recovery = calculate_attendance_recovery(
                    present=total_present,
                    total=total_classes,
                    target_pct=target_val,
                    remaining_classes=planned_remaining_classes,
                )

                if not recovery["isRecoverableWithinRemaining"]:
                    # Mathematically impossible to reach target within remaining classes
                    evaluated_criteria.append(
                        EvaluatedCriterion(
                            criterion=crit,
                            status=CriterionResultStatus.NOT_MET,
                            basis=EvidenceBasis.APP_ESTIMATE,
                            details=(
                                f"Mathematically unreachable: Current attendance {overall_attendance_pct:.1f}% requires "
                                f"{recovery['classesNeeded']} consecutive classes, exceeding planned remaining {planned_remaining_classes} classes."
                            ),
                            target_info=recovery,
                        )
                    )
                else:
                    # Midterm attendance is UNKNOWN because final certification occurs at term-end
                    on_track = overall_attendance_pct >= target_val
                    hint = "On track" if on_track else "Needs attention"
                    detail_msg = (
                        f"Midterm trajectory ({hint}): Current computed attendance {overall_attendance_pct:.1f}% "
                        f"(Requirement >= {target_val:.0f}% institute-certified). "
                    )
                    if on_track:
                        detail_msg += f"Safe buffer: up to {recovery['bufferClasses']} allowable misses."
                    else:
                        detail_msg += f"Requires attending next {recovery['classesNeeded']} consecutive classes."

                    evaluated_criteria.append(
                        EvaluatedCriterion(
                            criterion=crit,
                            status=CriterionResultStatus.UNKNOWN,
                            basis=EvidenceBasis.APP_ESTIMATE,
                            details=detail_msg,
                            target_info=recovery,
                            missing_input_label="End-of-term institutional attendance certificate",
                        )
                    )

        # 2. Previous Year Marksheet Marks Percent
        elif crit.type == "previous_year_marks":
            target_val = float(crit.value)
            # NEVER derive marks from SGPA! Must come from attested fact
            marks_fact = attested_facts.get("previousYearMarksPercent")
            if marks_fact is None:
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=CriterionResultStatus.UNKNOWN,
                        basis=EvidenceBasis.SELF_DECLARED,
                        details="Student-attested previous year marksheet percentage not entered. (Never derived from SGPA).",
                        missing_input_label="Previous year marksheet percentage certificate",
                    )
                )
            else:
                try:
                    val = float(marks_fact)
                    if val >= target_val:
                        status = CriterionResultStatus.MET
                        det = f"Attested marksheet percentage {val:.1f}% meets requirement (>= {target_val:.0f}%)."
                    else:
                        status = CriterionResultStatus.NOT_MET
                        det = f"Attested marksheet percentage {val:.1f}% does not meet requirement (>= {target_val:.0f}%)."
                    evaluated_criteria.append(
                        EvaluatedCriterion(
                            criterion=crit,
                            status=status,
                            basis=EvidenceBasis.SELF_DECLARED,
                            details=det,
                        )
                    )
                except ValueError:
                    evaluated_criteria.append(
                        EvaluatedCriterion(
                            criterion=crit,
                            status=CriterionResultStatus.UNKNOWN,
                            basis=EvidenceBasis.SELF_DECLARED,
                            details="Invalid marksheet percentage format.",
                            missing_input_label="Valid marksheet percentage",
                        )
                    )

        # 3. Annual Family Income
        elif crit.type == "annual_family_income":
            income_max = float(crit.value)
            income_fact = attested_facts.get("annualFamilyIncome")
            if income_fact is None:
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=CriterionResultStatus.UNKNOWN,
                        basis=EvidenceBasis.SELF_DECLARED,
                        details=f"Annual family income unverified. Must be <= ₹{income_max:,.0f}.",
                        missing_input_label="Competent authority income certificate",
                    )
                )
            else:
                try:
                    val = float(income_fact)
                    if val <= income_max:
                        status = CriterionResultStatus.MET
                        det = f"Attested annual income ₹{val:,.0f} meets requirement (<= ₹{income_max:,.0f})."
                    else:
                        status = CriterionResultStatus.NOT_MET
                        det = f"Attested annual income ₹{val:,.0f} exceeds maximum ceiling ₹{income_max:,.0f}."
                    evaluated_criteria.append(
                        EvaluatedCriterion(
                            criterion=crit,
                            status=status,
                            basis=EvidenceBasis.SELF_DECLARED,
                            details=det,
                        )
                    )
                except ValueError:
                    evaluated_criteria.append(
                        EvaluatedCriterion(
                            criterion=crit,
                            status=CriterionResultStatus.UNKNOWN,
                            basis=EvidenceBasis.SELF_DECLARED,
                            details="Invalid income entry format.",
                            missing_input_label="Valid income certificate",
                        )
                    )

        # 4. Domicile State
        elif crit.type == "domicile_state":
            domicile_fact = attested_facts.get("domicileGujarat")
            if domicile_fact is None:
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=CriterionResultStatus.UNKNOWN,
                        basis=EvidenceBasis.SELF_DECLARED,
                        details="Gujarat domicile status not attested.",
                        missing_input_label="Gujarat domicile certificate",
                    )
                )
            else:
                is_gujarat = bool(domicile_fact)
                status = CriterionResultStatus.MET if is_gujarat else CriterionResultStatus.NOT_MET
                det = "Gujarat domicile attested." if is_gujarat else "Candidate domicile outside Gujarat."
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=status,
                        basis=EvidenceBasis.SELF_DECLARED,
                        details=det,
                    )
                )

        # 5. Prior Recipient
        elif crit.type == "prior_recipient":
            rec_fact = attested_facts.get("currentlyReceivingScheme")
            if rec_fact is None:
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=CriterionResultStatus.UNKNOWN,
                        basis=EvidenceBasis.SELF_DECLARED,
                        details="Prior recipient status unverified.",
                        missing_input_label="Prior year scholarship sanction order",
                    )
                )
            else:
                is_rec = bool(rec_fact)
                status = CriterionResultStatus.MET if is_rec else CriterionResultStatus.NOT_MET
                det = "Prior scholarship recipient confirmed for renewal track." if is_rec else "Not recorded as prior recipient."
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=status,
                        basis=EvidenceBasis.SELF_DECLARED,
                        details=det,
                    )
                )

        # 6. SGPA Academic Requirement (e.g. in Demo Merit Scheme)
        elif crit.type == "sgpa":
            target_sgpa = float(crit.value)
            if not semester_results:
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=CriterionResultStatus.UNKNOWN,
                        basis=EvidenceBasis.OFFICIAL_IMPORT,
                        details="No published semester grade results available.",
                        missing_input_label="Published semester grade card",
                    )
                )
            else:
                latest_sgpa = semester_results[-1].sgpa
                if latest_sgpa >= target_sgpa:
                    status = CriterionResultStatus.MET
                    det = f"Latest SGPA {latest_sgpa:.2f} meets requirement (>= {target_sgpa:.2f})."
                else:
                    status = CriterionResultStatus.NOT_MET
                    det = f"Latest SGPA {latest_sgpa:.2f} does not meet requirement (>= {target_sgpa:.2f})."
                evaluated_criteria.append(
                    EvaluatedCriterion(
                        criterion=crit,
                        status=status,
                        basis=EvidenceBasis.OFFICIAL_IMPORT,
                        details=det,
                    )
                )

        else:
            # Fallback
            evaluated_criteria.append(
                EvaluatedCriterion(
                    criterion=crit,
                    status=CriterionResultStatus.UNKNOWN,
                    basis=EvidenceBasis.SELF_DECLARED,
                    details=f"Evaluation rule for type '{crit.type}' requires official clarification.",
                    missing_input_label=crit.label,
                )
            )

    met_count = sum(1 for c in evaluated_criteria if c.status == CriterionResultStatus.MET)
    not_met_count = sum(1 for c in evaluated_criteria if c.status == CriterionResultStatus.NOT_MET)
    unknown_count = sum(1 for c in evaluated_criteria if c.status == CriterionResultStatus.UNKNOWN)

    summary_counts_text = f"{met_count} met · {not_met_count} not met · {unknown_count} unknown"

    missing_docs = [c.missing_input_label for c in evaluated_criteria if c.missing_input_label]

    return {
        "schemeId": scheme.schemeId,
        "schemeName": scheme.name,
        "track": selected_track,
        "verificationLevel": scheme.verificationLevel.value,
        "isUnverified": is_conflicting_or_unverified,
        "summaryCountsText": summary_counts_text,
        "counts": {
            "met": met_count,
            "notMet": not_met_count,
            "unknown": unknown_count,
            "total": len(evaluated_criteria),
        },
        "criteria": [c.to_dict() for c in evaluated_criteria],
        "missingDocuments": missing_docs,
        "bannerMessage": (
            "⚠️ Not yet verified against an official source. Criteria drawn from secondary educational portals; "
            "must be verified against the official portal before reliance."
            if is_conflicting_or_unverified else None
        ),
    }
