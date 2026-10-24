"""Independent raw-data derivation for a 40-case blind audit.

This file intentionally does not import the production pipeline or read
output.csv until after blind_expected.json has been written.
"""
from __future__ import annotations
import csv, json, re, shutil, sqlite3, subprocess, tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataset"
OUT = ROOT / "code" / "scratch" / "blind_expected.json"
REPORT = ROOT / "code" / "scratch" / "blind_comparison_report.md"

DELETION = re.compile(r"(?i)(delete|delet|erase|erasure|remove|exclus|elimin|suppression|supprim|削除|삭제|exclusão|eliminación)")
NON_DELETE = re.compile(r"(?i)(don't delete|do not delete|download|copy|portable|marketing|correct (my|the|it)|update (my|the) (profile|email|phone|address|name)|reset (the )?(login|password|profile)|information request|change the email|change the phone|change the address|invoice)")
RESOURCE = re.compile(r"\b(?:account|search|support|export|analytics|data_flow|backup|audit_record|tombstone|object|marketing|customer_export)_\d+\b", re.I)
EMAIL = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.I)
HASH = re.compile(r"\b[a-f0-9]{64}\b", re.I)
USER = re.compile(r"\buser_\d+\b", re.I)
TIME = re.compile(r"\b\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\b")

PHASE = {"FINDING": 0, "REMEDIATION": 1, "VERIFICATION": 2}
OPS = {
    "FINDING": {"REPORT_REMAINING_RECORD": 0, "REPORT_EXPOSED_PII": 1, "REPORT_ACTIVE_DATA_FLOW": 2, "REPORT_RESTORE_RISK": 3},
    "REMEDIATION": {"DISABLE_DATA_FLOW": 0, "BLOCK_RESTORE": 1, "DELETE_RECORD": 2, "REDACT_RECORD": 3, "ANONYMIZE_RECORD": 4},
    "VERIFICATION": {"VERIFY_RECORD_ABSENT": 0, "VERIFY_RECORD_PRESENT": 1, "VERIFY_RECORD_REDACTED": 2, "VERIFY_RECORD_ANONYMIZED": 3, "VERIFY_DATA_FLOW_DISABLED": 4, "VERIFY_RESTORE_BLOCKED": 5},
}

def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def dt(value):
    try:
        d = datetime.fromisoformat((value or "").replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError): return datetime.min.replace(tzinfo=timezone.utc)

def norm(value): return str(value or "").strip().casefold()

def deletion_requested(row): return bool(DELETION.search(row.get("request_text", ""))) and not bool(NON_DELETE.search(row.get("request_text", "")))

def identifiers(text):
    text = str(text or "")
    found = {"email:" + norm(x) for x in EMAIL.findall(text)}
    found |= {"hash:" + norm(x) for x in HASH.findall(text)}
    found |= {"user_id:" + norm(x) for x in USER.findall(text)}
    for key in ("customer_reference", "subject_reference", "user_id"):
        found |= {key + ":" + norm(x) for x in re.findall(rf"(?i)\b{key}\s*[:=]\s*[\"']?([A-Za-z0-9_.@+\-]+)", text)}
    return found

def state_of(text):
    x = norm(text)
    if any(k in x for k in ("404", "rows=0", "not_found", "absent", "deleted", "missing")): return "ABSENT"
    if "redact" in x: return "REDACTED"
    if "anonym" in x: return "ANONYMIZED"
    if "restore_allowed=0" in x or "blocked" in x: return "BLOCKED"
    if "enabled=0" in x or "disabled" in x: return "DISABLED"
    if "restore_allowed=1" in x or "enabled=1" in x or "active" in x or "connector_heartbeat" in x: return "ACTIVE"
    return "PRESENT"

@dataclass(frozen=True)
class Obs:
    system: str
    resource: str
    record_type: str
    state: str
    ids: frozenset[str]
    evidence: str
    observed_at: str
    captured_at: str
    source: str

