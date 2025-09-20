## Flow Description

User → UI
The user enters a natural language query (e.g., “Show me black sneakers under $80”).

UI → Backend (BE)
The UI forwards the query to the backend for processing.

Backend → LLM (gemini-2.5-flash)
The backend sends the user’s query along with prompts and tool information to the LLM.

LLM internal planning
The LLM analyzes the query, decides how to answer, and determines which tools are needed.

LLM → Tools
The LLM calls one or more tools to fulfill the request.

Tools → Microservices (via gRPC)
The tools make a gRPC API call to Online Boutique microservices to fetch product data or perform shopping actions.

Microservices → Tools
The microservices return a structured response (e.g., product list, cart update).

Tools → LLM
The tools send the processed response back to the LLM.

LLM → Backend
The LLM formulates the final natural language answer.

Backend → UI
The backend forwards the final answer to the UI.

UI → User
The UI displays the answer back to the user in a conversational format.

## Inspiration

Online shopping is often overwhelming — too many clicks, filters, and endless scrolling. I wanted to make it feel as natural as asking a shopkeeper for what you want. Convershop was born from the idea of blending conversational AI with the simplicity of shopping.

## What it does

Convershop is an AI-powered shopping assistant that understands natural language. Users can ask for products in plain English — “Show me black sneakers under $80” — and the bot handles product discovery, filtering, cart management, and checkout, all through conversation.

## How we built it

We integrated a large language model (LLM) with a backend that orchestrates prompts and tool usage. The LLM decides which tools to call, and those tools interact with microservices via gRPC to fetch product data, manage the cart, and complete purchases. The frontend UI connects the user’s natural language queries to this backend pipeline and returns responses in real time.

## Challenges we ran into

- Deployment issues on GKE due to Docker image architecture mismatch: my Apple M1 Pro (arm64) built images that weren’t compatible with the linux/amd64 pods.

- File permission errors in the Python app: certain directories couldn’t be created inside the container and needed permission fixes during deployment.

- gRPC client development friction: VS Code lacked support for some gRPC-generated data types, making it harder to code without running into typos or IDE hints.

## Accomplishments that we're proud of

- Built a reactive demo shopping chatbot capable of handling end-to-end shopping entirely through natural conversation.

- Achieved rapid development and deployment in Google Kubernetes Engine (GKE), overcoming cloud and containerization hurdles.

- Designed an extendable architecture where new tools and features — like coupon code application or personalized recommendations — can be seamlessly integrated.

## What we learned

- The importance of UX in conversational AI — users expect quick, precise answers.

- Trade-offs between flexibility in natural language and system reliability.

- Creating langchain tools from gRPC APIs.

## What's next for Convershop

- Add personalized recommendations using user history and preferences.

- Support multiple languages for international shoppers.

- Expand to voice-based interactions for hands-free shopping.
