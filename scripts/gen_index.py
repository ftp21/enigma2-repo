#!/usr/bin/env python3
"""Generates an index.html for the gh-pages feed directory that looks like
Apache's default mod_autoindex listing (the classic "Index of /" page with
Name / Last modified / Size / Description columns), since GitHub Pages has
no server-side autoindex of its own.

Usage: gen_index.py <directory>

"Last modified" is read from git history (last commit that touched each
file), not the filesystem mtime - a plain checkout resets every file's
mtime to checkout time, which would make every entry show the same instant.
Requires a non-shallow checkout (fetch-depth: 0) to see each file's real
last-changed commit.
"""
import html
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE = {"index.html", ".git", ".github", "scripts", "README.md", "_main"}


def humanSize(numBytes):
	size = float(numBytes)
	for unit in ("", "K", "M", "G"):
		if size < 1024 or unit == "G":
			return f"{size:.0f}{unit}" if unit == "" else f"{size:.1f}{unit}"
		size /= 1024
	return f"{size:.1f}G"


def lastModified(path):
	try:
		out = subprocess.run(
			["git", "log", "-1", "--format=%aI", "--", path.name],
			cwd=path.parent, capture_output=True, text=True, check=True,
		).stdout.strip()
		if out:
			dt = datetime.fromisoformat(out).astimezone(timezone.utc)
			return dt.strftime("%Y-%m-%d %H:%M")
	except Exception:
		pass
	return "-"


def main():
	directory = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
	entries = sorted(
		p for p in directory.iterdir()
		if p.name not in EXCLUDE and not p.name.startswith(".")
	)

	rows = []
	for p in entries:
		name = p.name
		size = humanSize(p.stat().st_size) if p.is_file() else "-"
		modified = lastModified(p)
		rows.append(
			f'<tr><td><a href="{html.escape(name)}">{html.escape(name)}</a></td>'
			f'<td>{modified}</td><td align="right">{size}</td></tr>'
		)

	page = f"""<!DOCTYPE html>
<html>
<head>
<title>Index of /</title>
<meta charset="utf-8">
<style>
body {{ font-family: monospace; margin: 1.5em; }}
table {{ border-collapse: collapse; }}
th, td {{ padding: 2px 12px 2px 0; text-align: left; }}
th {{ border-bottom: 1px solid #999; }}
a {{ text-decoration: none; color: #0000EE; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>Index of /</h1>
<hr>
<table>
<tr><th>Name</th><th>Last modified</th><th>Size</th></tr>
{"".join(rows)}
</table>
<hr>
</body>
</html>
"""
	(directory / "index.html").write_text(page, encoding="utf-8")
	print(f"index.html written with {len(entries)} entries.")


if __name__ == "__main__":
	main()
