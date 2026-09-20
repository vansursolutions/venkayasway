"""Single Lambda behind an HTTP API. Routes: events, media, sponsors, users."""
import json, os, re, uuid, datetime, base64
import boto3
from boto3.dynamodb.conditions import Attr

REGION = os.environ.get("AWS_REGION", "us-east-1")
ddb = boto3.resource("dynamodb")
EVENTS = ddb.Table(os.environ["EVENTS_TABLE"])
SPONSORS = ddb.Table(os.environ["SPONSORS_TABLE"])
MEDIA = ddb.Table(os.environ["MEDIA_TABLE"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
USER_POOL = os.environ["USER_POOL_ID"]
SENDER = os.environ["SENDER_EMAIL"]
ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
SITE_URL = os.environ.get("SITE_URL", "https://srivenkaiahswamy.com")
TEMPLE = "Sri Venkaiah Swamy Temple, Sullurupeta"

s3 = boto3.client("s3", region_name=REGION, config=boto3.session.Config(signature_version="s3v4"))
ses = boto3.client("sesv2", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)
cognito = boto3.client("cognito-idp", region_name=REGION)


def resp(status, body=None):
    return {"statusCode": status, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body if body is not None else {}, default=str)}


def claims(event):
    return (event.get("requestContext", {}).get("authorizer", {}).get("jwt", {}) or {}).get("claims", {}) or {}


def groups(event):
    g = claims(event).get("cognito:groups", "")
    if isinstance(g, list):
        return g
    return [x.strip() for x in str(g).strip("[]").split(",") if x.strip()]


def is_admin(event):
    return "admin" in groups(event)


def body(event):
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode()
    try:
        return json.loads(raw)
    except Exception:
        return {}


def now():
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def next_saturdays(n=16):
    d = datetime.date.today()
    d += datetime.timedelta(days=(5 - d.weekday()) % 7)
    return [(d + datetime.timedelta(weeks=i)).isoformat() for i in range(n)]


def norm_phone(p):
    p = re.sub(r"[^\d+]", "", p or "")
    if not p:
        return ""
    if p.startswith("+"):
        return p
    if len(p) == 10:
        return "+91" + p          # Indian mobile numbers by default
    if len(p) == 11 and p[0] == "1":
        return "+" + p
    if len(p) == 12 and p.startswith("91"):
        return "+" + p
    return "+" + p


def send_email(to, subject, text, html=None):
    content = {"Simple": {"Subject": {"Data": subject}, "Body": {"Text": {"Data": text}}}}
    if html:
        content["Simple"]["Body"]["Html"] = {"Data": html}
    try:
        ses.send_email(FromEmailAddress=f"\"Sri Venkaiah Swamy Temple\" <{SENDER}>", Destination={"ToAddresses": [to]}, Content=content)
        return True
    except Exception as e:
        print("EMAIL FAILED", to, repr(e))
        return False


def send_sms(phone, text):
    try:
        sns.publish(PhoneNumber=phone, Message=text,
                    MessageAttributes={"AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"}})
        return True
    except Exception as e:
        print("SMS FAILED", phone, repr(e))
        return False


def pretty_date(iso):
    try:
        return datetime.date.fromisoformat(iso).strftime("%A, %d %B %Y")
    except Exception:
        return iso


# ---------- events ----------
def list_events():
    items = EVENTS.scan().get("Items", [])
    items.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
    return resp(200, items)


def save_event(event, eid=None):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    b = body(event)
    if not b.get("date") or not b.get("title_en"):
        return resp(400, {"error": "date and title_en required"})
    item = {"id": eid or uuid.uuid4().hex[:12], "date": b["date"], "time": b.get("time", ""),
            "title_en": b["title_en"], "title_te": b.get("title_te", ""),
            "desc_en": b.get("desc_en", ""), "desc_te": b.get("desc_te", ""),
            "updated": now(), "by": claims(event).get("email", "")}
    EVENTS.put_item(Item=item)
    return resp(200, item)


def delete_event(event, eid):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    EVENTS.delete_item(Key={"id": eid})
    return resp(200, {"deleted": eid})


# ---------- media ----------
ALLOWED = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "video/mp4": "mp4", "video/quicktime": "mov", "video/webm": "webm"}


def list_media():
    items = MEDIA.scan().get("Items", [])
    items.sort(key=lambda x: x.get("created", ""), reverse=True)
    return resp(200, items)


def upload_url(event):
    b = body(event)
    ctype = b.get("contentType", "")
    if ctype not in ALLOWED:
        return resp(400, {"error": "unsupported type", "allowed": list(ALLOWED)})
    mid = uuid.uuid4().hex[:12]
    key = f"media/{datetime.date.today().year}/{mid}.{ALLOWED[ctype]}"
    url = s3.generate_presigned_url("put_object", Params={"Bucket": MEDIA_BUCKET, "Key": key, "ContentType": ctype}, ExpiresIn=3600)
    return resp(200, {"id": mid, "key": key, "uploadUrl": url})


