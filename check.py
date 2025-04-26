import streamlit as st
from PIL import Image
import numpy as np
import cv2
import hashlib
import firebase_admin
from firebase_admin import credentials, db

# ──────────────────────────────────────────────────────────────────────────────
# 1) Page config must be the first Streamlit call in this script
st.set_page_config(page_title="Check QR", layout="wide")

# 2) Lazy‐initialize Firebase with your secrets
@st.cache_resource
def init_db():
    sa = st.secrets["firebase"]
    # build service‐account dict from secrets (minus databaseURL)
    cred_dict = {k: v for k, v in sa.items() if k != "databaseURL"}
    cred = credentials.Certificate(cred_dict)
    # initialize the Admin SDK
    firebase_admin.initialize_app(cred, {"databaseURL": sa["databaseURL"]})
    # point at your “qr_checksums” node
    return db.reference("qr_checksums")

ref = init_db()
# ──────────────────────────────────────────────────────────────────────────────

def checksum_of(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def decode_qr(pil_img: Image.Image):
    # convert to OpenCV BGR
    cv_img = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(cv_img)
    return data if pts is not None and data else None

st.title("🔍 Verify QR Code")
st.write("Upload an image containing a QR code. We'll verify its checksum against our database.")

upload = st.file_uploader("Upload QR code image", type=["png", "jpg", "jpeg"])
if upload:
    img = Image.open(upload)
    st.image(img, caption="Uploaded image", use_column_width=True)

    qr_content = decode_qr(img)
    if not qr_content:
        st.warning("⚠️ No QR code detected.")
    else:
        st.write("**QR Content:**", qr_content)
        cs = checksum_of(qr_content)
        st.write("**Computed Checksum:**", cs)

        records = ref.get() or {}
        found = any(r.get("checksum") == cs for r in records.values())
        if found:
            st.success("✅ This QR is known & safe.")
        else:
            st.error("❌ QR not recognized or unsafe.")


