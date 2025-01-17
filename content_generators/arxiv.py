from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import PyPDF2
from configs import config
from typing import List

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF-файла."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def create_content():
    pdf_text = extract_text_from_pdf(config.PDF_FILE_NAME)

    model = ChatOpenAI(model=config.GPT_MODEL, api_key=config.OPENAI_API, temperature=0.7, max_tokens=3000)

    class Response(BaseModel):
        reels_text: str = Field(description="the text for video")
        video_description: str = Field(description="description for social networks")
        hastags: str = Field(description="hastags for social networks")
        prompts: List[str] = Field(description="list of 5 prompt for stable diffusion image generator for generating images for this video")

    parser = JsonOutputParser(pydantic_object=Response)
    system_template = """
                Role: You are the professional science popular blogger
                Context: You creating the shorts video for youtube shorts, instagram reels, tiktok. You receive the science PDF file "{pdf_text}".
                Task: Create the text for short video explaining the concepts in the PDF file with science popular style. Don't use any formats like emoji etc, just return the text
                \n{format_instructions}\n
    """
    prompt = PromptTemplate(
                template=system_template,
                input_variables=["pdf_text"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    result = chain.invoke({
        "pdf_text": pdf_text[:2000],
    })

    return result