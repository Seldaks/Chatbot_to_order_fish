from .lang_tools import *
from .config import Config
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langchain.memory import SQLChatMessageHistory
# from langchain.memory.chat_message_histories.sql import BaseMessageConverter, DefaultMessageConverter
from langchain.chains.conversation.memory import ConversationBufferWindowMemory                                               
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import convert_to_openai_function


class Agent:
    @staticmethod


    def create_agent(session_id):

        Config.session_id=session_id

        tools = [instock, add_to_cart, setCustomerForOrder, setOrderShippingAddress, getAllEligibleShippingMethods, setShippingMethodToOrder,transitionOrderToCompletion]
        functions = [convert_to_openai_function(f) for f in tools]
        model = ChatOpenAI(model_name="gpt-4",temperature=0).bind(functions=functions)
    
        prompt = ChatPromptTemplate.from_messages([("system", """
                                                    You are OrderBot, an automated service for collecting restaurant orders. Follow these instructions precisely:
                                                    1. **Greeting and Order Collection**:
                                                    - Start by greeting the customer.
                                                    - Collect the order, ensuring you only take orders from the provided data.
                                                    - Ask if the customer wants to add anything else.
                                                    - Clarify all options, extras, and sizes uniquely.
                                                    - Invoke the tools according to the response from the customer.
                                                    - For items with combinations, show the full name without using the term "combo".

                                                    2. **Availability and Quantity**:
                                                    - NB: Always ask for the "quantity" or "No:of Itemsor fish" before adding to cart.
                                                    - Accurately check product availability and show only available items.
                                                    - NB: Only show the available items or fishes when instock tool is invoked,only take 'stockLevel': 'IN_STOCK'.
                                                    - If a specific quantity requested is not available, suggest the available quantity.

                                                    3. **Order Summary and Placement**:
                                                    - Summarize the entire order before proceeding.
                                                    - Place the order in the cart with the correct product variant ID.
                                                    - first cart_query should be invoked inside the add_to_cart tool and the data recieved from this should be used for add_item_mutation query.
                                                    - After summarizing, confirm the order with the customer.

                                                    4. **Customer and Shipping Details**:
                                                    - Always collect customer details: first name, last name, email address, and phone number.
                                                    - Set customer details using setCustomerForOrder tool. 
                                                    - Always collect shipping address details: street line and postal code.
                                                    - Set shipping address using setOrderShippingAddress tool.
                                                    - Retrieve and display eligible shipping methods to the customer using getAllEligibleShippingMethods tools.
                                                    - Set the shipping method using the selected shipping_method_id using setShippingMethodToOrder tools.
                                                    - strictly collect customer details and shipping address under any condition.

                                                    5. **Order Confirmation and Payment**:
                                                    - Confirm the order details with the customer.
                                                    - Inform the customer that only cash on delivery is available.
                                                    - If the customer agrees, invoke transitionOrderToCompletion.

                                                    6. **Final Steps**:
                                                    - Ask if the order is for pickup or delivery.
                                                    - If for delivery, confirm the address.
                                                    - Ensure all details (items, address, payment method) are accurate.
                                                    - Collect the payment.
                                                    - Show the total cost as value itself 

                                                    7. **Additional Information**:
                                                    - Provide details on available fishes if requested.
                                                    - Do not assume any customer details unless provided. always ask their details
                                                    - NB: invoke every tool that is provided. do not skip any.
                                                    -you have a great knowledge about fishes,their features.you are an expert in that field.
                                                    Respond in a short, conversational, and friendly style.
                                                    
                                                    """),
                                                MessagesPlaceholder(variable_name="chat_history"), ("user", "{input}"),
                                                MessagesPlaceholder(variable_name="agent_scratchpad")])
        
        
        # connection_string = "mysql+pymysql://root:Tech2022@localhost:3306/chatbotbase"
        chat_memory = SQLChatMessageHistory(
                # session ID should be user-specific, it isolates sessions
                
                session_id=session_id,
                # MyScale SaaS is using HTTPS connection
                connection_string='postgresql://postgres:$TT_Postgres_^2023$@tt-postgres-instance.c894lrepeoma.ap-south-1.rds.amazonaws.com:5432/chatbot-database',
                table_name="message_store"
                # Here we customized the message converter and table schema
                # custom_message_converter=DefaultClickhouseMessageConverter(name)
                )
        
        memory = ConversationBufferWindowMemory(
        
                chat_memory=chat_memory,
                memory_key="chat_history",
                k=7,
                return_messages=True
            )

        chain = RunnablePassthrough.assign(agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
                                        ) | prompt | model | OpenAIFunctionsAgentOutputParser()
        
        agent_executor = AgentExecutor(agent=chain, tools=tools, memory=memory, verbose=True)
        
        return agent_executor






















                        


