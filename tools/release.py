"""Check public files and build two skill packages without reading user materials."""

import argparse
import hashlib
import re
import struct
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FILES = ("SKILL.md", "agents/openai.yaml", "assets/avatar.png", "LICENSE")
DISPLAY_FIELDS = ("version", "display_name", "display_name_en", "description_zh", "description_en")
PATTERNS = {
    "home-directory path": re.compile(r"/(?:Users|home)/[^\s/]+|\b[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/]"),
    "credential-like string": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|(?:AKIA|ASIA)[A-Z0-9]{16})\b"),
    "private key": re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
}
EMAIL = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_skill(raw):
    match = re.fullmatch(r"---\n(.*?)\n---\n(.*)", raw.decode("utf-8"), re.S)
    require(match is not None, "Invalid SKILL.md frontmatter")
    return yaml.safe_load(match.group(1)), match.group(2)


def check_png(data, *, avatar=False):
    require(data[:8] == b"\x89PNG\r\n\x1a\n", "Image must be PNG")
    width, height = struct.unpack(">II", data[16:24])
    require(width > 0 and height > 0, "PNG dimensions must be positive")
    if avatar:
        require((width, height) == (512, 512), "Avatar must be 512 x 512")
        require(len(data) <= 500000, "Avatar exceeds 500 KB")
    offset = 8
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        require(kind not in {b"eXIf", b"tEXt", b"zTXt", b"iTXt", b"tIME"}, "PNG contains extra metadata")
        offset += length + 12
    require(offset == len(data), "Malformed PNG chunks")


def check_public_files():
    public = (ROOT / ".public-files").read_text().splitlines()
    require(len(public) == len(set(public)), "Duplicate public file entry")
    for name in public:
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts, "Unsafe public file path")
        require((ROOT / path).is_file() and not (ROOT / path).is_symlink(), f"Missing or linked file: {name}")
    if (ROOT / ".git").is_dir():
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        require(set(filter(None, tracked)) <= set(public), "Tracked files exceed .public-files; review the file list")
    for name in public:
        if name.endswith(".png"):
            check_png((ROOT / name).read_bytes(), avatar=(name == "assets/avatar.png"))
            continue
        text = (ROOT / name).read_text()
        for label, pattern in PATTERNS.items():
            require(not pattern.search(text), f"Review {name}: {label}")
        for address in EMAIL.findall(text):
            require(address.endswith("@users.noreply.github.com"), f"Review {name}: personal email")
        if name.endswith(".md"):
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if "://" not in link and not link.startswith("#"):
                    require((ROOT / name).parent.joinpath(link.split("#", 1)[0]).exists(), f"Broken local link in {name}")
    print(f"Checked {len(public)} public files; no configured sensitive-content pattern matched.")


def check_skill():
    header, body = parse_skill((ROOT / "SKILL.md").read_bytes())
    require(header["name"] == "academic-writing-zh", "Unexpected skill name")
    require(header["license"] == "MIT", "Expected MIT license")
    require(isinstance(header.get("description"), str) and header["description"].strip(), "Missing description")
    metadata = header["metadata"]
    for key in DISPLAY_FIELDS:
        require(isinstance(metadata.get(key), str) and metadata[key].strip(), f"Missing metadata: {key}")
    version = metadata["version"]
    require(re.fullmatch(r"\d+\.\d+\.\d+", version), "Version must use major.minor.patch")
    ui = yaml.safe_load((ROOT / "agents/openai.yaml").read_text())["interface"]
    require(ui["display_name"] == metadata["display_name"], "Display names differ")
    require(25 <= len(ui["short_description"]) <= 64, "Invalid short description length")
    require(version in (ROOT / "CHANGELOG.md").read_text(), "Version missing from changelog")
    return header, body, version


def write_package(path, overrides):
    expected = {}
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zipped:
        for name in PACKAGE_FILES:
            data = overrides.get(name, (ROOT / name).read_bytes())
            entry = ZipInfo(f"academic-writing-zh/{name}", date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            zipped.writestr(entry, data)
            expected[entry.filename] = data
    with ZipFile(path) as zipped:
        require(zipped.testzip() is None, "ZIP CRC check failed")
        require(set(zipped.namelist()) == set(expected), "Unexpected ZIP entries")
        for name, data in expected.items():
            require(zipped.read(name) == data, f"ZIP content differs: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without building ZIP files")
    args = parser.parse_args()
    check_public_files()
    header, body, version = check_skill()
    if args.check:
        print(f"Version {version} passed local checks.")
        return
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    standard = dist / f"academic-writing-zh-{version}.zip"
    upload = dist / f"academic-writing-zh-upload-{version}.zip"
    promoted = {key: value for key, value in header.items() if key != "metadata"}
    promoted.update(header["metadata"])
    upload_text = "---\n" + yaml.safe_dump(promoted, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + body
    upload_raw = upload_text.encode("utf-8")
    parsed, upload_body = parse_skill(upload_raw)
    require(upload_body == body, "Upload body changed")
    require(all(parsed[key] == header["metadata"][key] for key in DISPLAY_FIELDS), "Upload metadata differs")
    write_package(standard, {})
    write_package(upload, {"SKILL.md": upload_raw})
    sums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in (standard, upload))
    (dist / "SHA256SUMS").write_text(sums)
    print(f"Built and reopened two ZIP files for {version}; upload and standard bodies match.")


if __name__ == "__main__":
    main()
