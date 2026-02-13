#!/usr/bin/env python3
"""問題集PDFをページ単位で分割し、本文から推定した名前でリネームするツール。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter


def extract_title(text: str, fallback: str, max_len: int = 48) -> str:
    """ページ先頭の有効な行をファイル名候補として抽出する。"""
    if not text:
        return fallback

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:6]:
        candidate = re.sub(r"\s+", "_", line)
        candidate = re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龯ー_\-]", "", candidate)
        candidate = candidate.strip("_-")
        if len(candidate) >= 2:
            return candidate[:max_len]
    return fallback


def iter_pages(reader: PdfReader, start: int, end: int) -> Iterable[tuple[int, str]]:
    for i in range(start - 1, end):
        page = reader.pages[i]
        yield i + 1, page.extract_text() or ""


def split_and_rename(input_pdf: Path, output_dir: Path, start: int, end: int, prefix: str) -> None:
    reader = PdfReader(str(input_pdf))
    total = len(reader.pages)

    if start < 1 or end > total or start > end:
        raise ValueError(f"ページ範囲が不正です: start={start}, end={end}, total={total}")

    output_dir.mkdir(parents=True, exist_ok=True)

    used_names: set[str] = set()

    for page_no, text in iter_pages(reader, start, end):
        writer = PdfWriter()
        writer.add_page(reader.pages[page_no - 1])

        fallback = f"{prefix}{page_no:03d}"
        title = extract_title(text, fallback=fallback)
        file_stem = fallback if title == fallback else f"{fallback}_{title}"

        unique_stem = file_stem
        suffix = 2
        while unique_stem in used_names:
            unique_stem = f"{file_stem}_{suffix}"
            suffix += 1
        used_names.add(unique_stem)

        out_path = output_dir / f"{unique_stem}.pdf"
        with out_path.open("wb") as f:
            writer.write(f)

        print(f"page {page_no} -> {out_path.name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="問題集PDFをページごとに分割し、本文をもとに自動リネームします。"
    )
    parser.add_argument("input_pdf", type=Path, help="入力PDFファイル")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("split_output"),
        help="出力先ディレクトリ（デフォルト: split_output）",
    )
    parser.add_argument("--start", type=int, default=1, help="開始ページ（1始まり）")
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="終了ページ（省略時は最終ページ）",
    )
    parser.add_argument(
        "--prefix",
        default="q_",
        help="出力ファイル名プレフィックス（デフォルト: q_）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input_pdf.exists():
        raise FileNotFoundError(f"入力PDFが見つかりません: {args.input_pdf}")

    reader = PdfReader(str(args.input_pdf))
    end = args.end if args.end is not None else len(reader.pages)

    split_and_rename(
        input_pdf=args.input_pdf,
        output_dir=args.output_dir,
        start=args.start,
        end=end,
        prefix=args.prefix,
    )


if __name__ == "__main__":
    main()
