from pathlib import Path
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
import pymupdf4llm


class SummaryFormatExtractor:
    def __init__(self, sample_pdf_path: str, api_key: str, model_name: str):
        self.sample_pdf_path = sample_pdf_path
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        self.md_path = Path(sample_pdf_path).with_suffix(".md")

    def convert_sample_to_markdown(self):
        print(f"Converting sample summary {self.sample_pdf_path} to Markdown...")
        md_text = pymupdf4llm.to_markdown(self.sample_pdf_path)
        self.md_path.write_text(md_text, encoding="utf-8")
        print(f"Saved Markdown to {self.md_path}")

    def extract_format_text(self) -> str:
        self.convert_sample_to_markdown()
        input_parts = [
            types.Part.from_bytes(
                data=self.md_path.read_bytes(),
                mime_type='text/plain',
            )
        ]

        prompt = (
            '''
            You are a Legal expert. Analyze the sample judgement summary provided by the user.  
            Tell me what kind of information should be extracted from any judgment under each heading of this sample.  
            Format the response clearly with headings and bullet points. No need to return JSON.
            '''
        )

        print("Extracting format description from sample summary...")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part(text=prompt),
                *input_parts
            ],
            config=GenerateContentConfig(
                temperature=0.0,
                response_modalities=["TEXT"],
            )
        )
        response_text = "".join(part.text for part in response.candidates[0].content.parts)
        print("Extracted format description:")
        print(response_text)

        return response_text
