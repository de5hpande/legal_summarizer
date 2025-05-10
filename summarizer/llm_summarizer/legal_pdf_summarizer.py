import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import pymupdf4llm
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
from summarizer.exception.exception import SummaryException

class LegalPdfSummarizer:
    # def __init__(self, pdf_path: str, api_key: str, system_prompt: str):
    #     self.pdf_path = pdf_path
    #     self.md_path = self._get_md_path(pdf_path)
    #     self.api_key = api_key
    #     self.system_prompt = system_prompt
    #     self.client = genai.Client(api_key=self.api_key)

    
    def __init__(self, pdf_path: str, api_key: str, system_prompt: str, model_name: str):
        self.pdf_path = pdf_path
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        self.md_path = self._get_md_path(pdf_path)


    def _get_md_path(self, pdf_path: str) -> str:
        return str(Path(pdf_path).with_suffix(".md"))

    def convert_pdf_to_markdown(self):
        print(f"Converting {self.pdf_path} to Markdown...")
        md_text = pymupdf4llm.to_markdown(self.pdf_path)
        Path(self.md_path).write_text(md_text, encoding="utf-8")
        print(f"Saved Markdown to {self.md_path}")

    def _prepare_input(self):
        return [
            types.Part.from_bytes(
                data=Path(self.md_path).read_bytes(),
                mime_type='text/plain',
            )
        ]

    def summarize(self) -> str:
        try:
            contents = self._prepare_input()
            print(f"Sending content from {self.pdf_path} to Gemini...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=[],
                    response_modalities=["TEXT"],
                    temperature=0.0
                )
            )
            print(f"Tokens used: {response.usage_metadata}")
            return "".join(part.text for part in response.candidates[0].content.parts)
        except Exception as e:
            raise SummaryException(sys,e)


