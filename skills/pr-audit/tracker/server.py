#!/usr/bin/env python3
"""Serve a PR-audit tracker, or check a findings file.

Usage:
  python3 server.py PR_DIR [--port 8765]
      Serve PR_DIR/findings.json and PR_DIR/state.json behind the tracker page
      (index.html, beside this script). Loopback only. If the port is taken,
      the next free one within 20 is used; the chosen URL is printed.
  python3 server.py --check PR_DIR/findings.json
      Validate the findings file against the shape FORMAT.md describes.
      Prints one line per problem and exits 1 if there are any.

The page's Submit button sends POST /api/submit; the server answers, prints
a `submitted at ...; stopping` line, and exits 0. Run it as a tracked
background command so that exit reaches the agent as a notification; the
same command restarts it for another round, with state.json intact.

State is {item_id: {verdict, note, reviewed, updated_at}}. Writes go through
a lock and a temp-file rename, so a crash mid-write leaves the previous file
intact.
"""

from __future__ import annotations

import argparse
import datetime
import errno
import json
import os
import pathlib
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
STATE_LOCK = threading.Lock()

PROVENANCE = {"ran", "read", "unverified"}
GROUPS = {"A": ["did-not-hold", "held"], "B": ["lead", "complete"]}
ITEM_FIELDS = {
    "A": ["id", "provenance", "evidence", "summary", "detail"],
    "B": ["id", "summary", "turns_on", "grounded", "default"],
}
TOP_FIELDS = ["pr", "lead", "verdict", "limit_line", "risk_pointer", "verdicts", "sections"]
PR_FIELDS = ["number", "title", "url", "head", "audited"]


def check(path: pathlib.Path) -> list[str]:
    """Return the problems with a findings file; an empty list means it is well-formed."""
    problems: list[str] = []
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot read as JSON: {exc}"]

    def need(obj, fields, where):
        for f in fields:
            if f not in obj:
                problems.append(f"{where}: missing `{f}`")
            elif isinstance(obj[f], str) and not obj[f].strip() and f != "risk_pointer":
                problems.append(f"{where}: `{f}` is empty")

    if not isinstance(data, dict):
        return [f"{path}: top level is not an object"]
    need(data, TOP_FIELDS, "top level")
    if isinstance(data.get("pr"), dict):
        need(data["pr"], PR_FIELDS, "pr")
    else:
        problems.append("pr: not an object")

    lead = data.get("lead")
    if not isinstance(lead, list) or not lead:
        problems.append("lead: must be a non-empty list of {heading, text} paragraphs")
    else:
        for i, para in enumerate(lead):
            if not isinstance(para, dict):
                problems.append(f"lead[{i}]: not an object")
                continue
            need(para, ["heading", "text"], f"lead[{i}]")

    verdicts = data.get("verdicts")
    if not isinstance(verdicts, dict):
        problems.append("verdicts: not an object")
        verdicts = {}
    for sec_id in GROUPS:
        vocab = verdicts.get(sec_id)
        if not isinstance(vocab, list) or not vocab or not all(isinstance(v, str) and v for v in vocab):
            problems.append(f"verdicts.{sec_id}: must be a non-empty list of strings")

    sections = data.get("sections")
    if not isinstance(sections, list):
        problems.append("sections: not a list")
        return problems
    seen_ids: dict[str, str] = {}
    links: list[tuple[str, str]] = []
    found_sections = [s.get("id") for s in sections if isinstance(s, dict)]
    if found_sections != list(GROUPS):
        problems.append(f"sections: ids must be exactly {list(GROUPS)} in order, got {found_sections}")
    for sec in sections:
        if not isinstance(sec, dict):
            problems.append("sections: entry is not an object")
            continue
        sec_id = sec.get("id")
        where = f"section {sec_id}"
        need(sec, ["id", "title", "blurb", "groups"], where)
        if sec_id not in GROUPS:
            continue
        groups = sec.get("groups")
        if not isinstance(groups, list):
            problems.append(f"{where}: groups is not a list")
            continue
        group_ids = [g.get("id") for g in groups if isinstance(g, dict)]
        if group_ids != GROUPS[sec_id]:
            problems.append(f"{where}: group ids must be exactly {GROUPS[sec_id]} in order, got {group_ids}")
        for g in groups:
            if not isinstance(g, dict):
                continue
            gwhere = f"{where}/{g.get('id')}"
            need(g, ["id", "title", "items"], gwhere)
            for item in g.get("items") or []:
                if not isinstance(item, dict):
                    problems.append(f"{gwhere}: item is not an object")
                    continue
                item_id = item.get("id", "?")
                iwhere = f"{gwhere}/{item_id}"
                need(item, ITEM_FIELDS[sec_id], iwhere)
                if not str(item_id).startswith(sec_id):
                    problems.append(f"{iwhere}: id must start with `{sec_id}`")
                if item_id in seen_ids:
                    problems.append(f"{iwhere}: duplicate id (also in {seen_ids[item_id]})")
                seen_ids[item_id] = gwhere
                if sec_id == "A" and item.get("provenance") not in PROVENANCE:
                    problems.append(f"{iwhere}: provenance must be one of {sorted(PROVENANCE)}")
                for key in ("refs", "links"):
                    val = item.get(key, [])
                    if not isinstance(val, list) or not all(isinstance(v, str) for v in val):
                        problems.append(f"{iwhere}: `{key}` must be a list of strings")
                for target in item.get("links", []) or []:
                    links.append((item_id, target))
    for src, target in links:
        if target not in seen_ids:
            problems.append(f"{src}: links to `{target}`, which does not exist")
    return problems


