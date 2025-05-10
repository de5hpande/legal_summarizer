import os
from dotenv import load_dotenv
from summarizer.llm_summarizer.legal_pdf_summarizer import LegalPdfSummarizer
from summarizer.summary_format_extractor.summary_extractor_string import SummaryFormatExtractor

# class SummarizerManager:
#     def __init__(self, pdf_paths: list[str]):
#         load_dotenv()
#         self.api_key = os.getenv("GEMINI_API_KEY")
#         self.system_prompt = os.getenv("SYSTEM_PROMPT")
#         self.pdf_paths = pdf_paths

#     def run(self):
#         for pdf in self.pdf_paths:
#             print(f"\n=== Processing: {pdf} ===")
#             summarizer = LegalPdfSummarizer(pdf, self.api_key, self.system_prompt)
#             summarizer.convert_pdf_to_markdown()
#             summary = summarizer.summarize()
#             print(f"\n--- Summary for {pdf} ---\n{summary}\n")


# if __name__ == "__main__":
#     pdf_list = [
#         "TVF-Fund-Ltd.pdf",
#         "TVF-Fund-Ltd.pdf"
#     ]
#     manager = SummarizerManager(pdf_list)
#     manager.run()

class SummarizerManager:
    # def __init__(self, pdf_paths: list[str], sample_summary_path: str = None):
    #     load_dotenv()
    #     self.api_key = os.getenv("GEMINI_API_KEY")
    #     self.system_prompt = os.getenv("SYSTEM_PROMPT")
    #     self.pdf_paths = pdf_paths
    #     self.sample_summary_path = sample_summary_path
    #     self.format_json = None

    #     if sample_summary_path:
    #         extractor = SummaryFormatExtractor(sample_summary_path, self.api_key)
    #         self.format_json = extractor.extract_format_json()

    def __init__(self, pdf_paths: list[str], sample_summary_path: str = None, model_name: str = "gemini-2.5-flash-preview-04-17"):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.system_prompt = os.getenv("SYSTEM_PROMPT")
        self.pdf_paths = pdf_paths
        self.sample_summary_path = sample_summary_path
        self.model_name = model_name
        self.string_format = None

        if sample_summary_path:
            extractor = SummaryFormatExtractor(sample_summary_path, self.api_key, self.model_name)
            self.string_format = extractor.extract_format_text()


    # def run(self):
    #     for pdf in self.pdf_paths:
    #         print(f"\n=== Processing: {pdf} ===")
    #         summarizer = LegalPdfSummarizer(pdf, self.api_key, self._build_prompt())
    #         summarizer.convert_pdf_to_markdown()
    #         summary = summarizer.summarize()
    #         print(f"\n--- Summary for {pdf} ---\n{summary}\n")

    def run(self, return_summaries=False):
        results = {}
        for pdf in self.pdf_paths:
            print(f"\n=== Processing: {pdf} ===")
            summarizer = LegalPdfSummarizer(pdf, self.api_key, self._build_prompt(),self.model_name)
            summarizer.convert_pdf_to_markdown()
            summary = summarizer.summarize()
            if return_summaries:
                results[os.path.basename(pdf)] = summary
            else:
                print(f"\n--- Summary for {pdf} ---\n{summary}\n")
        return results if return_summaries else None

    def _build_prompt(self) -> str:
        if self.string_format:
            return (
                f"You are a Legal Assistant. Use the following format guide extracted from a sample summary:\n\n"
                f"{self.string_format}\n\n"
                f"Strictly follow this format when summarizing the judgment."
            )
        return self.system_prompt

# if __name__ == "__main__":
#     pdf_list = [
#         "vodafone.PDF",
#          ]
#     sample_path = "pwc.pdf"
#     manager = SummarizerManager(pdf_list, sample_summary_path=sample_path)
#     manager.run()
