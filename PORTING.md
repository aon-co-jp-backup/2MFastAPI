# 2MFastAPI PORTING / 再開メモ

## 日本語
**状態(2026-11-18)**: v0.1.0 を新規作成。`2mfastapi scan/convert/auto`。FastAPI は無変更で `run_mfastapi.py` を追加、Flask/Django/DRF は 2FastAPI(v0.5.2 以降)に委譲。毎晩のCI(02:47 JST)で再試験・自動リリース。easy-web.tokyo の `/2MFastAPI` と `/2MFastAPI/demo/`(ダウンロード専用)を公開。
**未了**: PyPI公開(所有者の認証)、`easy-web.tokyo` トップのバナーはサーバー(open-easy-web)の再ビルド・配備が必要(本ファイル末尾の記録を参照)。
**テスト**: `bash run-tests.sh`(WSL。`2FastAPI` を隣に置き、MFastAPI のホイールを入れると Rust 版で試験)。
**再開用メッセージ**: 「`F:\2MFastAPI\PORTING.md` を読んで、未了の続きを確認なしで開発・TEST・DEBUG・commit・pushして。チャットは日本語のみ。」

## English
**Status (2026-11-18)**: v0.1.0 created. `2mfastapi scan/convert/auto`. FastAPI projects are kept unchanged plus `run_mfastapi.py`; Flask/Django/DRF are delegated to 2FastAPI (v0.5.2+). Nightly CI (02:47 JST) re-tests and auto-releases. `/2MFastAPI` and `/2MFastAPI/demo/` (download-only) are live on easy-web.tokyo.
**Open**: PyPI (owner credentials); the easy-web.tokyo top-page banner needs a rebuild and deploy of the open-easy-web server (see the record at the end of this file).
**Tests**: `bash run-tests.sh` (WSL; keep `2FastAPI` next to this repo and install an MFastAPI wheel to test the Rust backend).
**Resume message**: "Read `F:\2MFastAPI\PORTING.md` and continue the open items without asking (develop, test, debug, commit, push). Chat in Japanese only."

## 記録 / Record (2026-11-18)
- 日本語: `aon-co-jp/2MFastAPI` 公開(v0.1.0、CI成功)。VPS: `/root/easy-web-intros/2MFastAPI/`(index・demo)、`domains.toml` に `/2MFastAPI` を追加(反映前のコピー `/root/domains.toml.before-2mfastapi-20261118`、`open-web-server` を再起動し既存ドメインの応答は前後で同一)、`/root/refresh_versions.py` に 2MFastAPI を追加(元は `.before-2mfastapi`)。version-control の走査対象 `/root/repository/` に `2MFastAPI`・`2FastAPI` をクローン。**トップページのバナーは `open-easy-web` `f205e8c`(intro_banners.rs)に追加済みだが、本番の open-easy-web サーバー(認証サーバー)の再ビルド・差し替えは未実施**。
- English: `aon-co-jp/2MFastAPI` published (v0.1.0, CI green). VPS: `/root/easy-web-intros/2MFastAPI/` (index, demo); `/2MFastAPI` added to `domains.toml` (pre-change copy `/root/domains.toml.before-2mfastapi-20261118`, `open-web-server` restarted, other domains answered the same before/after); `/root/refresh_versions.py` now lists 2MFastAPI (original kept as `.before-2mfastapi`). `2MFastAPI` and `2FastAPI` cloned under `/root/repository/` for version-control. **The top-page banner is in `open-easy-web` `f205e8c` (intro_banners.rs) but the production open-easy-web (auth) server has not been rebuilt and swapped.**
