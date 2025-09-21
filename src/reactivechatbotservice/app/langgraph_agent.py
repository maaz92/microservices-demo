import os
import sys
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from google.protobuf.json_format import MessageToJson
import demo_pb2
import grpc_clients
import streamlit as st

memory = InMemorySaver()

try:
    api_key = os.environ["GEMINI_API_KEY"]
except KeyError:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
try:
    ONLINE_BOUTIQUE_BASE_URL = os.environ["ONLINE_BOUTIQUE_BASE_URL"]
except KeyError:
    print("Error: ONLINE_BOUTIQUE_BASE_URL environment variable is not set.")
    sys.exit(1)

@tool
def get_cart_items(user_id: str) -> demo_pb2.Cart:
    """
    Gets the items in the cart.

    Args:
        user_id (str): The user_id

    Returns:
        demo_pb2.Cart the user_id and items(a list of cart items)
    """
    return grpc_clients.cart_service_client.get_cart(user_id=user_id)

@tool
def add_item_to_cart(user_id: str, product_id: str, quantity: int) -> None:
    """
    Adds given quantity of products to the cart.

    Args:
        user_id (str): The user_id
        product_id (str): The product_id
        quantity (int): The quantity of product
    """
    grpc_clients.cart_service_client.add_item_to_cart(user_id=user_id, product_id=product_id, quantity=quantity)

@tool
def empty_cart(user_id) -> None:
    """
    Empties the cart for the user.
    Args:
        user_id (str): The user_id
    """
    grpc_clients.cart_service_client.empty_cart(user_id=user_id)

@tool
def list_product() -> demo_pb2.ListProductsResponse:
    """
    Lists all the products in the catalog
    Args: No arguments
    Returns:
        demo_pb2.ListProductsResponse products(a list of products)
    """
    list_product_response =  grpc_clients.product_catalog_service_client.list_product()
    for product in list_product_response.products:
        product.picture = get_product_picture_url(picture=product.picture)
    return list_product_response

@tool
def get_product(id: str) -> demo_pb2.Product:
    """
    Gets a product for a specific id from the catalog
    Args:
        id (str): The id of the product
    Returns:
        demo_pb2.Product the product
    """
    product = grpc_clients.product_catalog_service_client.get_product(id=id)
    product.picture = get_product_picture_url(picture=product.picture)
    return product

@tool
def search_product(query: str) -> demo_pb2.SearchProductsResponse:
    """
    Gets a product for a specific id from the catalog
    Args:
        id (str): The id of the product
    Returns:
        demo_pb2.SearchProductsResponse results(a list of products)
    """
    search_product_response = grpc_clients.product_catalog_service_client.search_product(query=query)
    for product in search_product_response.results:
        product.picture = get_product_picture_url(picture=product.picture)
    return search_product_response

def get_product_picture_url(picture: str):
    """
    Gets the product picture url
    Args: picture (str)
    Returns:
        str: The product picture url
    """
    return f"{ONLINE_BOUTIQUE_BASE_URL}{picture}"

@tool
def place_order(user_id: str) -> demo_pb2.PlaceOrderResponse:
    """
    Places order for the user
    Args:
        user_id (str): The user_id string
    Returns:
        demo_pb2.PlaceOrderResponse: the order details
    """
    return grpc_clients.checkout_service_client.place_order(user_id=user_id)

@tool
def get_supported_currencies() -> demo_pb2.GetSupportedCurrenciesResponse:
    """
    Gets the supported currencies
    Args: No arguments
    Returns:
        demo_pb2.GetSupportedCurrenciesResponse: the list of supported currencies
    """
    return grpc_clients.currency_service_client.get_supported_currencies()

