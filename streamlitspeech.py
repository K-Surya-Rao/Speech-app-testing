import streamlit as st
import whisper
import language_tool_python
import tempfile
import os

st.set_page_config(page_title="🎙️ Multilingual Speech Transcriber", layout="wide")
st.title("🎙️ Multilingual Speech-to-Text with Translation & Correction")

uploaded_file = st.file_uploader("📤 Upload a `.wav` file", type=["wav"])

model_size = st.selectbox("Choose Whisper model", ["tiny", "base", "medium"], index=1)
run_button = st.button("🔍 Transcribe and Process")

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

    tool = language_tool_python.LanguageToolPublicAPI('en-US')


    st.subheader("📝 Results")

    # Show each segment
    for i, (orig, trans) in enumerate(zip(orig_segments, translated_segments)):
        start = orig['start']
        end = orig['end']
        translated = trans['text'].strip()
        # At the end, after collecting all segments
        #full_corrected = language_tool_python.utils.correct(translated_text, tool.check(translated_text))
        #st.text_area("✅ Full Corrected Text", full_corrected, height=300)


        st.markdown(f"### Segment {i+1} [`{start:.2f}s - {end:.2f}s`]")        
        st.markdown(f"🌐 **Translated**: `{translated}`")
        st.markdown(f"✅ **Corrected**: `{corrected}`")
        st.divider()

    st.success("✅ All segments processed.")

    # Optional: Offer full download
    if st.download_button("📥 Download translated text", translated_text, file_name="translated.txt"):
        st.info("Download started.")