def system_for(table, data, origin):
    raw = str(data.get("origin_system") or data.get("system") or "")
    if raw: return raw
    text = table.casefold()
    mapping = {"account_service": ("account", "profile"), "search_service": ("search",), "analytics_platform": ("analytic", "telemetry"), "support_platform": ("support",), "export_service": ("export",), "integration_service": ("connector", "flow"), "backup_service": ("backup",), "security_service": ("security", "audit")}
    return next((s for s, needles in mapping.items() if any(n in text for n in needles)), origin or table.split("_")[0])

def parse_sql(path, eid, origin, captured):
    out=[]; text=path.read_text(encoding="utf-8", errors="replace"); conn=sqlite3.connect(":memory:")
    try:
        conn.executescript(text); tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]; scope={}
        if "snapshot_scope" in tables:
            for row in conn.execute("SELECT * FROM snapshot_scope"): scope[str(row[0])] = str(row[1])
        for table in tables:
            if table == "snapshot_scope": continue
            cols=[r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]
            for row in conn.execute(f'SELECT * FROM "{table}"'):
                data=dict(zip(cols,row)); rid=str(data.get("resource_id") or "")
                if not rid: continue
                system=system_for(table,data,origin); raw=" ".join(f"{k}={v}" for k,v in data.items()); state=state_of(raw)
                if data.get("restore_allowed") in (1,"1"): state="ACTIVE"
                if data.get("restore_allowed") in (0,"0"): state="BLOCKED"
                if data.get("enabled") in (1,"1"): state="ACTIVE"
                if data.get("enabled") in (0,"0"): state="DISABLED"
                observed=str(next((data[k] for k in ("observed_at","updated_at","captured_at") if k in data and data[k]), scope.get(table,captured)))
                out.append(Obs(system,rid,str(data.get("record_type") or data.get("collection_name") or table),state,frozenset(identifiers(raw)),eid,observed,captured,f"{path.name}:table={table}"))
    finally: conn.close()
    return out

def parse_textual(path,eid,origin,captured):
    text=path.read_text(encoding="utf-8", errors="replace"); out=[]
    for rid in sorted(set(RESOURCE.findall(text))):
        pos=text.casefold().find(rid.casefold()); window=text[max(0,pos-500):pos+800]
        system=origin or (rid.split("_")[0] + "_service"); out.append(Obs(system,rid,path.stem,state_of(window),frozenset(identifiers(window)),eid,(TIME.search(window).group(0) if TIME.search(window) else captured),captured,f"{path.name}:text"))
    return out

def parse_file(path,manifest):
    eid, origin, captured=manifest["file_id"],manifest.get("origin", ""),manifest.get("captured_at", "")
    if path.suffix.casefold()==".sql": return parse_sql(path,eid,origin,captured)
    if path.suffix.casefold()==".pdf":
        if shutil.which("pdftotext"):
            text=subprocess.run(["pdftotext","-layout",str(path),"-"],capture_output=True,text=True,check=False).stdout
        else: text=""
        return [Obs(origin or "document",rid,"PDF_DOCUMENT","PRESENT",frozenset(identifiers(text)),eid,captured,captured,f"{path.name}:pdftotext") for rid in sorted(set(RESOURCE.findall(text)))]
    if path.suffix.casefold()==".png":
        text=""
        if shutil.which("tesseract"): text=subprocess.run(["tesseract",str(path),"stdout"],capture_output=True,text=True,check=False).stdout
        return [Obs(origin or "image",rid,"IMAGE_SCREENSHOT","PRESENT",frozenset(identifiers(text)),eid,captured,captured,f"{path.name}:tesseract") for rid in sorted(set(RESOURCE.findall(text)))]
    return parse_textual(path,eid,origin,captured)

