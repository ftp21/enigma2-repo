#!/usr/bin/env python3
"""Generates an opkg 'Packages' index for every *.ipk in a directory,
without depending on the opkg-utils apt package (not reliably installable
on GitHub's ubuntu-latest runners - see the "Install opkg-utils" step this
replaced). An .ipk is just an `ar` archive of debian-binary/control.tar.gz/
data.tar.gz, so this only needs `ar` and `tar`, both already on the runner.

Usage: gen_packages_index.py <directory>
Writes <directory>/Packages (Packages.gz is gzipped by the workflow step).
"""
import hashlib
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def controlFields(ipkPath):
	with tempfile.TemporaryDirectory() as tmp:
		tmp = Path(tmp)
		subprocess.run(["ar", "x", str(ipkPath.resolve()), "--output", str(tmp)], check=True, cwd=tmp)
		controlArchive = next(tmp.glob("control.tar*"))
		with tarfile.open(controlArchive) as tf:
			member = next(m for m in tf.getmembers() if Path(m.name).name == "control")
			text = tf.extractfile(member).read().decode("utf-8")

	fields = {}
	order = []
	lastKey = None
	for line in text.splitlines():
		if line.startswith((" ", "\t")) and lastKey:
			fields[lastKey] += "\n" + line
			continue
		if ":" not in line:
			continue
		key, _, value = line.partition(":")
		key = key.strip()
		fields[key] = value.strip()
		order.append(key)
		lastKey = key
	return fields, order


def main():
	directory = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
	stanzas = []
	for ipkPath in sorted(directory.glob("*.ipk")):
		fields, order = controlFields(ipkPath)
		data = ipkPath.read_bytes()
		fields["Filename"] = ipkPath.name
		fields["Size"] = str(len(data))
		fields["MD5Sum"] = hashlib.md5(data).hexdigest()
		fields["SHA256sum"] = hashlib.sha256(data).hexdigest()
		for extra in ("Filename", "Size", "MD5Sum", "SHA256sum"):
			if extra not in order:
				order.append(extra)
		stanzas.append("\n".join(f"{k}: {fields[k]}" for k in order if k in fields))

	(directory / "Packages").write_text(("\n\n".join(stanzas) + "\n") if stanzas else "", encoding="utf-8")
	print(f"Packages written with {len(stanzas)} package(s).")


if __name__ == "__main__":
	main()
