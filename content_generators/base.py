from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from configs import config
from typing import List

def create_content(articles, prompt):
    model = ChatOpenAI(model=config.GPT_MODEL, api_key=config.OPENAI_API, temperature=0.7, max_tokens=3000)

    class Response(BaseModel):
        reels_text: str = Field(description="the text for the video")
        video_description: str = Field(description="description for the social networks")
        hashtags: str = Field(description="hashtags for social networks")

    parser = JsonOutputParser(pydantic_object=Response)
    system_template = prompt
    prompt = PromptTemplate(
                template=system_template,
                input_variables=["articles"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    result = chain.invoke({
        "articles": articles,
    })

    return result