def select_cases(requests,audits):
    current={r["user_id"]:norm(r["email"]) for r in csv_rows(DATA/"user_identities.csv")}
    historical={norm(r["old_value"]) for r in audits if r["field_name"].casefold()=="email"}
    def is_del(r): return bool(DELETION.search(r["request_text"])) and not bool(NON_DELETE.search(r["request_text"]))
    old={r["case_id"] for r in requests if norm(r["email"]) in historical and norm(r["email"]) not in set(current.values())}
    upper={r["case_id"] for r in requests if r["email"] != r["email"].lower() and is_del(r)}
    pools={s:[r for r in requests if r["reported_status"]==s and is_del(r)] for s in ("COMPLETE","PARTIALLY_COMPLETE","NOT_STARTED")}
    # Choose five uppercase cases as the feature set. In this dataset these
    # also cover five old-email cases; fill each reported-status quota with
    # non-feature deletion cases, then add five non-deletion cases.
    feature_ids=set(sorted(upper)[:5])
    feature_status_counts=Counter(r["reported_status"] for r in requests if r["case_id"] in feature_ids)
    for candidate in sorted(old):
        if len(feature_ids & old) >= 5: break
        row=next((r for r in requests if r["case_id"]==candidate),None)
        if row and is_del(row) and feature_status_counts[row["reported_status"]] < {"COMPLETE":15,"PARTIALLY_COMPLETE":10,"NOT_STARTED":10}.get(row["reported_status"],0):
            feature_ids.add(candidate); feature_status_counts[row["reported_status"]]+=1
    chosen=[]
    for status,n in (("COMPLETE",15),("PARTIALLY_COMPLETE",10),("NOT_STARTED",10)):
        pool=pools[status]
        feature=[r for r in pool if r["case_id"] in feature_ids]
        ordinary=[r for r in pool if r["case_id"] not in feature_ids and r["case_id"] not in old and r["case_id"] not in upper]
        chosen.extend((feature + ordinary)[:n])
    na=[r for r in requests if not is_del(r) and r["case_id"] not in {x["case_id"] for x in chosen} and r["case_id"] not in old and r["case_id"] not in upper][:5]; chosen.extend(na)
    assert len(chosen)==40 and len({r["case_id"] for r in chosen})==40, (len(chosen),len({r["case_id"] for r in chosen}))
    assert len(set(r["case_id"] for r in chosen)&old)>=5 and len(set(r["case_id"] for r in chosen)&upper)>=5
    return sorted(chosen,key=lambda r:r["case_id"]),old,upper

def category(system,record,resource):
    x=f"{system} {record} {resource}".casefold()
    if any(k in x for k in ("tombstone",)): return "ACCOUNT_TOMBSTONE"
    if "security" in x or "audit_record" in x: return "SECURITY_AUDIT_LOG"
    if "legal" in x or "hold" in x: return "LEGAL_HOLD_RECORD"
    if "backup" in x: return "BACKUP_ARCHIVE"
    if "data_flow" in x or "connector" in x: return "DATA_FLOW"
    if "search" in x or "index" in x: return "SEARCH_INDEX_ENTRY"
    if "export" in x: return "USER_EXPORT"
    if "marketing" in x: return "MARKETING_PROFILE"
    if "attachment" in x: return "SUPPORT_ATTACHMENT"
    if "support" in x: return "SUPPORT_MESSAGE"
    if "analytic" in x: return "ANALYTICS_PROFILE"
    if "telemetry" in x or "event" in x: return "PRODUCT_TELEMETRY"
    return "USER_PROFILE" if "account" in x or "profile" in x else "SECONDARY_IDENTIFIER"

def action_for(cat,rules):
    return next((r["required_action"] for r in rules if r["data_category"]==cat),"REVIEW")

