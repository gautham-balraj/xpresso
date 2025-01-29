from typing_extensions import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from src.assistant.state import SummaryState, SummaryStateInput, SummaryStateOutput
from src.assistant.prompts import query_writer_instructions, summarizer_instructions, reflection_instructions, x_agent_instructions
from langchain_groq import ChatGroq
from src.assistant.utils.web_sc import TavilySearchAPI
from src.assistant.utils.x_sc import initialize_twitter_client
from dotenv import load_dotenv
import json
import os


load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')  
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API')  

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

search_api = TavilySearchAPI(api_key=os.environ['TAVILY_API_KEY'])

client, api = initialize_twitter_client()


def generate_query(state:SummaryState):
    print(f"\033[94mRunning function: generate_query - {state.research_loop_count} \033[0m")
    query_writer_instructions_prompt = query_writer_instructions.format(research_topic=state.research_topic)
    structured_llm = llm.with_structured_output(method="json_mode", include_raw=True)

    response = structured_llm.invoke([
        SystemMessage(content=query_writer_instructions_prompt),
        HumanMessage(content=f"Generate a query for web search:")])
    

    return {"search_query":response['parsed']['query'] }

def web_search(state:SummaryState):
    print("\033[94mRunning function: web_search\033[0m")
    search_query = generate_query(state)['search_query']
    result = search_api.search(query=search_query, search_depth="advanced",  max_results=5, include_images=False, include_image_descriptions=False, include_answer=False, include_raw_content=False)

    result_formatted = search_api.format_llm(result)

    return {"web_research_results":[result_formatted],'sources_gathered':result['results'],'research_loop_count':state.research_loop_count+1}


def summarizer(state:SummaryState):
    print("\033[94mRunning function: summarizer\033[0m")
    existing_summary = state.running_summary
    recent_web = state.web_research_results[-1]

    if existing_summary:
        human_message_content = (
            f"Extend the existing summary: {existing_summary}\n\n"
            f"Include new search results: {recent_web} "
            f"That addresses the following topic: {state.research_topic}"
        )
    else:
        human_message_content = (
            f"Generate a summary of these search results: {recent_web} "
            f"That addresses the following topic: {state.research_topic}"
        )

    result = llm.invoke([
        SystemMessage(content=summarizer_instructions),
        HumanMessage(content=human_message_content)
    ])

    return {'running_summary':result.content}

def reflection(state:SummaryState): 
    print("\033[94mRunning function: reflection\033[0m")
    structured_llm = llm.with_structured_output(method="json_mode", include_raw=True)
    result = structured_llm.invoke([
        SystemMessage(content=reflection_instructions),
        HumanMessage(content=f"Indentify a knowledge gap and generate a follow-up web search query based on our existing knowledge : {state.running_summary}")
    ])

    return {"search_query":result['parsed']['follow_up_query']}


def finalize_summary(state: SummaryState):
    print("\033[94mRunning function: finalize_summary\033[0m")
    """ Finalize the summary """
    
    # Format all accumulated sources into a single bulleted list
    all_sources = "\n".join(source for source in [e['url'] for e in state.sources_gathered])
    state.running_summary = f"## Summary\n\n{state.running_summary}\n\n ### Sources:\n{all_sources}"
    return {"running_summary": state.running_summary}


def route_research(state: SummaryState) -> Literal["finalize_summary", "web_research"]:
    print("\033[94mRunning function: route_research\033[0m")
    """ Route the research based on the follow-up query """

    if state.research_loop_count <= 1:
        return "web_research"
    else:
        return "finalize_summary" 
    

def x_agent(state: SummaryState):
    structured_llm = llm.with_structured_output(method="json_mode", include_raw=True)
    response = structured_llm.invoke([
        SystemMessage(content=x_agent_instructions),
        HumanMessage(content=f"Generate a tweets for the following topic: {state.research_topic} and the following researched Content: {state.running_summary}")
    ])


    return {"tweets":response['parsed']['tweets']}

    
def graph_builder():    
    print("\033[94mRunning function: graph_builde\033[0m")
    builder = StateGraph(SummaryState, input=SummaryStateInput, output=SummaryStateOutput, )
    builder.add_node("generate_query", generate_query)
    builder.add_node("web_research", web_search)
    builder.add_node("summarize_sources", summarizer)
    builder.add_node("reflect_on_summary", reflection)
    builder.add_node("finalize_summary", finalize_summary)
    builder.add_node("x_agent", x_agent)

    builder.add_edge(START, "generate_query")
    builder.add_edge("generate_query", "web_research")
    builder.add_edge("web_research", "summarize_sources")
    builder.add_edge("summarize_sources", "reflect_on_summary")
    builder.add_conditional_edges("reflect_on_summary", route_research)
    builder.add_edge("finalize_summary", "x_agent")
    builder.add_edge("x_agent", END)
    graph = builder.compile()

    return graph