# HYC sailing results

Bits and pieces relating to https://www.hyc.ie/results

The results-site capture and its automation moved to
[`sailscoring/hyc-archive`](https://github.com/sailscoring/hyc-archive)
(2026-07): the daily FTP-site backup (`backups/results.hyc.ie/` →
`sources/reshyc/results.hyc.ie/`), the admin-DB catalogue backup
(`backups/admin/`), the prize-winner summary PDFs (`backups/summaries/`),
the `scripts/admin/` scrapers, and the backup workflows. This repo's
history preserves the day-by-day capture record up to the handover.

What remains here: the local Sailwave-under-wine setup (`Makefile`), the
2022 Autumn League page-chunking tooling (`scripts/chunk.py`,
`data/chunk/`), `scripts/ftp-upload.sh`, and the `transftp/` AWS bits.
