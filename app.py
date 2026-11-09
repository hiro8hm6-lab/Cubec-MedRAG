import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

# 環境変数の読み込み
load_dotenv()
client = genai.Client()

# ページ設定
st.set_page_config(
    page_title="Cubec-MedRAG: Clinical Medical RAG",
    page_icon="🩺",
    layout="wide"
)

# タイトルとバックグラウンドの説明（医療者視点をアピール）
st.title("🩺 Cubec-MedRAG: 医療・放射線論文クロスアナリティクス・プラットフォーム")
st.markdown("""
**開発者**: 現役医学部生 / 元・理学療法士  
**概要**: 複数の医学・放射線論文PDFをマルチモーダルに横断解析し、
単なるモデル精度（AUC等）だけでなく、**「臨床実装に向けた障壁」「ワークフロー統合」「ヒューマン・イン・ザ・ループ」**の観点から構造化比較するAIシステム。
""")

st.markdown("---")

# サイドバー：PDFフォルダからの自動検出
st.sidebar.header("📁 1. 論文データ選択 (PDFフォルダ)")

pdf_dir = "PDF"
available_pdfs = []
if os.path.exists(pdf_dir):
    available_pdfs = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

if available_pdfs:
    # デフォルトで全ファイルを選択状態にする
    selected_pdfs = st.sidebar.multiselect(
        "分析対象とする論文にチェックを入れてください:",
        available_pdfs,
        default=available_pdfs
    )
else:
    st.sidebar.warning("⚠️ 'PDF' フォルダ内にPDFファイルが見つかりません。")
    selected_pdfs = []

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. 分析パラメータ")
analysis_mode = st.sidebar.selectbox(
    "分析の視点を選択",
    [
        "包括的横断比較（臨床課題・モダリティ・性能・障壁）",
        "臨床実装リスク＆ワークフロー評価特化",
        "エビデンスの限界とバイアス検証"
    ]
)

# メイン画面：プロンプトのカスタマイズ
default_prompt = (
    "これら複数の医療・放射線分野の論文を横断的に分析し、"
    "医療従事者（臨床医・放射線科医・医学物理士）の視点から以下の4項目について比較・構造化してまとめてください。\n\n"
    "1. 各論文の主要テーマと解決しようとしている臨床課題の比較\n"
    "2. 使用されたモダリティやデータ（規模・特性）の違い\n"
    "3. AIモデルの性能・評価結果における共通点と相違点（AIの得意・不得意の質的特性）\n"
    "4. 臨床実装（Clinical Implementation）に向けた共通の障壁（ワークフロー統合、自動化バイアス、前向きエビデンスの不足）"
)

query_text = st.text_area(
    "💡 AIへの分析指示（プロンプトの調整が可能です）:",
    default_prompt,
    height=120
)

# 実行ボタン
if st.button("🚀 選択した論文の横断分析を実行する", type="primary"):
    if not selected_pdfs:
        st.warning("⚠️ サイドバーから分析対象の論文を少なくとも1つ選択してください。")
    elif not query_text:
        st.warning("⚠️ 分析指示を入力してください。")
    else:
        with st.spinner("🤖 サーバー混雑を自動回避しながら、Gemini APIがマルチモーダル解析中..."):
            try:
                file_objs = []
                # PDFフォルダ内の選択されたファイルをGeminiにアップロード
                for pdf_name in selected_pdfs:
                    pdf_path = os.path.join(pdf_dir, pdf_name)
                    if os.path.exists(pdf_path):
                        file_obj = client.files.upload(file=pdf_path)
                        file_objs.append(file_obj)

                # --- 自動リトライ付きのGemini呼び出し ---
                max_retries = 3
                response = None
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=[*file_objs, f"【分析モード: {analysis_mode}】\n\n{query_text}"]
                        )
                        break
                    except ServerError as se:
                        if attempt < max_retries - 1:
                            time.sleep(5)
                        else:
                            raise se

                # 結果の表示
                st.success("✅ 横断分析レポートの生成が完了しました！")
                st.markdown("---")
                st.markdown("### 📊 臨床・技術 横断比較分析レポート")
                st.markdown(response.text)

                # --- レポートのダウンロード（エクスポート） ---
                st.markdown("---")
                st.subheader("💾 レポートのエクスポート")
                st.markdown("生成された分析結果をMarkdownファイルとしてダウンロードできます。抄読会や研究ノートにご活用ください。")
                
                st.download_button(
                    label="📥 比較レポートをダウンロード (.md)",
                    data=response.text,
                    file_name="Cubec-MedRAG_Cross_Analysis_Report.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"❌ エラーが発生しました（サーバーが混雑している可能性があります。少し時間を置いて再度お試しください）: {e}")