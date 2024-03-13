from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilyAnswer, TavilySearchResults
from langchain import hub
import streamlit as st
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


# Response generator function
def response_generator():
    response = st.session_state.agent_executor.invoke(
        {"input": prompt + " Use the web search tool"}
    )

    response_text = response["output"]
    
    # print(response_text)

    # print(st.session_state.agent_executor)

    return response_text

selected_model = False

st.title("🦜🔗 Ollama ReAct Chatbot with Web Search")

if "model" not in st.session_state and "selected_model" in st.session_state and not selected_model:
    
    st.session_state.selected_model = st.selectbox('Select model', st.session_state.names, index=None,
   placeholder="Select model to chat with...", disabled=True)

    st.write("Chatting with 🤖 with Web Search", st.session_state.selected_model)


    st.session_state.instructions = """You are a knowledgeable and helpful assistant. Use web search to find the answer to the user's question. If you can't find the answer, ask the user for more information. If the user asks for a specific type of information, try to find that type of information."""
    # prompt = hub.pull("hwchase17/self-ask-with-search")
    st.session_state.prompt = hub.pull("hwchase17/react-chat")

    # prompt = base_prompt.partial(instructions=instructions)
    st.session_state.prompt = st.session_state.prompt.partial(instructions=st.session_state.instructions)

    st.session_state.model = ChatOllama(model=str(st.session_state.selected_model))

    # tavily_tool = TavilySearchResults()
    st.session_state.tools = [TavilyAnswer(name="Intermediate Answer")]

    st.session_state.agent = create_react_agent(st.session_state.model, st.session_state.tools, st.session_state.prompt)

    st.session_state.agent_executor = AgentExecutor(
        agent=st.session_state.agent,
        tools=st.session_state.tools,
        verbose=True,
        handle_parsing_errors=True,
        memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
    )

    # template_messages = [
    
    #     SystemMessage(content="You are a helpful and knowledgeable assistant."),
        
    #     MessagesPlaceholder(variable_name="chat_history"),
        
    #     HumanMessagePromptTemplate.from_template("{text}"),
    # ]

    # st.session_state.prompt_template = ChatPromptTemplate.from_messages(template_messages)

    # st.session_state.model = ChatOllama(model=str(st.session_state.selected_model))

    # st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # st.session_state.chain = LLMChain(llm=st.session_state.model, prompt=st.session_state.prompt_template, memory=st.session_state.memory)

    # print(st.session_state.agent_executor)

    selected_model = True

if "selected_model" in st.session_state and "model" in st.session_state:

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask your personal assistant a anything..."):
        # Add user message to chat history
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Assistant is typing..."):
                response = response_generator()
            message_placeholder = st.empty()
            
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
            
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            # st.write(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

else:


    # Get all models

    result = requests.get('http://localhost:11434/api/tags').json()['models']

    # Put them in list and store in session state

    st.session_state.names = tuple([f"{model['name']}" for model in result])

    print(st.session_state.names)

    st.write("Choose a model to start chatting")

    st.session_state.selected_model = st.selectbox('Select model', st.session_state.names, index=None,
   placeholder="Select model to chat with...", disabled=False)
    