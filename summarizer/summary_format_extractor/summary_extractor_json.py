from pathlib import Path
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
import pymupdf4llm

class SummaryFormatExtractor:
    # def __init__(self, sample_pdf_path: str, api_key: str):
    #     self.sample_pdf_path = sample_pdf_path
    #     self.api_key = api_key
    #     self.client = genai.Client(api_key=self.api_key)
    #     self.md_path = Path(sample_pdf_path).with_suffix(".md")

    
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

    def extract_format_json(self) -> dict:
        self.convert_sample_to_markdown()
        input_parts = [
            types.Part.from_bytes(
                data=self.md_path.read_bytes(),
                mime_type='text/plain',
            )
        ]

        prompt = (
            
            '''
           You are a Legal expert. Tell me information to be extracted from any judgement per heading of the sample judgement summary provided by user.  
           Strictly return a JSON where each key is the heading of the sample judgement summary and value describes what kind of information must be included under that heading from any judgement.  
           All answers must be in bullet point format.

            '''
        )

        print("Extracting format from sample summary...")
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
        json_response = "".join(part.text for part in response.candidates[0].content.parts)
        print("Extracted format JSON:")
        print(json_response)
        return json_response