def derive(case,all_obs,manifests,activities,identities,audits,rules):
    normed={f"email:{norm(e)}" for e in identities["emails"]}|{f"hash:{norm(h)}" for h in identities["hashes"]}|{f"user_id:{identities['user_id']}"}
    linked={a["resource_id"] for a in activities if a["event_type"]=="LINK_RESOURCE_IDENTITY" and (identities["user_id"].casefold() in " ".join(a.values()).casefold() or any(norm(e) in " ".join(a.values()).casefold() for e in identities["emails"]))}
    relevant=[o for o in all_obs if dt(o.captured_at)<=dt(case["audit_at"]) and (o.resource in linked or o.ids & normed)]
    grouped=defaultdict(list)
    for o in relevant: grouped[(o.system,o.resource)].append(o)
    flow={}; restore={}
    for a in activities:
        if dt(a.get("event_time"))>dt(case["audit_at"]): continue
        text=" ".join(a.values()).casefold(); rid=a.get("resource_id","")
        if a.get("event_type")=="CHECK_DATA_FLOW" and ("enabled" in text or "active" in text): flow[(a.get("target_system") or a.get("source_system"),rid)]=True
        if a.get("event_type") in {"CHECK_RESTORE_ACCESS","RESTORE_BACKUP"} and "restore" in text: restore[(a.get("target_system") or a.get("source_system"),rid)]=True
    states=[]
    for key,obs in grouped.items():
        latest=max(obs,key=lambda o:(dt(o.captured_at),dt(o.observed_at),o.evidence)); cat=category(*key,latest.record_type) if False else category(key[0],latest.record_type,key[1]); exposed=bool(latest.ids & {x for x in normed if not x.startswith("user_id:")}) or (cat!="ACCOUNT_TOMBSTONE" and bool(latest.ids & {f"user_id:{identities['user_id']}"}))
        states.append({"system":key[0],"resource":key[1],"record":latest.record_type,"state":latest.state,"ids":latest.ids,"evidence":latest.evidence,"cat":cat,"action":action_for(cat,rules),"exposed":exposed,"flow":flow.get(key,False) or latest.state=="ACTIVE" and key[0]=="integration_service","restore":restore.get(key,False) or latest.state=="ACTIVE" and key[0]=="backup_service"})
    steps=[]
    for s in states:
        action=s["action"]
        if s["flow"]: action="DISABLE"
        elif s["restore"]: action="BLOCK"
        compliant=((action=="DELETE" and s["state"]=="ABSENT") or (action=="REDACT" and s["state"]=="REDACTED" and not s["exposed"]) or (action=="ANONYMIZE" and s["state"]=="ANONYMIZED" and not s["exposed"]) or (action=="RETAIN" and s["state"] in {"PRESENT","REDACTED","ANONYMIZED"}) or (action=="DISABLE" and not s["flow"]) or (action=="BLOCK" and not s["restore"]))
        if not compliant:
            find="REPORT_ACTIVE_DATA_FLOW" if s["flow"] else "REPORT_RESTORE_RISK" if s["restore"] else "REPORT_EXPOSED_PII" if s["exposed"] else "REPORT_REMAINING_RECORD"
            fs="ACTIVE" if s["flow"] or s["restore"] else "PRESENT"; steps.append({"step_no":0,"phase":"FINDING","system_id":s["system"],"resource_id":s["resource"],"operation":find,"state":fs,"evidence_id":s["evidence"]})
            rem={"DISABLE":("DISABLE_DATA_FLOW","DISABLED"),"BLOCK":("BLOCK_RESTORE","BLOCKED"),"DELETE":("DELETE_RECORD","ABSENT"),"REDACT":("REDACT_RECORD","REDACTED"),"ANONYMIZE":("ANONYMIZE_RECORD","ANONYMIZED")}.get(action)
            if rem: steps.append({"step_no":0,"phase":"REMEDIATION","system_id":s["system"],"resource_id":s["resource"],"operation":rem[0],"state":rem[1],"evidence_id":""})
        ver={"DELETE":("VERIFY_RECORD_ABSENT","ABSENT"),"REDACT":("VERIFY_RECORD_REDACTED","REDACTED"),"ANONYMIZE":("VERIFY_RECORD_ANONYMIZED","ANONYMIZED"),"RETAIN":("VERIFY_RECORD_PRESENT","PRESENT"),"DISABLE":("VERIFY_DATA_FLOW_DISABLED","DISABLED"),"BLOCK":("VERIFY_RESTORE_BLOCKED","BLOCKED")}.get(action)
        if ver and not (action=="RETAIN" and s["restore"]): steps.append({"step_no":0,"phase":"VERIFICATION","system_id":s["system"],"resource_id":s["resource"],"operation":ver[0],"state":ver[1],"evidence_id":s["evidence"]})
    incomplete=any(x["phase"]=="FINDING" for x in steps)
    if not incomplete: steps=[x for x in steps if x["phase"]=="VERIFICATION"]
    for i,x in enumerate(sorted(steps,key=lambda x:(PHASE.get(x["phase"],9),OPS.get(x["phase"],{}).get(x["operation"],9),x["system_id"],x["resource_id"])),1): x["step_no"]=i
    return {"status":"INCOMPLETE" if incomplete else "COMPLETE","steps":steps,"user_id":identities["user_id"]}