def make_handler(pr_dir: pathlib.Path):
    findings_path = pr_dir / "findings.json"
    state_path = pr_dir / "state.json"
    index_path = HERE / "index.html"

    def read_state() -> dict:
        if not state_path.exists():
            return {}
        with state_path.open() as f:
            return json.load(f)

    def write_state(state: dict) -> None:
        tmp = state_path.with_suffix(".json.tmp")
        with tmp.open("w") as f:
            json.dump(state, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, state_path)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: HTTPStatus, payload) -> None:
            self._send(status, json.dumps(payload).encode(), "application/json")

        def _file(self, path: pathlib.Path, content_type: str) -> None:
            try:
                self._send(HTTPStatus.OK, path.read_bytes(), content_type)
            except FileNotFoundError:
                self._json(HTTPStatus.NOT_FOUND, {"error": f"{path.name} not found"})

        def _item_id(self) -> str | None:
            prefix = "/api/state/"
            if not self.path.startswith(prefix):
                return None
            item_id = self.path[len(prefix):]
            return item_id if item_id and "/" not in item_id else None

        def do_GET(self) -> None:
            if self.path in ("/", "/index.html"):
                self._file(index_path, "text/html; charset=utf-8")
            elif self.path == "/api/findings":
                self._file(findings_path, "application/json")
            elif self.path == "/api/state":
                with STATE_LOCK:
                    self._json(HTTPStatus.OK, read_state())
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_PUT(self) -> None:
            item_id = self._item_id()
            if item_id is None:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "bad item id"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                incoming = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
                return
            update = {k: v for k, v in incoming.items() if k in {"verdict", "note", "reviewed"}}
            with STATE_LOCK:
                state = read_state()
                entry = state.get(item_id, {})
                entry.update(update)
                entry["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(
                    timespec="seconds"
                )
                state[item_id] = entry
                write_state(state)
            self._json(HTTPStatus.OK, entry)

        def do_POST(self) -> None:
            if self.path != "/api/submit":
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                self.rfile.read(length)
            submitted_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            self._json(HTTPStatus.OK, {"submitted_at": submitted_at})
            print(f"submitted at {submitted_at}; stopping", flush=True)
            # shutdown() blocks until serve_forever() returns, so it must run off
            # the serving thread; the delay lets this response leave first.
            threading.Timer(0.2, self.server.shutdown).start()

        def do_DELETE(self) -> None:
            item_id = self._item_id()
            if item_id is None:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "bad item id"})
                return
            with STATE_LOCK:
                state = read_state()
                removed = state.pop(item_id, None)
                write_state(state)
            self._json(HTTPStatus.OK, {"removed": removed is not None})

        def log_message(self, fmt, *args) -> None:
            if args and ("/api/state/" in str(args[0]) or "/api/submit" in str(args[0])):
                super().log_message(fmt, *args)

    return Handler


def serve(pr_dir: pathlib.Path, port: int) -> None:
    handler = make_handler(pr_dir)
    for candidate in range(port, port + 21):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), handler)
            break
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
    else:
        sys.exit(f"no free port in {port}..{port + 20}")
    print(f"serving {pr_dir} at http://127.0.0.1:{candidate}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("interrupted; stopping", flush=True)
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pr_dir", nargs="?", type=pathlib.Path, help="directory holding findings.json and state.json")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", type=pathlib.Path, metavar="FINDINGS_JSON", help="validate a findings file and exit")
    args = parser.parse_args()

    if args.check is not None:
        problems = check(args.check.resolve())
        for p in problems:
            print(p)
        print(f"{args.check}: {'OK' if not problems else f'{len(problems)} problem(s)'}")
        sys.exit(1 if problems else 0)

    if args.pr_dir is None:
        parser.error("PR_DIR is required unless --check is given")
    pr_dir = args.pr_dir.resolve()
    if not (pr_dir / "findings.json").exists():
        sys.exit(f"{pr_dir / 'findings.json'} does not exist")
    serve(pr_dir, args.port)


if __name__ == "__main__":
    main()
