# Changelog

## [1.2.0](https://github.com/vineethkrishnan/medix/compare/medix-v1.1.0...medix-v1.2.0) (2026-03-08)


### Features

* auto-detect and install ffmpeg prerequisites interactively ([207447c](https://github.com/vineethkrishnan/medix/commit/207447c6083c3a379a6446783a14f320fcac713e))

## [1.1.0](https://github.com/vineethkrishnan/medix/compare/medix-v1.0.0...medix-v1.1.0) (2026-03-08)


### Features

* initial release of medix CLI media converter ([eecc674](https://github.com/vineethkrishnan/medix/commit/eecc6746eec827c92408f527aba3bdce3c36e3b4))

## [1.0.0](https://github.com/vineethkrishnan/medix/releases/tag/v1.0.0) (2026-03-08)

### Features

- Interactive CLI media format converter powered by FFmpeg
- Single file and batch directory conversion
- Source format filtering when directory contains mixed formats
- 6 output formats: MP4, MKV, WebM, MOV, AVI, TS
- 20+ recognized input formats including VOB, MKV, AVI, MOV, WMV, FLV, MPEG, TS, WebM
- Advanced encoding settings: video/audio codec, resolution, frame rate, CRF, preset, bitrate
- Real-time progress bars with per-file and overall tracking
- Recursive directory scanning with `-r` flag
- Custom output directory with `-o` flag
