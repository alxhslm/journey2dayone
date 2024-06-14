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

os.makedirs("dayone/photos", exist_ok=True)

entries = []
for f in glob.glob("./journey/*.json"):
    with open(f, "r") as fh:
        journey = json.load(fh)

    dayone = journeyjson2dayonejson(journey)

    if journey["photos"]:
        for (p, j) in zip(dayone["photos"], journey["photos"]):
            source = "./journey/" + str(j)
            target = "./dayone/photos/" + str(j)
            shutil.copyfile(source, target)

            dayone["text"] = dayone["text"] + "\n![](dayone-moment://{})".format(p["identifier"])
    entries.append(dayone)

dayone_json = {"metadata": {"version": "1.0"}, "entries": entries}

with open("dayone/Journey.json", "w") as fh:
    fh.write(json.dumps(dayone_json, indent=4, separators=(",", ": ")).replace("/", r"\/"))

if os.path.exists("dayone.zip"):
    os.remove("dayone.zip")

shutil.make_archive("dayone", "zip", "./dayone")
