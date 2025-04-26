import streamlit as st
import qrcode
import io
import hashlib
import requests
from datetime import datetime

# Grab RTDB URL from secrets
DB_URL = st.secrets["firebase"]["databaseURL"].rstrip("/")


def generate_qr_page():
    st.header("🔧 Generate QR Code")
    content = st.text_input("Enter content for your QR code:")
    if st.button("Generate"):
        if not content.strip():
            st.error("Please enter some content.")
            return

        # Compute checksum
        checksum = hashlib.md5(content.encode("utf-8")).hexdigest()
        # Create QR image
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Display
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        st.image(buf, caption="Generated QR Code", use_column_width=True)
        st.write("**Content:**", content)
        st.write("**Checksum:**", checksum)

        # Push to Firebase RTDB via REST
        payload = {"content": content, "checksum": checksum, "timestamp": datetime.utcnow().isoformat()}
        resp = requests.post(f"{DB_URL}/qr_checksums.json", json=payload)
        if resp.ok:
            st.success("✅ Stored to Firebase!")
        else:
            st.error(f"❌ Firebase error: {resp.text}")

        # Download button
        st.download_button(
            label="Download QR PNG",
            data=buf.getvalue(),
            file_name="qr_code.png",
            mime="image/png"
        )

