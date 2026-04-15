# Changelog

## [1.3.1](https://github.com/vineethkrishnan/medix/compare/medix-v1.3.0...medix-v1.3.1) (2026-04-15)


### Bug Fixes

* **ci:** hardcode --branch=main so deploys land on production URL ([ed2e95e](https://github.com/vineethkrishnan/medix/commit/ed2e95ee00f4505a0188d8d137df58773f64dfa7))


### Documentation

* astro starlight site + cloudflare pages deploy ([#5](https://github.com/vineethkrishnan/medix/issues/5)) ([0f71eb0](https://github.com/vineethkrishnan/medix/commit/0f71eb033df110d3b5e9e53b1a65a0061cfafd51))
* use correct medix-5bc.pages.dev URL everywhere ([a3a9054](https://github.com/vineethkrishnan/medix/commit/a3a90544bf113f97e8b1fac3ec097434405eeba5))

## [1.3.0](https://github.com/vineethkrishnan/medix/compare/medix-v1.2.1...medix-v1.3.0) (2026-03-08)


### Features

* add --dry-run flag and comprehensive test suite (119 tests) ([a24b6e7](https://github.com/vineethkrishnan/medix/commit/a24b6e772e5d8aa3871033bf71dfa422f2a6f776))


### Documentation

* update CONTRIBUTING.md with test suite, ruff, and dry-run guidance ([9ecad6a](https://github.com/vineethkrishnan/medix/commit/9ecad6a554de1cc11f21d206357e4aa08e8b066c))

## [1.2.1](https://github.com/vineethkrishnan/medix/compare/medix-v1.2.0...medix-v1.2.1) (2026-03-08)


### Documentation

* update README with demo screenshots, PyPI install, and auto-install docs ([269fd5d](https://github.com/vineethkrishnan/medix/commit/269fd5dc0b58339b41e60529de1dfd1e66696718))

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
