## PDF 問題集の分割・リネーム

`split_rename_pdf.py` は、問題集PDFをページ単位で分割し、各ページの先頭テキストを使ってファイル名を自動生成します。

### セットアップ

```bash
python3 -m pip install pypdf
```

### 使い方

```bash
python3 split_rename_pdf.py 問題集.pdf -o output_dir --start 1 --end 50 --prefix q_
```

### 例

```bash
python3 split_rename_pdf.py mondai.pdf -o split_output
```

出力例:

- `q_001_第1問_関数の基本.pdf`
- `q_002_第2問_微分法.pdf`

> 注意: スキャン画像だけのPDFはテキスト抽出が弱いため、ファイル名は `q_001` のようなフォールバック名になる場合があります。
