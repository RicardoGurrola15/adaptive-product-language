#!/usr/bin/env python3
import argparse,json,statistics
from pathlib import Path
REQ={"case_id","condition","run_id","model","output","quality_scores","expected_findings_found","telemetry","evaluator"}; CONDS=["baseline","light","balanced","performance"]
def avg(v): return round(statistics.mean(v),4) if v else None
def score(r):
 v=[x for x in r["quality_scores"].values() if isinstance(x,(int,float))]; return statistics.mean(v) if v else None
def main():
 p=argparse.ArgumentParser(); p.add_argument("--results-dir",required=True); p.add_argument("--json",action="store_true"); a=p.parse_args(); rs=[]
 for f in sorted(Path(a.results_dir).glob("*.json")):
  r=json.loads(f.read_text()); miss=REQ-set(r)
  if miss: raise SystemExit(f"{f}: missing {sorted(miss)}")
  if r["condition"] not in CONDS: raise SystemExit(f"{f}: invalid condition")
  rs.append(r)
 g={}
 for r in rs: g.setdefault((r["case_id"],r["condition"]),[]).append(r)
 out=[]
 for (case,c),items in sorted(g.items()):
  s=[score(r) for r in items if score(r) is not None]; t={k:avg([r["telemetry"].get(k) for r in items if isinstance(r["telemetry"].get(k),(int,float))]) for k in ["input_tokens","output_tokens","elapsed_ms","tool_calls","files_read"]}
  out.append({"case_id":case,"condition":c,"n":len(items),"quality_mean":avg(s),"quality_median":statistics.median(s) if s else None,"quality_stdev":statistics.stdev(s) if len(s)>1 else None,"telemetry_mean":t})
 d=[]
 for case in sorted({r["case_id"] for r in rs}):
  b={r["run_id"]:score(r) for r in g.get((case,"baseline"),[]) if score(r) is not None}
  for c in CONDS[1:]:
   x={r["run_id"]:score(r) for r in g.get((case,c),[]) if score(r) is not None}; z=[x[k]-v for k,v in b.items() if k in x]
   if z: d.append({"case_id":case,"condition":c,"pairs":len(z),"mean_delta":avg(z),"wins":sum(q>.25 for q in z),"ties":sum(abs(q)<=.25 for q in z),"losses":sum(q<-.25 for q in z)})
 result={"records":len(rs),"summaries":out,"paired_deltas":d}; print(json.dumps(result,indent=2) if a.json else json.dumps(result))
if __name__=="__main__": main()