def register_media(event):
    b = body(event)
    if not b.get("id") or not b.get("key"):
        return resp(400, {"error": "id and key required"})
    try:
        s3.head_object(Bucket=MEDIA_BUCKET, Key=b["key"])
    except Exception:
        return resp(400, {"error": "file not uploaded"})
    kind = "video" if b.get("contentType", "").startswith("video/") else "photo"
    item = {"id": b["id"], "key": b["key"], "type": kind, "title": (b.get("title") or "")[:120],
            "created": now(), "by": claims(event).get("email", "")}
    MEDIA.put_item(Item=item)
    return resp(200, item)


def delete_media(event, mid):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    it = MEDIA.get_item(Key={"id": mid}).get("Item")
    if it:
        try:
            s3.delete_object(Bucket=MEDIA_BUCKET, Key=it["key"])
        except Exception as e:
            print("S3 delete failed", e)
        MEDIA.delete_item(Key={"id": mid})
    return resp(200, {"deleted": mid})


# ---------- sponsors ----------
def sponsor_dates():
    items = SPONSORS.scan(FilterExpression=Attr("status").ne("declined")).get("Items", [])
    counts = {}
    for it in items:
        counts[it["date"]] = counts.get(it["date"], 0) + 1
    return resp(200, [{"date": d, "sponsors": counts.get(d, 0)} for d in next_saturdays(20)])


def create_sponsor(event):
    b = body(event)
    name = (b.get("name") or "").strip()[:100]
    email = (b.get("email") or "").strip().lower()[:120]
    phone = norm_phone(b.get("phone") or "")
    date = (b.get("date") or "").strip()
    note = (b.get("note") or "").strip()[:500]
    lang = "te" if b.get("lang") == "te" else "en"
    if not name or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or len(phone) < 11 or not date:
        return resp(400, {"error": "name, valid email, phone and date are required"})
    try:
        d = datetime.date.fromisoformat(date)
    except Exception:
        return resp(400, {"error": "bad date"})
    if d.weekday() != 5 or d < datetime.date.today():
        return resp(400, {"error": "date must be an upcoming Saturday"})
    item = {"id": uuid.uuid4().hex[:12], "name": name, "email": email, "phone": phone, "date": date,
            "note": note, "status": "pending", "created": now(), "lang": lang}
    SPONSORS.put_item(Item=item)
    nice = pretty_date(date)
    if lang == "te":
        subj = f"అన్నదాన సేవ నమోదు - {nice}"
        text = (f"నమస్కారం {name} గారు,\n\n{nice} నాడు అన్నదాన సేవకు స్పాన్సర్‌గా నమోదు చేసుకున్నందుకు ధన్యవాదాలు. "
                f"ఆలయ కార్యాలయం త్వరలో మిమ్మల్ని {phone} నంబర్‌లో సంప్రదించి వివరాలు ఖరారు చేస్తుంది.\n\n"
                f"ఓం నారాయణ ఆది నారాయణ\n{TEMPLE}\n{SITE_URL}")
        sms = f"{TEMPLE}: {nice} అన్నదాన సేవకు మీ నమోదు అందింది. ధన్యవాదాలు. ఆలయం త్వరలో సంప్రదిస్తుంది."
    else:
        subj = f"Annadanam sponsorship request received - {nice}"
        text = (f"Namaskaram {name},\n\nThank you for offering to sponsor annadanam on {nice}. "
                f"The temple office will contact you on {phone} shortly to confirm the details.\n\n"
                f"Om Narayana Adi Narayana\n{TEMPLE}\n{SITE_URL}")
        sms = f"{TEMPLE}: your annadanam sponsorship request for {nice} is received. Thank you! The temple will contact you shortly."
    html = "<p>" + text.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
    item["email_sent"] = send_email(email, subj, text, html)
    item["sms_sent"] = send_sms(phone, sms)
    SPONSORS.update_item(Key={"id": item["id"]}, UpdateExpression="SET email_sent=:e, sms_sent=:s",
                         ExpressionAttributeValues={":e": item["email_sent"], ":s": item["sms_sent"]})
    send_email(ADMIN_EMAIL, f"New annadanam sponsor: {name} for {nice}",
               f"Name: {name}\nPhone: {phone}\nEmail: {email}\nDate: {nice}\nNote: {note}\n\nReview at {SITE_URL}/admin/")
    return resp(200, {"ok": True, "id": item["id"], "email_sent": item["email_sent"], "sms_sent": item["sms_sent"]})


def list_sponsors(event):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    items = SPONSORS.scan().get("Items", [])
    items.sort(key=lambda x: (x.get("date", ""), x.get("created", "")))
    return resp(200, items)


