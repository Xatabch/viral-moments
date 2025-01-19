from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from configs import config
from typing import List

def get_prompts(segments, frames):
    model = ChatOpenAI(model=config.GPT_MODEL, api_key=config.OPENAI_API, temperature=0.7, max_tokens=3000)

    class Response(BaseModel):
        prompts: List[str] = Field(description=f"list of prompts. It should have minimum {frames} prompts")

    parser = JsonOutputParser(pydantic_object=Response)
    system_template = """
                Role: You're an expert at coming up with prompt for images for generative models.
                Context: You receive as input words that contain timestamps of their pronunciation "{segments}".
                Task: 1. Highlight the themes of the text
                      2. For each topic, select the required number of prompt images, taking into account that one image lasts 2 seconds and the transition between images lasts 0.1 seconds
                      The output should be a list of prompts in the required sequence according to the time of pronunciation of the text topic
                \n{format_instructions}\n
    """
    prompt = PromptTemplate(
                template=system_template,
                input_variables=["segments"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    result = chain.invoke({
        "segments": segments,
    })

    return result