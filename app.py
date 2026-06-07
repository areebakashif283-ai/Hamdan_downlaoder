import streamlit as st
import yt_dlp
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Nexus Downloader Pro", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    :root { --primary: #6366f1; --secondary: #a855f7; --bg-dark: #0f172a; --card-bg: #1e293b; --text-main: #f8fafc; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg-dark); color: var(--text-main); }
    #MainMenu, footer, header { visibility: hidden; }
    .stButton > button { background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; border-radius: 8px; padding: 10px 24px; font-weight: 600; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4); }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background-color: #0f172a; color: white; border: 1px solid #334155; border-radius: 8px; }
    h1, h2, h3 { font-weight: 800; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, var(--primary), var(--secondary)); }
</style>
""", unsafe_allow_html=True)

def ensure_dirs():
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("cookies", exist_ok=True)

def update_ytdlp():
    try:
        yt_dlp.version.update_self()
        return True, "yt-dlp updated successfully!"
    except Exception as e:
        return False, f"Update failed: {str(e)}"

def load_cookies(platform):
    cookie_file = f"cookies/{platform.lower()}_cookies.txt"
    return cookie_file if os.path.exists(cookie_file) else None

def save_cookies(platform, cookie_data):
    try:
        with open(f"cookies/{platform.lower()}_cookies.txt", "w") as f:
            f.write(cookie_data)
        return True
    except:
        return False

class DownloadProgress:
    def __init__(self, progress_bar, status_text, speed_text):
        self.progress_bar = progress_bar
        self.status_text = status_text
        self.speed_text = speed_text

    def hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)
            if total > 0:
                self.progress_bar.progress(downloaded / total)
                self.speed_text.text(f"Speed: {speed/1024/1024:.2f} MB/s" if speed else "")
        elif d['status'] == 'finished':
            self.progress_bar.progress(1.0)

def main():
    ensure_dirs()
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3665/3665931.png", width=80)
        st.title("Nexus Pro")
        st.markdown("---")
        choice = st.radio("Navigation", ["📥 Universal Downloader", "🍪 Cookie Manager", "⚙️ Settings & Updates"], label_visibility="collapsed")
        st.markdown("---")
        st.caption(f"Version: 2.0.0 | Engine: yt-dlp Latest")

    if choice == "📥 Universal Downloader":
        st.title("🌐 Universal Social Downloader")
        tab1, tab2, tab3 = st.tabs(["✨ Single Download", "📦 Bulk Download", "👤 Profile Fetcher"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col1:
                url = st.text_input("Paste Video URL", placeholder="https://...")
            with col2:
                fmt = st.selectbox("Format", ["Best Quality (Video+Audio)", "Audio Only (MP3)", "Best Video (No Audio)"])
            download_thumb = st.checkbox("Extract Thumbnail Image", value=True)
            
            if st.button("🚀 Start Download"):
                if not url:
                    st.error("Please enter a URL!")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    speed_text = st.empty()
                    ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s', 'progress_hooks': [DownloadProgress(progress_bar, status_text, speed_text).hook], 'ignoreerrors': True}
                    if fmt == "Audio Only (MP3)":
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
                    else:
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                        ydl_opts['merge_output_format'] = 'mp4'
                    for platform, keywords in [("youtube", ["youtube.com", "youtu.be"]), ("instagram", ["instagram.com"]), ("tiktok", ["tiktok.com"]), ("facebook", ["facebook.com", "fb.watch"])]:
                        if any(k in url for k in keywords):
                            ck = load_cookies(platform)
                            if ck: ydl_opts['cookiefile'] = ck
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            if download_thumb and info and info.get('thumbnail'):
                                thumb_data = requests.get(info['thumbnail']).content
                                with open(f"downloads/{info.get('title', 'video')}.jpg", 'wb') as f:
                                    f.write(thumb_data)
                                st.success("✅ Thumbnail saved!")
                            st.success("✅ Download Completed!")
                            st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with tab2:
            st.info("Paste one URL per line.")
            bulk_urls = st.text_area("Bulk URLs", height=200)
            if st.button("📥 Start Bulk Download"):
                if bulk_urls:
                    urls = [l.strip() for l in bulk_urls.split('\n') if l.strip()]
                    progress_bar = st.progress(0)
                    for i, url in enumerate(urls):
                        try:
                            with yt_dlp.YoutubeDL({'outtmpl': 'downloads/%(title)s.%(ext)s', 'quiet': True}) as ydl:
                                ydl.download([url])
                        except: pass
                        progress_bar.progress((i + 1) / len(urls))
                    st.success("🎉 All downloads finished!")

        with tab3:
            st.markdown("### 👤 Full Profile Downloader")
            profile_url = st.text_input("Profile/Channel URL", placeholder="https://www.instagram.com/username/")
            max_videos = st.slider("Max Videos to Fetch", 1, 100, 10)
            if st.button("🔍 Scan Profile"):
                if profile_url:
                    ydl_opts = {'extract_flat': True, 'playlistend': max_videos, 'quiet': True}
                    if "instagram" in profile_url:
                        ck = load_cookies("instagram")
                        if ck: ydl_opts['cookiefile'] = ck
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(profile_url, download=False)
                            entries = info.get('entries', [])
                            if entries:
                                st.success(f"Found {len(entries)} videos!")
                                cols = st.columns(3)
                                for idx, entry in enumerate(entries):
                                    with cols[idx % 3]:
                                        st.markdown(f"**{entry.get('title', 'Unknown')[:30]}**")
                                        if entry.get('thumbnail'): st.image(entry['thumbnail'])
                                        if st.button("Download", key=f"p_{idx}"):
                                            full_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                                            with yt_dlp.YoutubeDL({'outtmpl': 'downloads/%(title)s.%(ext)s'}) as ydl_dl:
                                                ydl_dl.download([full_url])
                                            st.toast("Downloaded!")
                            else:
                                st.warning("No videos found (add cookies for private profiles).")
                    except Exception as e:
                        st.error(f"Error: {e}")

    elif choice == "🍪 Cookie Manager":
        st.title("🍪 Cookie Management")
        st.markdown("**Why use cookies?** Private profiles and age-restricted videos need authentication.")
        platform = st.selectbox("Select Platform", ["Instagram", "YouTube", "TikTok", "Facebook", "Twitter/X"])
        cookie_content = st.text_area("Paste Cookies Content", height=300)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Cookies") and cookie_content:
                if save_cookies(platform, cookie_content):
                    st.success(f"Cookies for {platform} saved!")
        with col2:
            if st.button("🗑️ Delete Cookies"):
                fname = f"cookies/{platform.lower()}_cookies.txt"
                if os.path.exists(fname):
                    os.remove(fname)
                    st.success("Cookies deleted!")

    elif choice == "⚙️ Settings & Updates":
        st.title("⚙️ System Settings")
        st.subheader("🔄 Engine Update")
        if st.button("Check & Update yt-dlp"):
            with st.spinner("Updating..."):
                success, msg = update_ytdlp()
                st.success(msg) if success else st.error(msg)
        st.markdown("---")
        st.subheader("💾 Storage")
        st.code(f"Downloads folder: {os.path.abspath('downloads')}")

if __name__ == "__main__":
    main()
