MEDIA_EXTENSIONS = {
    ".vob",
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".mpeg",
    ".mpg",
    ".ts",
    ".webm",
    ".m4v",
    ".3gp",
    ".ogv",
    ".mts",
    ".m2ts",
    ".divx",
    ".asf",
    ".rm",
    ".rmvb",
    ".f4v",
}

OUTPUT_FORMATS = {
    "MP4": {
        "extension": ".mp4",
        "description": "H.264 + AAC \u2014 Most Compatible",
        "default_vcodec": "libx264",
        "default_acodec": "aac",
    },
    "MKV": {
        "extension": ".mkv",
        "description": "Matroska \u2014 Flexible Container",
        "default_vcodec": "libx264",
        "default_acodec": "aac",
    },
    "WebM": {
        "extension": ".webm",
        "description": "VP9 + Opus \u2014 Web Optimized",
        "default_vcodec": "libvpx-vp9",
        "default_acodec": "libopus",
    },
    "MOV": {
        "extension": ".mov",
        "description": "QuickTime \u2014 Apple Ecosystem",
        "default_vcodec": "libx264",
        "default_acodec": "aac",
    },
    "AVI": {
        "extension": ".avi",
        "description": "Audio Video Interleave \u2014 Legacy",
        "default_vcodec": "libx264",
        "default_acodec": "libmp3lame",
    },
    "TS": {
        "extension": ".ts",
        "description": "MPEG Transport Stream \u2014 Broadcast",
        "default_vcodec": "libx264",
        "default_acodec": "aac",
    },
}

VIDEO_CODECS = {
    "libx264": "H.264 (AVC) \u2014 Best Compatibility",
    "libx265": "H.265 (HEVC) \u2014 Better Compression",
    "libvpx-vp9": "VP9 \u2014 Open Source, Web",
    "libaom-av1": "AV1 \u2014 Best Compression, Slow",
    "mpeg4": "MPEG-4 Part 2 \u2014 Legacy",
    "copy": "Copy \u2014 No Re-encoding",
}

AUDIO_CODECS = {
    "aac": "AAC \u2014 Most Compatible",
    "libmp3lame": "MP3 \u2014 Universal",
    "libopus": "Opus \u2014 Best Quality/Size",
    "ac3": "AC3 (Dolby Digital)",
    "flac": "FLAC \u2014 Lossless",
    "copy": "Copy \u2014 No Re-encoding",
}

RESOLUTIONS = {
    "original": "Keep Original",
    "3840x2160": "4K (3840\u00d72160)",
    "2560x1440": "2K (2560\u00d71440)",
    "1920x1080": "1080p (1920\u00d71080)",
    "1280x720": "720p (1280\u00d7720)",
    "854x480": "480p (854\u00d7480)",
    "640x360": "360p (640\u00d7360)",
}

PRESETS = {
    "ultrafast": "Ultra Fast \u2014 Lowest Quality",
    "superfast": "Super Fast",
    "veryfast": "Very Fast",
    "faster": "Faster",
    "fast": "Fast",
    "medium": "Medium \u2014 Balanced (Default)",
    "slow": "Slow \u2014 Better Quality",
    "slower": "Slower",
    "veryslow": "Very Slow \u2014 Best Quality",
}

FRAME_RATES = {
    "original": "Keep Original",
    "24": "24 fps \u2014 Cinema",
    "25": "25 fps \u2014 PAL",
    "30": "30 fps \u2014 NTSC",
    "48": "48 fps",
    "60": "60 fps \u2014 Smooth",
}

AUDIO_BITRATES = {
    "auto": "Auto (Encoder Default)",
    "96k": "96 kbps \u2014 Low",
    "128k": "128 kbps \u2014 Standard",
    "192k": "192 kbps \u2014 Good",
    "256k": "256 kbps \u2014 High",
    "320k": "320 kbps \u2014 Maximum",
}
