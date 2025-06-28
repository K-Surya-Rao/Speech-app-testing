import streamlit as st
import whisper
import language_tool_python
from indic_transliteration.sanscript import transliterate, sanscript
import tempfile
import os

st.set_page_config(page_title="🎙️ Multilingual Speech Transcriber", layout="wide")
st.title("🎙️ Multilingual Speech-to-Text with Translation & Correction")

uploaded_file = st.file_uploader("📤 Upload a `.wav` file", type=["wav"])

model_size = st.selectbox("Choose Whisper model", ["tiny", "base"], index=1)
run_button = st.button("🔍 Transcribe and Process")

def get_script_code(lang_code):
    return {
        "hi": sanscript.DEVANAGARI,
        "te": sanscript.TELUGU,
        "ta": sanscript.TAMIL,
        "kn": sanscript.KANNADA,
        "ml": sanscript.MALAYALAM,
        "gu": sanscript.GUJARATI,
        "bn": sanscript.BENGALI,
        "pa": sanscript.GURMUKHI,
        "mr": sanscript.DEVANAGARI,
        "or": sanscript.ORIYA,
        "en": None
    }.get(lang_code, None)

def transliterate_text(text, lang_code):
    script = get_script_code(lang_code)
    return transliterate(text, script, sanscript.ITRANS) if script else text

if uploaded_file and run_button:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        audio_path = temp_file.name

    st.info("⏳ Loading Whisper model...")
    model = whisper.load_model(model_size)

    # Transcribe original
    st.success("🔠 Transcribing original language...")
    original_result = model.transcribe(audio_path, task="transcribe")
    original_lang = original_result["language"]
    orig_segments = original_result.get("segments", [])

    # Translate to English
    st.success("🌍 Translating to English...")
    translated_result = model.transcribe(audio_path, task="translate")
    translated_segments = translated_result.get("segments", [])
    translated_text = translated_result["text"]

    tool = language_tool_python.LanguageTool('en-US')
    st.subheader("📝 Results")

    # Show each segment
    for i, (orig, trans) in enumerate(zip(orig_segments, translated_segments)):
        start = orig['start']
        end = orig['end']
        original = orig['text'].strip()
        translated = trans['text'].strip()
        corrected = language_tool_python.utils.correct(translated, tool.check(translated))
        romanized = transliterate_text(original, original_lang)

        st.markdown(f"### Segment {i+1} [`{start:.2f}s - {end:.2f}s`]")
        st.markdown(f"🗣️ **Romanized**: `{romanized}`")
        st.markdown(f"🌐 **Translated**: `{translated}`")
        st.markdown(f"✅ **Corrected**: `{corrected}`")
        st.divider()

    st.success("✅ All segments processed.")

    # Optional: Offer full download
    if st.download_button("📥 Download translated text", translated_text, file_name="translated.txt"):
        st.info("Download started.")
