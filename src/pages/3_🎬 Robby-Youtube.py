import os
import streamlit as st
import re
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import AnalyzeDocumentChain
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
import openai  # Import the openai module

st.set_page_config(layout="wide", page_icon="💬", page_title="Leo | Chat-Bot 🤖")

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

st.markdown(
    f"""
    <h1 style='text-align: center;'> Ask Leo to summarize YouTube video! 😁</h1>
    """,
    unsafe_allow_html=True,
)

user_api_key = utils.load_api_key()

sidebar.about()

if not user_api_key:
    layout.show_api_key_missing()
else:
    os.environ["OPENAI_API_KEY"] = "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"  # Replace with your actual OpenAI API key

    def get_youtube_id(url):
        video_id = None
        match = re.search(r"(?<=v=)[^&#]+", url)
        if match:
            video_id = match.group()
        else:
            match = re.search(r"(?<=youtu.be/)[^&#]+", url)
            if match:
                video_id = match.group()
        return video_id

    video_url = st.text_input(placeholder="Enter YouTube Video URL", label_visibility="hidden", label=" ")

    if video_url:
        video_id = get_youtube_id(video_url)

        if video_id:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=('en', 'fr', 'es', 'zh-cn', 'hi', 'ar', 'bn', 'ru', 'pt', 'sw'))
                final_string = " ".join(item['text'] for item in transcript)

                text_splitter = CharacterTextSplitter()
                chunks = text_splitter.split_text(final_string)

                summary_chain = load_summarize_chain(OpenAI(temperature=0), chain_type="map_reduce", verbose=True)
                summarize_document_chain = AnalyzeDocumentChain(combine_docs_chain=summary_chain)

                answer = summarize_document_chain.run(chunks)

                st.subheader("Summary:")
                st.write(answer)

            except TranscriptsDisabled:
                st.error("Transcripts are disabled for this video.")
            except openai.error.OpenAIError as e:
                st.error(f"OpenAI error occurred: {e}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
