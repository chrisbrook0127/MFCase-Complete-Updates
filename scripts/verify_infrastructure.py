"""Read-only MFCase Complete setup and local ZIP safety validation."""
import argparse
import hashlib
import os
import re
import stat
import subprocess
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

REPOSITORY = "chrisbrook0127/MFCase-Complete-Updates"
ORIGINAL = {
    "README.md": ("100644", "blob", "0c45643211f9260582ffce8a70b46e567c9323c4"),
    "installer": ("100644", "blob", "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"),
    "updates": ("100644", "blob", "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"),
}
ADDED = {
    "AGENTS.md", "PROJECT_RULES.md", "APP_BASELINE.md", "PROJECT_STATE.md",
    "WORK_LOG.md", "CHANGELOG.md", "CI_ADAPTER.md",
    "scripts/verify_infrastructure.py", "tests/test_infrastructure.py",
    ".github/workflows/windows-infrastructure.yml",
}
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    prefix + str(i) for prefix in ("COM", "LPT") for i in range(1, 10)
}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def verify_repository(origin, github_repository=None):
    accepted = {
        "https://github.com/" + REPOSITORY,
        "https://github.com/" + REPOSITORY + ".git",
        "git@github.com:" + REPOSITORY + ".git",
    }
    require(origin.strip() in accepted, "Wrong repository origin")
    require(github_repository in (None, "", REPOSITORY), "Wrong GitHub repository")

def verify_tree(entries):
    require(set(entries) == set(ORIGINAL) | ADDED,
            "Missing or unexpected tracked files in setup tree")
    for path, identity in ORIGINAL.items():
        require(entries[path] == identity, "Protected original changed: " + path)
    for path in ADDED:
        require(entries[path][:2] == ("100644", "blob"), "Unsafe infrastructure file type")

def read_tree():
    raw = subprocess.check_output(["git", "ls-tree", "-r", "-z", "HEAD"])
    entries = {}
    for entry in raw.split(b"\0"):
        if entry:
            header, path = entry.split(b"\t", 1)
            entries[path.decode("utf-8")] = tuple(header.decode("ascii").split())
    return entries

def verify_setup():
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True)
    verify_repository(origin, os.environ.get("GITHUB_REPOSITORY"))
    verify_tree(read_tree())
    print("PASS repository identity, 3 original blobs, exact 10-file infrastructure allowlist.")
    print("APPLICATION VALIDATION BLOCKED: approved Complete source and tests unavailable.")

def verify_archive(path, expected_sha):
    require(re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha) is not None,
            "An independently approved SHA-256 is required")
    with Path(path).open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    require(actual == expected_sha.lower(), "Archive SHA-256 mismatch")
    with ZipFile(path) as archive:
        infos = archive.infolist()
        require(bool(infos), "Empty archive")
        require(sum(i.file_size for i in infos) <= 1_000_000_000, "Expanded archive exceeds inspection limit")
        seen = set()
        files = set()
        folders = set()
        for entry in infos:
            name = entry.filename
            p = PurePosixPath(name)
            require(name and not p.is_absolute() and ".." not in p.parts
                    and p.as_posix() == name.rstrip("/")
                    and not any(c in name for c in '\\:<>"|?*')
                    and not stat.S_ISLNK(entry.external_attr >> 16),
                    "Unsafe archive member")
            require(all(part.rstrip(" .") == part and part.split(".")[0].upper() not in RESERVED
                        and not any(ord(c) < 32 for c in part) for part in p.parts),
                    "Unsafe Windows archive destination")
            key = p.as_posix().casefold()
            parents = {q.as_posix().casefold() for q in p.parents if q.as_posix() != "."}
            require(key not in seen and not (parents & files), "Duplicate or conflicting archive destination")
            seen.add(key)
            folders.update(parents)
            if entry.is_dir():
                folders.add(key)
            else:
                require(key not in folders, "Conflicting file and directory destination")
                files.add(key)
        require(bool(files), "Archive contains no files")
        require(archive.testzip() is None, "Archive CRC failure")
    return len(infos)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("setup")
    arc = subs.add_parser("archive")
    arc.add_argument("--archive", required=True, type=Path)
    arc.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if args.command == "setup":
        verify_setup()
    else:
        count = verify_archive(args.archive, args.sha256)
        print("PASS archive identity and safety inspection:", count, "members. Not application validation.")

if __name__ == "__main__":
    main()
