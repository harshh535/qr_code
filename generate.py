# generate.py
import streamlit as st
import qrcode, io, hashlib, requests
from datetime import datetime

st.title("🔧 Generate QR Code")

# grab your RTDB URL from secrets
db_url = st.secrets["firebase"]["databaseURL"].rstrip("/")

def checksum_of(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def make_qr(content: str):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(content)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

content = st.text_input("Enter content for your QR code:")
if st.button("Generate"):
    if not content.strip():
        st.error("Please enter some content.")
    else:
        cs = checksum_of(content)
        img = make_qr(content)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        st.image(buf, caption="Generated QR", use_column_width=True)
        st.write("**Content:**", content)
        st.write("**Checksum:**", cs)

        # push to RTDB via its REST API
        payload = {
            "content": content,
            "checksum": cs,
            "timestamp": datetime.utcnow().isoformat()
        }
        resp = requests.post(f"{db_url}/qr_checksums.json", json=payload)
        if resp.ok:
            st.success("✔️ Stored to Firebase!")
        else:
            st.error(f"❌ Failed: {resp.text}")

        st.download_button(
            "Download QR as PNG",
            data=buf.getvalue(),
            file_name="qr_code.png",
            mime="image/png"
        )
