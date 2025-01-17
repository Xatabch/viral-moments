from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from configs import config
from typing import List

def create_content(articles):
    model = ChatOpenAI(model=config.GPT_MODEL, api_key=config.OPENAI_API, temperature=0.7, max_tokens=3000)

    class Response(BaseModel):
        reels_text: str = Field(description="the text for video")
        video_description: str = Field(description="description for social networks")
        hastags: str = Field(description="hastags for social networks")
        prompts: List[str] = Field(description="list of 20 prompt for image generator flux fast for generating images for this video. The prompts should have the order like the news gone. In prompt for images add that they should be in cinematic dark style with cinematic light.")

    parser = JsonOutputParser(pydantic_object=Response)
    system_template = """
                Role: You are the professional tech blogger
                Context: You know all about viral moments and you creating the shorts video for youtube shorts, instagram reels, tiktok based on the tech news. You receive the tech articles "{articles}".
                Task: Create the text for short video with the most interesting tech news from the articles. Make it short like not more than 40 secs. Don't use any formats like emoji etc, just return the text.
                \n{format_instructions}\n
    """
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