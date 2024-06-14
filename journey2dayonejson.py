import argparse
import tempfile
import typing as t
import json
import uuid
import os, glob
from datetime import datetime
from markdownify import markdownify
import shutil
import pytz
from tzlocal import get_localzone

def getuuid() -> str:
    uu = str(uuid.uuid4())
    return uu.replace("-", "").upper()


def convert_unixtime(unixtime:int, tzinfo:pytz.BaseTzInfo)->str:
    date = datetime.fromtimestamp(unixtime / 1000)
    date = tzinfo.localize(date)
    return date.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_photo(name:str, i:int) -> dict[str, t.Any]:
    md5, ext = name.split(".")
    return {
        "orderInEntry": i,
        "identifier": getuuid(),
        "type": ext,
        "isSketch": False,
        "creationDevice": "Joe's MacBook Pro",
        "md5": md5,
    }


def journeyjson2dayonejson(journey:dict[str, t.Any])->dict[str, t.Any]:
    tz = pytz.timezone(journey["timezone"]) if journey["timezone"].strip() else get_localzone()

    dayone = {
        "creationOSName": "macOS",
        "creationOSVersion": "10.15.7",
        "creationDevice": "Joe's MacBook Pro",
        "creationDeviceType": "MacBook Pro",
        "creationDate": convert_unixtime(journey["date_journal"], tz),
        "timeZone": str(tz),
        "starred": False,
        "uuid": getuuid(),
        "text": markdownify(journey["text"], strip=["div"]).strip().replace("\\n\\n", "\\n").replace("\\n  \\n", "\\n"),
    }

    if abs(journey["lat"]) < 90:
        dayone["location"] = {
            "longitude": journey["lon"],
            "latitude": journey["lat"],
            "placeName": journey["address"].strip(),
        }

    if journey["weather"]["degree_c"] < 100:
        dayone["weather"] = {
            "temperatureCelsius": journey["weather"]["degree_c"],
            "conditionsDescription": journey["weather"]["description"],
        }

    if journey["tags"]:
        dayone["tags"] = journey["tags"]

    if journey["photos"]:
        dayone["photos"] = [convert_photo(f, i) for i, f in enumerate(journey["photos"])]
    return dayone

parser = argparse.ArgumentParser(prog="journey2dayone", description="Convert Journey zip entries to the Day One format")
parser.add_argument("filename", help="Path to journal in Journey zip format")
parser.add_argument("-o", "--output", default="dayone", help = "Filename of journal in Day One zip format (without extension)")
parser.add_argument("-j", "--journal-name", default="Journey", help="Name of journal when imported into Day One")

args = parser.parse_args()

tempdir = tempfile.TemporaryDirectory() 
shutil.unpack_archive(args.filename, extract_dir=tempdir.name)
os.makedirs(os.path.join(tempdir.name, "dayone/photos"))

entries = []
for f in glob.glob(os.path.join(tempdir.name, "journey/*.json")):
    with open(f, "r") as fh:
        journey = json.load(fh)

    dayone = journeyjson2dayonejson(journey)

    if journey["photos"]:
        for (p, j) in zip(dayone["photos"], journey["photos"]):
            source = os.path.join(tempdir.name, "journey", j)
            target = os.path.join(tempdir.name, "dayone", "photos", j)
            shutil.copyfile(source, target)

            dayone["text"] = dayone["text"] + "\n![](dayone-moment://{})".format(p["identifier"])
    entries.append(dayone)

dayone_json = {"metadata": {"version": "1.0"}, "entries": entries}

with open(os.path.join(tempdir.name, "dayone", f"{args.journal_name}.json"), "w") as fh:
    fh.write(json.dumps(dayone_json, indent=4, separators=(",", ": ")).replace("/", r"\/"))

shutil.make_archive(os.path.join(os.path.dirname(args.filename), args.output), format="zip", root_dir=os.path.join(tempdir.name, "dayone"))

tempdir.cleanup()