@tool
def list_recommendations(user_id: str, product_ids: list[str]) -> demo_pb2.ListRecommendationsResponse:
    """
    Lists recommendations
    Args:
        user_id (str): The list of product ids in the cart
        product_ids (list[str]): The list of product ids in the cart
    Returns:
        demo_pb2.ListRecommendationsResponse: the list of product_ids
    """
    return grpc_clients.recommendation_service_client.list_recommendations(user_id=user_id, product_ids=product_ids)

@tool
def get_shipping_quote(product_ids: list[str], quantities: list[int]):
    """
    Gets the quote for shipping
    Args:
        product_ids (list[str]): The list of product ids in the cart
        quantities (list[int]): The list of product ids in the cart
    Returns:
        demo_pb2.GetQuoteResponse: the quote for shipping the items. The total amount = units + nanos/1e9
    """
    return grpc_clients.shipping_service_client.get_quote(product_ids=product_ids, quantities=quantities)

@tool
def get_ads():
    """
    Gets the ads
    Args: No Arguments
    Returns:
        demo_pb2.AdResponse: A list of ads
    """
    return grpc_clients.ad_service_client.get_ads()

@tool
def get_product_url(product_id: str) -> str:
    """
    Gets the product url
    Args: product_id (str)
    Returns:
        str: The product url
    """
    return f"{ONLINE_BOUTIQUE_BASE_URL}/product/{product_id}"


tools = [get_cart_items, add_item_to_cart, empty_cart, list_product, get_product,search_product,
         place_order, get_supported_currencies, list_recommendations, get_shipping_quote,
         get_ads, get_product_url]

# Create LLM class
llm = ChatGoogleGenerativeAI(
    model= "gemini-2.5-flash",
    temperature=0.4,
    max_retries=2,
    google_api_key=api_key,
)

# Bind tools to the model
llm_with_tools = llm.bind_tools(tools)

# Nodes
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="""You are Rachel an online shopping assistant for Online Boutique. You can assist by doing only the following two types of tasks:
                        1. Add items to the cart.
                        2. Show the cart: product name, picture, price and the shipping quote for the whole cart, total amount including the shipping quote. Everything in a tabular format.
                        3. Empty the cart: After emptying the cart show ads to him. Show product name, picture, description, url and price.
                        4. List products in the shop. Show the product name, picture, description, url and price.
                        5. Search for products in the shop. Show the product name, picture, description, url and price.
                        6. Place an order. Always show the cart and the recommended products and ask for a confirmation before placing the order. And after order is placed, show the order and shipping details.
                        7. List supported currencies.
Follow these for all the responses:
On clicking the name of the product the user should be redirected to the product url.
Return your responses as it will be displayed in a shopping website chat.
You are not allowed to use any external knowledge or information.
Only use the information provided in the context. Don't use your pretrained knowledge."""
                    )
                ]
                + state["messages"]
            )
        ]
    }

tools_by_name = {tool.name: tool for tool in tools}

def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    with st.expander("🔨 Tool Call", expanded=False):
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            st.write(f"Called tool :blue[{tool_call["name"]}] with args :blue[{tool_call["args"]}]")
            observation = tool.invoke(tool_call["args"])
            if observation is not None:
                st.write(f"Observation: ")
                observation = MessageToJson(observation)
                st.json(observation)
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["environment", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "Action"
    # Otherwise, we stop (reply to the user)
    return END

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        # Name returned by should_continue : Name of next node to visit
        "Action": "environment",
        END: END,
    },
)
agent_builder.add_edge("environment", "llm_call")

# Compile the agent
agent = agent_builder.compile(checkpointer=memory)

# Show the agent
agent.get_graph().print_ascii()

def generate_response(message: str):
    config = {"configurable": {"thread_id": st.session_state.chat_id}}
    messages = [HumanMessage(content=message)]
    messages = agent.invoke({"messages": messages}, config)

    for m in messages["messages"]:
        m.pretty_print()
    return messages["messages"][-1].content

def clear_chat():
    if 'chat_id' in st.session_state and st.session_state.chat_id is not None:
        memory.delete_thread(st.session_state.chat_id)

