import streamlit as st
import qrcode
import io
import hashlib
import requests
from datetime import datetime

DB_URL = st.secrets["firebase"]["databaseURL"].rstrip("/")

def is_malicious(content):
    resp = requests.get(f"{DB_URL}/malicious.json")
    if resp.ok and resp.json():
        data = resp.json()
        return any(item.get("content") == content for item in data.values())
    return False

def generate_qr_page():
    st.header("🔧 Generate QR Code")
    content = st.text_input("Enter content for your QR code:")
    if st.button("Generate"):
        if not content.strip():
            st.error("Please enter some content.")
            return

        if is_malicious(content):
            st.error("🚫 This is a **malicious link**. QR generation blocked.")
            return

        checksum = hashlib.md5(content.encode("utf-8")).hexdigest()

        # Create QR
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to buffer
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # Show
        st.image(buf, caption="Generated QR Code", use_column_width=True)
        st.write("**Content:**", content)
        st.write("**Checksum:**", checksum)

        # Save to Firebase
        payload = {
            "content": content,
            "checksum": checksum,
            "timestamp": datetime.utcnow().isoformat()
        }
        resp = requests.post(f"{DB_URL}/qr_checksums.json", json=payload)
        if resp.ok:
            st.success("✅ Stored to Firebase!")
        else:
            st.error(f"Firebase error: {resp.status_code} {resp.text}")

        # Download option
        st.download_button("📥 Download QR", data=buf.getvalue(), file_name="qr.png", mime="image/png")

