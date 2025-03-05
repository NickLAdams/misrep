from autogen import AssistantAgent, UserProxyAgent
from typing import Literal

from pydantic import BaseModel, Field
from typing_extensions import Annotated
from dotenv import load_dotenv
import autogen
import os

CurrencySymbol = Literal["USD", "EUR"]

def calculate_price_of_insurance(
        age: Annotated[int, 'Age of customer'],
        smoker_status: Annotated[bool, 'Boolean value of if customer is a smoker'],
        cover_amount: Annotated[int, 'GBP amount of cover'],
        term: Annotated[int, 'The duration of the policy in years']
    ) -> Annotated[float, 'The GBP price of the policy per month']:
    
    return cover_amount * (age/100) * (2 if smoker_status else 1) / (term * 12)

def set_up_chatbot(model: str):
    config_list = [
        {
            "model": model,
            "api_key": os.getenv('OPENAI_API_KEY'),
        }
    ]

    llm_config = {
        "config_list": config_list,
        "timeout": 120,
    }

    chatbot = autogen.AssistantAgent(
        name="pricing assistant",
        system_message="You are a pricing assistant, you will help a customer that is searching for a life insurance policy and give them a price for their cover. In order to do that you must ask the customer for their age, smoker status, amount of cover and the length of the cover",
        llm_config=llm_config,
    )

    user_proxy = autogen.UserProxyAgent(
        chatbot
    )

    return chatbot, user_proxy


def main(model:str):

    chatbot, user_proxy = set_up_chatbot(model=model)

    autogen.agentchat.register_function(
        calculate_price_of_insurance,
        caller=chatbot,
        executor=user_proxy,
        description="Calculator for monthly price of life insurance",
    )

    user_proxy.initiate_chat(
        chatbot,
        message="How much would my life insurance cost?",
    )


if __name__ == '__main__':

    load_dotenv()

    main("gpt-4o-mini")