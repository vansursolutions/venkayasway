#!/usr/bin/env python3
"""Publish the app to Google Play through the Play Developer API.

Usage:
  python3 android/publish.py upload  <bundle.aab> [--track internal|production] [--notes-en file] [--notes-te file]
  python3 android/publish.py listing               # push store listing text, icon, feature graphic, screenshots
  python3 android/publish.py status                # show tracks and version codes

Needs android/play-service-account.json (a Google Cloud service account key that has been
invited to the Play Console with release + store-presence permissions).
"""
import argparse, os, sys, time, re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = "com.srivenkaiahswamy.app"
KEY = os.path.join(HERE, "play-service-account.json")
STORE = os.path.join(HERE, "store")


def svc():
    if not os.path.exists(KEY):
        sys.exit(f"Missing {KEY}. Download the service account JSON key from Google Cloud and save it there.")
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=["https://www.googleapis.com/auth/androidpublisher"])
    return build("androidpublisher", "v3", credentials=creds, cache_discovery=False)


def read(path, default=""):
    return open(path, encoding="utf-8").read().strip() if path and os.path.exists(path) else default


def section(md, heading):
    """Pull a block out of store/listing.md by its bold heading."""
    m = re.search(r"\*\*" + re.escape(heading) + r"[^*]*\*\*\s*\n?(.*?)(?=\n\*\*|\Z)", md, re.S)
    return m.group(1).strip() if m else ""


def cmd_status(api, a):
    edit = api.edits().insert(packageName=PACKAGE, body={}).execute()["id"]
    tracks = api.edits().tracks().list(packageName=PACKAGE, editId=edit).execute().get("tracks", [])
    for t in tracks:
        for r in t.get("releases", []):
            print(f"{t['track']:<12} {r.get('status'):<11} versionCodes={r.get('versionCodes')} name={r.get('name')}")
    if not tracks:
        print("no releases yet")
    api.edits().delete(packageName=PACKAGE, editId=edit).execute()


def cmd_upload(api, a):
    edit = api.edits().insert(packageName=PACKAGE, body={}).execute()["id"]
    print("uploading", a.bundle)
    media = MediaFileUpload(a.bundle, mimetype="application/octet-stream", resumable=True)
    b = api.edits().bundles().upload(packageName=PACKAGE, editId=edit, media_body=media).execute()
    vc = b["versionCode"]
    print("uploaded versionCode", vc)
    notes = []
    en = read(a.notes_en); te = read(a.notes_te)
    if en: notes.append({"language": "en-IN", "text": en})
    if te: notes.append({"language": "te-IN", "text": te})
    release = {"versionCodes": [str(vc)], "status": a.status, "releaseNotes": notes}
    if a.name: release["name"] = a.name
    api.edits().tracks().update(packageName=PACKAGE, editId=edit, track=a.track, body={"track": a.track, "releases": [release]}).execute()
    api.edits().commit(packageName=PACKAGE, editId=edit).execute()
    print(f"committed: track={a.track} status={a.status} versionCode={vc}")


def cmd_listing(api, a):
    md = read(os.path.join(STORE, "listing.md"))
    edit = api.edits().insert(packageName=PACKAGE, body={}).execute()["id"]
    en = {"language": "en-IN", "title": section(md, "App name"), "shortDescription": section(md, "Short description"),
          "fullDescription": section(md, "Full description (4000"), "video": ""}
    te = {"language": "te-IN", "title": "శ్రీ వెంకయ్య స్వామి ఆలయం", "shortDescription": "శ్రీ వెంకయ్య స్వామి ఆలయం, సూళ్లూరుపేట: సమయాలు, కార్యక్రమాలు, అన్నదానం, గ్యాలరీ.",
          "fullDescription": section(md, "Full description (Telugu"), "video": ""}
    for l in (en, te):
        api.edits().listings().update(packageName=PACKAGE, editId=edit, language=l["language"], body=l).execute()
        print("listing", l["language"], "ok")
    for lang in ("en-IN", "te-IN"):
        for kind, files in (("icon", ["icon-512.png"]), ("featureGraphic", ["feature-graphic.png"]),
                            ("phoneScreenshots", sorted(os.listdir(os.path.join(STORE, "screenshots"))))):
            api.edits().images().deleteall(packageName=PACKAGE, editId=edit, language=lang, imageType=kind).execute()
            for f in files:
                p = os.path.join(STORE, "screenshots" if kind == "phoneScreenshots" else "", f)
                if f.lower().endswith(".png"):
                    api.edits().images().upload(packageName=PACKAGE, editId=edit, language=lang, imageType=kind,
                                                media_body=MediaFileUpload(p, mimetype="image/png")).execute()
            print(lang, kind, len([f for f in files if f.endswith('.png')]), "image(s)")
    api.edits().details().update(packageName=PACKAGE, editId=edit, body={
        "defaultLanguage": "en-IN", "contactEmail": "info@srivenkaiahswamy.com", "contactWebsite": "https://srivenkaiahswamy.com"}).execute()
    api.edits().commit(packageName=PACKAGE, editId=edit).execute()
    print("listing committed")


if __name__ == "__main__":
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("upload"); u.add_argument("bundle"); u.add_argument("--track", default="production")
    u.add_argument("--status", default="completed", choices=["draft", "inProgress", "halted", "completed"])
    u.add_argument("--name"); u.add_argument("--notes-en", default=os.path.join(STORE, "release-notes-en.txt")); u.add_argument("--notes-te", default=os.path.join(STORE, "release-notes-te.txt"))
    sub.add_parser("listing"); sub.add_parser("status")
    a = p.parse_args(); api = svc()
    {"upload": cmd_upload, "listing": cmd_listing, "status": cmd_status}[a.cmd](api, a)
