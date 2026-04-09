import streamlit as st
import yt_dlp
import os
import tempfile

# Page Branding
st.set_page_config(page_title="Hamdan Downloader Pro", page_icon="🚀", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #3b82f6; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Hamdan Downloader Pro")
st.write("Duniya ke kisi bhi social platform se video download karein.")

# Sidebar for Support
with st.sidebar:
    st.header("Admin Panel")
    st.write("Developed by: **Hamdan**")
    st.write("---")
    st.write("Contact for Custom Tools:")
    st.link_button("WhatsApp Support", "https://wa.me/923032825926")

# URL Input
url = st.text_input("Paste Link Here (YouTube, TikTok, FB, IG):", placeholder="https://...")

if st.button("PROCESS VIDEO"):
    if url:
        try:
            with st.spinner("Analyzing Video... Please wait"):
                # Temporary folder for download
                with tempfile.TemporaryDirectory() as tmp_dir:
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                        'quiet': True,
                        'no_warnings': True,
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        # Show Video Preview
                        st.success(f"Video Found: {info['title']}")
                        
                        # Provide Download Button
                        with open(filename, "rb") as f:
                            btn = st.download_button(
                                label="📥 CLICK HERE TO SAVE TO DEVICE",
                                data=f,
                                file_name=os.path.basename(filename),
                                mime="video/mp4"
                            )
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Pehle koi link paste karein!")