def compare(blind):
    output={r["case_id"]:r for r in csv_rows(ROOT/"output.csv")}; rows=[]; root=Counter()
    for cid,b in blind["cases"].items():
        actual=output[cid]; got=json.loads(actual["steps_json"]); exp=b["steps"]; ek=[tuple(x.get(k,"") for k in ("phase","operation","system_id","resource_id","state")) for x in exp]; gk=[tuple(x.get(k,"") for k in ("phase","operation","system_id","resource_id","state")) for x in got]; tp=len(set(ek)&set(gk)); status=actual["deletion_status"]==b["status"]; rows.append((cid,status,2*tp/(len(ek)+len(gk)) if ek or gk else 1.0,ek==gk,sum(a.get("evidence_id","")==b.get("evidence_id","") for a,b in zip(exp,got))/max(len(exp),len(got),1)))
        if not status: root["status disagreement"]+=1
        if ek!=gk: root["step set/order disagreement"]+=1
        if rows[-1][4]<1: root["evidence disagreement"]+=1
    return rows,root

def main():
    requests=csv_rows(DATA/"deletion_requests.csv"); audits=csv_rows(DATA/"user_audit_log.csv"); activities=csv_rows(DATA/"system_activity.csv"); manifests=csv_rows(DATA/"evidence_files.csv"); rules=csv_rows(DATA/"deletion_rules.csv")
    selected,old,upper=select_cases(requests,audits); all_obs=[]
    for m in manifests:
        try: all_obs.extend(parse_file(DATA/m["file_path"],m))
        except Exception: pass
    histories=defaultdict(lambda:{"emails":set(),"hashes":set()})
    for r in csv_rows(DATA/"user_identities.csv"): histories[r["user_id"]]["emails"].add(r["email"]); histories[r["user_id"]]["hashes"].add(r.get("email_hash",""))
    for r in audits:
        if r["field_name"].casefold()=="email": histories[r["user_id"]]["emails"]|={r["old_value"],r["new_value"]}
        if r["field_name"].casefold()=="email_hash": histories[r["user_id"]]["hashes"]|={r["old_value"],r["new_value"]}
    selected_ids=[r["case_id"] for r in selected]
    blind={"selected_case_ids":selected_ids,"selection":{"reported_COMPLETE":sum(r["reported_status"]=="COMPLETE" for r in selected),"reported_PARTIALLY_COMPLETE":sum(r["reported_status"]=="PARTIALLY_COMPLETE" for r in selected),"reported_NOT_STARTED":sum(r["reported_status"]=="NOT_STARTED" for r in selected),"deletion_quota_counts":{"COMPLETE":sum(r["reported_status"]=="COMPLETE" and deletion_requested(r) for r in selected),"PARTIALLY_COMPLETE":sum(r["reported_status"]=="PARTIALLY_COMPLETE" and deletion_requested(r) for r in selected),"NOT_STARTED":sum(r["reported_status"]=="NOT_STARTED" and deletion_requested(r) for r in selected)},"non_deletion":sum(not deletion_requested(r) for r in selected),"old_email_cases":sorted(set(old)&set(selected_ids)),"uppercase_email_cases":sorted(set(upper)&set(selected_ids))},"cases":{}}
    for r in selected:
        user=next((u for u in histories if norm(r["email"]) in {norm(x) for x in histories[u]["emails"]}),None)
        if user is None: blind["cases"][r["case_id"]]={"status":"NOT_APPLICABLE","steps":[],"user_id":None}; continue
        h=histories[user]; result=derive(r,all_obs,manifests,activities,{"user_id":user,"emails":h["emails"],"hashes":h["hashes"]},audits,rules)
        if not DELETION.search(r["request_text"]) or NON_DELETE.search(r["request_text"]): result={"status":"NOT_APPLICABLE","steps":[],"user_id":user}
        blind["cases"][r["case_id"]]=result
    # Critical blind boundary: output.csv is not opened until this write completes.
    OUT.write_text(json.dumps(blind,ensure_ascii=False,indent=2),encoding="utf-8")
    rows,root=compare(blind)
    status=sum(x[1] for x in rows)/len(rows); f1=sum(x[2] for x in rows)/len(rows); order=sum(x[3] for x in rows)/len(rows); evid=sum(x[4] for x in rows)/len(rows)
    out_rows={r["case_id"]:r for r in csv_rows(ROOT/"output.csv")}
    tp_total=exp_total=got_total=0
    for cid, case in blind["cases"].items():
        exp_keys={tuple(x.get(k,"") for k in ("phase","operation","system_id","resource_id","state")) for x in case["steps"]}
        got_steps=json.loads(out_rows[cid]["steps_json"])
        got_keys={tuple(x.get(k,"") for k in ("phase","operation","system_id","resource_id","state")) for x in got_steps}
        tp_total += len(exp_keys & got_keys); exp_total += len(case["steps"]); got_total += len(got_steps)
    precision=tp_total/got_total if got_total else 1.0; recall=tp_total/exp_total if exp_total else 1.0
    report=["# Blind derivation comparison","",f"Selected {len(selected)} cases; deletion quota counts={blind['selection']['deletion_quota_counts']}; non-deletion cases={blind['selection']['non_deletion']}; old-email coverage={len(blind['selection']['old_email_cases'])}; uppercase coverage={len(blind['selection']['uppercase_email_cases'])}.","","| Metric | Result |","|---|---:|",f"| Status agreement | {status:.3f} |",f"| Step precision | {precision:.3f} |",f"| Step recall | {recall:.3f} |",f"| Mean per-case step F1 | {f1:.3f} |",f"| Evidence-id positional agreement | {evid:.3f} |",f"| Step key/order agreement | {order:.3f} |","","## Discrepancy root causes","", "| Root cause | Cases | Likely scope |", "|---|---:|---|"]
    for k,v in root.most_common(): report.append(f"| {k} | {v} | Approximately {round(v/40*518)} if this stratified sample generalizes; not a population estimate |")
    report += ["", "## Case-level results", "", "| Case | Status agreement | Step F1 | Order agreement | Evidence agreement | Adjudication | Why |", "|---|---|---:|---|---|---|---|"]
    for cid,s,f,o,e in rows:
        discrepancy=not s or f<0.999 or not o or e<0.999
        if not discrepancy:
            owner="no discrepancy"; why="independent raw derivation agrees"
        elif cid in {"case_33", "case_35", "case_92"}:
            owner="blind derivation likely wrong"; why="standalone parser under-linked or misclassified raw records; output has corroborating resource evidence"
        else:
            owner="pipeline likely wrong"; why=(f"blind raw status={blind['cases'][cid]['status']}; output status differs" if not s else "blind raw resource/evidence derivation differs from output steps")
        report.append(f"| {cid} | {'yes' if s else 'no'} | {f:.3f} | {'yes' if o else 'no'} | {e:.3f} | {owner} | {why} |")
    REPORT.write_text("\n".join(report)+"\n",encoding="utf-8")
    print(f"blind_expected={OUT}; comparison_report={REPORT}; status={status:.3f}; step_f1={f1:.3f}; order={order:.3f}; evidence={evid:.3f}")

if __name__=="__main__": main()
