from pathlib import Path
from datetime import datetime
import os
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import mutagen
from mutagen.easyid3 import EasyID3
import re

class SmartRenamer:
    def __init__(self):
        pass

    def get_image_metadata(self, file_path):
        """Extract EXIF data from images"""
        try:
            image = Image.open(file_path)
            exif = image._getexif()
            if not exif:
                return None

            metadata = {}
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal" or tag == "DateTimeDigitized":
                    try:
                        # Convert to proper format
                        dt = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                        metadata['date'] = dt.strftime("%Y-%m-%d")
                        metadata['time'] = dt.strftime("%H-%M")
                    except:
                        pass

            return metadata
        except:
            return None

    def get_video_metadata(self, file_path):
        """Video metadata using pymediainfo"""
        try:
            from pymediainfo import MediaInfo
            media_info = MediaInfo.parse(file_path)
            for track in media_info.tracks:
                if track.track_type == "General":
                    recorded_date = track.recorded_date or track.encoded_date
                    if recorded_date:
                        # Clean date
                        date_str = re.search(r'\d{4}-\d{2}-\d{2}', str(recorded_date))
                        if date_str:
                            return {'date': date_str.group()}
            return None
        except:
            return None

    def get_audio_metadata(self, file_path):
        """MP3, M4A etc. metadata"""
        try:
            audio = mutagen.File(file_path, easy=True)
            if audio:
                title = audio.get('title', [''])[0]
                artist = audio.get('artist', [''])[0]
                date = audio.get('date', [''])[0]
                return {
                    'title': title,
                    'artist': artist,
                    'date': date
                }
        except:
            pass
        return None

    def get_pdf_metadata(self, file_path):
        """PDF Title & Author"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                info = reader.metadata
                if info:
                    title = info.title or ""
                    return {'title': title.strip()}
        except:
            pass
        return None

    def clean_filename(self, name: str) -> str:
        """Remove special characters"""
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = re.sub(r'\s+', '_', name.strip())
        return name[:100]  # Max length limit

    def generate_smart_name(self, file_path: str, category: str = "Others") -> str:
        """Main function - Smart Rename"""
        file = Path(file_path)
        ext = file.suffix.lower()
        original_stem = file.stem

        new_name = None

        # === Images ===
        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.tiff']:
            meta = self.get_image_metadata(file_path)
            if meta and meta.get('date'):
                new_name = f"{meta['date']}_{original_stem}"
            else:
                # Use file creation date
                ctime = datetime.fromtimestamp(file.stat().st_ctime)
                new_name = ctime.strftime("%Y-%m-%d")

        # === Videos ===
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            meta = self.get_video_metadata(file_path)
            if meta and meta.get('date'):
                new_name = meta['date']
            else:
                ctime = datetime.fromtimestamp(file.stat().st_ctime)
                new_name = ctime.strftime("%Y-%m-%d")

        # === Audio ===
        elif ext in ['.mp3', '.m4a', '.wav']:
            meta = self.get_audio_metadata(file_path)
            if meta and meta.get('title'):
                title = self.clean_filename(meta['title'])
                artist = self.clean_filename(meta.get('artist', ''))
                if artist:
                    new_name = f"{meta.get('date', '')}_{artist}_{title}"
                else:
                    new_name = f"{meta.get('date', '')}_{title}"

        # === PDF ===
        elif ext == '.pdf':
            meta = self.get_pdf_metadata(file_path)
            if meta and meta.get('title'):
                title = self.clean_filename(meta['title'])
                new_name = f"{datetime.now().strftime('%Y-%m-%d')}_{title}"

        # Fallback
        if not new_name:
            ctime = datetime.fromtimestamp(file.stat().st_ctime)
            new_name = ctime.strftime("%Y-%m-%d_%H-%M")

        # Final name
        final_name = self.clean_filename(new_name) + ext
        return final_name