def update_sponsor(event, sid):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    status = body(event).get("status")
    if status not in ("pending", "confirmed", "declined"):
        return resp(400, {"error": "bad status"})
    SPONSORS.update_item(Key={"id": sid}, UpdateExpression="SET #s=:s, updated=:u",
                         ExpressionAttributeNames={"#s": "status"}, ExpressionAttributeValues={":s": status, ":u": now()})
    return resp(200, {"id": sid, "status": status})


# ---------- users ----------
def list_users(event):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    out = []
    for u in cognito.list_users(UserPoolId=USER_POOL, Limit=60).get("Users", []):
        email = next((a["Value"] for a in u["Attributes"] if a["Name"] == "email"), "")
        g = cognito.admin_list_groups_for_user(UserPoolId=USER_POOL, Username=u["Username"]).get("Groups", [])
        out.append({"username": u["Username"], "email": email, "status": u["UserStatus"], "enabled": u["Enabled"],
                    "role": "admin" if any(x["GroupName"] == "admin" for x in g) else "member",
                    "created": u["UserCreateDate"]})
    return resp(200, out)


def create_user(event):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    b = body(event)
    email = (b.get("email") or "").strip().lower()
    role = "admin" if b.get("role") == "admin" else "member"
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return resp(400, {"error": "valid email required"})
    try:
        u = cognito.admin_create_user(UserPoolId=USER_POOL, Username=email, DesiredDeliveryMediums=["EMAIL"],
                                      UserAttributes=[{"Name": "email", "Value": email}, {"Name": "email_verified", "Value": "true"}])
    except cognito.exceptions.UsernameExistsException:
        return resp(409, {"error": "user already exists"})
    cognito.admin_add_user_to_group(UserPoolId=USER_POOL, Username=u["User"]["Username"], GroupName=role)
    return resp(200, {"username": u["User"]["Username"], "email": email, "role": role})


def delete_user(event, username):
    if not is_admin(event):
        return resp(403, {"error": "admin only"})
    if username == claims(event).get("cognito:username") or username == claims(event).get("email"):
        return resp(400, {"error": "cannot delete yourself"})
    cognito.admin_delete_user(UserPoolId=USER_POOL, Username=username)
    return resp(200, {"deleted": username})


# ---------- youtube ----------
YT_CHANNEL = "UCrNrbCerWLBjv_raGBn9oxQ"
_yt_cache = {"t": 0, "items": []}


def youtube_videos():
    import time, urllib.request, html
    if time.time() - _yt_cache["t"] < 3600 and _yt_cache["items"]:
        return resp(200, _yt_cache["items"])
    items = []
    try:
        req = urllib.request.Request(f"https://www.youtube.com/playlist?list=UU{YT_CHANNEL[2:]}",
                                     headers={"User-Agent": "Mozilla/5.0", "Cookie": "CONSENT=YES+1", "Accept-Language": "en"})
        page = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", "ignore")
        seen = []
        for vid in re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', page):
            if vid not in seen:
                seen.append(vid)
        titles = {}
        for m in re.finditer(r'"videoId":"([A-Za-z0-9_-]{11})".{0,3000}?"title":\{(?:"runs":\[\{"text"|"content"):"((?:[^"\\]|\\.)*)"', page):
            titles.setdefault(m.group(1), m.group(2).encode().decode("unicode_escape", "ignore"))
        items = [{"id": v, "title": html.unescape(titles.get(v, ""))} for v in seen[:24]]
        if items:
            _yt_cache.update(t=time.time(), items=items)
    except Exception as e:
        print("YOUTUBE FAILED", repr(e))
        items = _yt_cache["items"]
    return resp(200, items)


# ---------- router ----------
def handler(event, context):
    rk = event.get("routeKey", "")
    p = event.get("pathParameters") or {}
    try:
        if rk == "GET /events": return list_events()
        if rk == "POST /events": return save_event(event)
        if rk == "PUT /events/{id}": return save_event(event, p["id"])
        if rk == "DELETE /events/{id}": return delete_event(event, p["id"])
        if rk == "GET /media": return list_media()
        if rk == "GET /youtube": return youtube_videos()
        if rk == "POST /media/upload-url": return upload_url(event)
        if rk == "POST /media": return register_media(event)
        if rk == "DELETE /media/{id}": return delete_media(event, p["id"])
        if rk == "GET /sponsors/dates": return sponsor_dates()
        if rk == "POST /sponsors": return create_sponsor(event)
        if rk == "GET /sponsors": return list_sponsors(event)
        if rk == "PUT /sponsors/{id}": return update_sponsor(event, p["id"])
        if rk == "GET /users": return list_users(event)
        if rk == "POST /users": return create_user(event)
        if rk == "DELETE /users/{username}": return delete_user(event, p["username"])
        return resp(404, {"error": "no route", "route": rk})
    except Exception as e:
        print("ERROR", rk, repr(e))
        return resp(500, {"error": str(e)})
