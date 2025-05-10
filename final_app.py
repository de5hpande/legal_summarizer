import streamlit as st
import os
import tempfile
import markdown2
import pdfkit
from summarizer.summarizer_manager.summarizer_manager import SummarizerManager

# Configure wkhtmltopdf path
config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

st.set_page_config(page_title="Legal PDF Summarizer", layout="wide")

# --- Markdown to PDF Converter ---
def convert_md_to_pdf(md_content):
    html_content = markdown2.markdown(md_content)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
        temp_html.write(html_content.encode("utf-8"))
        temp_html_path = temp_html.name

    pdf_path = temp_html_path.replace(".html", ".pdf")
    pdfkit.from_file(temp_html_path, pdf_path, configuration=config)
    return pdf_path

# --- Reset Mechanism ---
def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()

# --- Sidebar ---
with st.sidebar:
    st.title("📂 Upload Files")

    model_choice = st.selectbox(
        "🧠 Choose Gemini Model",
        options=[
            "gemini-2.5-flash-preview-04-17",
            "models/gemini-2.5-pro-exp-03-25"
        ],
        index=0
    )

    uploaded_pdfs = st.file_uploader(
        "📚 Judgment PDFs",
        type="pdf",
        accept_multiple_files=True,
        help="Upload one or more PDFs to summarize"
    )

    sample_summary = st.file_uploader("📘 Sample Summary PDF (style)", type="pdf")

    if st.button("🚀 Generate Summaries"):
        st.session_state.generate = True

    if st.button("🔁 Reset App"):
        reset_app()

# --- Main UI ---
st.title("💬 Legal Judgement Summarizer")

if st.session_state.get("generate") and uploaded_pdfs:
    if "summaries" not in st.session_state:
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_path = None
            if sample_summary:
                sample_path = os.path.join(temp_dir, "sample_summary.pdf")
                with open(sample_path, "wb") as f:
                    f.write(sample_summary.read())

            pdf_paths = []
            for uploaded_file in uploaded_pdfs:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                pdf_paths.append(file_path)

            with st.spinner("Generating summaries..."):
                manager = SummarizerManager(
                    pdf_paths=pdf_paths,
                    sample_summary_path=sample_path,
                    model_name=model_choice
                )
                summaries = manager.run(return_summaries=True)

                # Generate PDFs immediately and store paths in session
                st.session_state.summaries = summaries
                st.session_state.pdf_files = {}
                for fname, summary in summaries.items():
                    pdf_path = convert_md_to_pdf(summary)
                    st.session_state.pdf_files[fname] = pdf_path

        st.rerun()  # Force refresh to display UI properly

    # Show summaries and download buttons
    for filename, summary in st.session_state.summaries.items():
        with st.chat_message("user"):
            st.markdown(f"**📄 Uploaded file:** `{filename}`")

        with st.chat_message("assistant"):
            st.markdown(f"### 📝 Summary of `{filename}`")
            st.markdown(summary, unsafe_allow_html=True)

            with open(st.session_state.pdf_files[filename], "rb") as pdf_file:
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_file,
                    file_name=filename.replace(".pdf", "_summary.pdf"),
                    mime="application/pdf",
                    key=filename + "_download"
                )
