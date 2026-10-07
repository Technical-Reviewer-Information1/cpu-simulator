# CPUにおける計算の仕組み

『大学入学共通テスト「情報Ⅰ」対策問題集』（技術評論社, ISBN 978-4-297-15084-6）pp.178-180 連動Webアプリ。

**公開URL**: https://technical-reviewer-information1.github.io/cpu-simulator/

本文の仮想コンピュータAをそのまま動かせます。1命令ずつ実行して、プログラムカウンタとレジスタの値の変化を追いましょう。

## 技術

静的な HTML / CSS / JavaScript のみで動作します。ビルド不要・外部CDN不使用・サーバ通信なし。
GitHub Pages で配信しており、Python や Streamlit は不要です。スマートフォン／タブレット／PC に対応。

```
index.html
css/style.css   全アプリ共通スタイル
css/app.css     このアプリ固有のスタイル
js/app.js       画面制御
```

`streamlit_app.py` は旧版（Streamlit Community Cloud 用）です。

---
Created by Dit-Lab.(Daiki ITO) / Supported by Tomoaki ATSUMI
