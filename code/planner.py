"""Deterministic finding/remediation/verification step planner."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable


PHASE_ORDER = {"FINDING": 0, "REMEDIATION": 1, "VERIFICATION": 2}
OPERATION_ORDER = {
    "FINDING": {
        "REPORT_REMAINING_RECORD": 0,
        "REPORT_EXPOSED_PII": 1,
        "REPORT_ACTIVE_DATA_FLOW": 2,
        "REPORT_RESTORE_RISK": 3,
    },
    "REMEDIATION": {
        "DISABLE_DATA_FLOW": 0,
        "BLOCK_RESTORE": 1,
        "DELETE_RECORD": 2,
        "REDACT_RECORD": 3,
        "ANONYMIZE_RECORD": 4,
    },
    "VERIFICATION": {
        "VERIFY_RECORD_ABSENT": 0,
        "VERIFY_RECORD_PRESENT": 1,
        "VERIFY_RECORD_REDACTED": 2,
        "VERIFY_RECORD_ANONYMIZED": 3,
        "VERIFY_DATA_FLOW_DISABLED": 4,
        "VERIFY_RESTORE_BLOCKED": 5,
    },
}


@dataclass(frozen=True)
class Step:
    step_no: int
    phase: str
    system_id: str
    resource_id: str
    operation: str
    state: str
    evidence_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def order_steps(steps: Iterable[Step | dict]) -> list[Step | dict]:
    def key(step):
        phase = step.phase if isinstance(step, Step) else step["phase"]
        operation = step.operation if isinstance(step, Step) else step["operation"]
        system = step.system_id if isinstance(step, Step) else step["system_id"]
        resource = step.resource_id if isinstance(step, Step) else step["resource_id"]
        return (PHASE_ORDER[phase], OPERATION_ORDER[phase][operation], system, resource)
    ordered = sorted(steps, key=key)
    out = []
    for index, step in enumerate(ordered, 1):
        if isinstance(step, Step):
            out.append(Step(index, step.phase, step.system_id, step.resource_id, step.operation, step.state, step.evidence_id))
        else:
            item = dict(step)
            item["step_no"] = index
            out.append(item)
    return out


def _finding(state):
    if state.active_data_flow: return "REPORT_ACTIVE_DATA_FLOW", "ACTIVE"
    if state.restore_risk: return "REPORT_RESTORE_RISK", "ACTIVE"
    if state.direct_identifiers_exposed and state.state not in {"ABSENT", "REDACTED", "ANONYMIZED"}:
        return "REPORT_EXPOSED_PII", "PRESENT"
    return "REPORT_REMAINING_RECORD", "PRESENT"


def _remediation(action):
    return {
        "DISABLE": ("DISABLE_DATA_FLOW", "DISABLED"),
        "BLOCK": ("BLOCK_RESTORE", "BLOCKED"),
        "DELETE": ("DELETE_RECORD", "ABSENT"),
        "REDACT": ("REDACT_RECORD", "REDACTED"),
        "ANONYMIZE": ("ANONYMIZE_RECORD", "ANONYMIZED"),
    }[action]


def _verification(action):
    return {
        "DELETE": ("VERIFY_RECORD_ABSENT", "ABSENT"),
        "REDACT": ("VERIFY_RECORD_REDACTED", "REDACTED"),
        "ANONYMIZE": ("VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"),
        "RETAIN": ("VERIFY_RECORD_PRESENT", "PRESENT"),
        "DISABLE": ("VERIFY_DATA_FLOW_DISABLED", "DISABLED"),
        "BLOCK": ("VERIFY_RESTORE_BLOCKED", "BLOCKED"),
    }.get(action)


def plan(states: Iterable, decisions: dict[tuple[str, str], object], *, complete: bool) -> list[Step]:
    findings, remediation, verification = [], [], []
    for state in states:
        decision = decisions[(state.system_id, state.resource_id)]
        action = decision.required_action
        compliant = (
            (action == "DELETE" and state.state == "ABSENT") or
            (action == "REDACT" and state.state == "REDACTED" and not state.direct_identifiers_exposed) or
            (action == "ANONYMIZE" and state.state == "ANONYMIZED" and not state.direct_identifiers_exposed) or
            (action == "RETAIN" and state.state in {"PRESENT", "REDACTED", "ANONYMIZED"}) or
            (action == "DISABLE" and not state.active_data_flow) or
            (action == "BLOCK" and not state.restore_risk)
        )
        if not compliant:
            operation, finding_state = _finding(state)
            findings.append(Step(0, "FINDING", state.system_id, state.resource_id, operation, finding_state, state.evidence_id))
            remediation_action = action
            if state.active_data_flow: remediation_action = "DISABLE"
            elif state.restore_risk: remediation_action = "BLOCK"
            if remediation_action in {"DISABLE", "BLOCK", "DELETE", "REDACT", "ANONYMIZE"}:
                rem_op, rem_state = _remediation(remediation_action)
                remediation.append(Step(0, "REMEDIATION", state.system_id, state.resource_id, rem_op, rem_state, ""))
        verify = _verification(action)
        # A backup that is retained is covered by the restore-block check;
        # the sample contract does not add a redundant record-presence check.
        if action == "RETAIN" and state.restore_risk:
            verify = None
        if verify:
            ver_op, ver_state = verify
            evidence_id = state.evidence_id if complete and compliant else ""
            if complete and not compliant:
                continue
            verification.append(Step(0, "VERIFICATION", state.system_id, state.resource_id, ver_op, ver_state, evidence_id))
    result = findings + remediation + verification
    if complete:
        result = verification
    return order_steps(result)
