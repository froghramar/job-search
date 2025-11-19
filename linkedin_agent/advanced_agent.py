"""
Advanced Multi-Agent System for LinkedIn Job Search
Demonstrates extensible architecture with specialized agents
"""

from typing import Annotated, TypedDict, Literal, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

# ============================================================================
# ENHANCED STATE WITH MEMORY
# ============================================================================

class EnhancedAgentState(TypedDict):
    """Enhanced state with memory and context"""
    messages: Annotated[list, add_messages]
    
    # User context
    user_profile: dict
    preferences: dict
    
    # Job search context
    search_history: List[dict]
    found_jobs: List[dict]
    shortlisted_jobs: List[dict]
    applied_jobs: List[dict]
    
    # Agent routing
    current_agent: str
    next_action: str
    
    # Analysis results
    job_analyses: dict
    recommendations: List[str]


# ============================================================================
# SPECIALIZED TOOLS BY AGENT
# ============================================================================

# Research Agent Tools
@tool
def deep_job_research(job_id: str, company_name: str) -> dict:
    """
    Research job and company in depth.
    Includes company reviews, culture, interview process.
    """
    return {
        "job_id": job_id,
        "company": company_name,
        "glassdoor_rating": 4.2,
        "company_size": "1000-5000 employees",
        "culture_tags": ["innovative", "fast-paced", "collaborative"],
        "interview_process": {
            "rounds": ["Phone screen", "Technical", "Behavioral", "Final"],
            "difficulty": "Medium-Hard",
            "timeline": "2-3 weeks"
        },
        "employee_reviews": [
            "Great work-life balance",
            "Competitive compensation",
            "Strong engineering culture"
        ]
    }


# Analyst Agent Tools
@tool
def calculate_job_score(
    job_requirements: List[str],
    user_skills: List[str],
    salary: str,
    location: str,
    user_preferences: dict
) -> dict:
    """
    Calculate comprehensive job match score.
    """
    # Simple mock scoring
    skill_match = len(set(job_requirements) & set(user_skills)) / len(job_requirements)
    
    return {
        "total_score": 0.87,
        "skill_match": skill_match,
        "salary_match": 0.9,
        "location_match": 0.85,
        "culture_fit": 0.88,
        "breakdown": {
            "technical_fit": 0.9,
            "experience_match": 0.85,
            "career_growth": 0.82
        },
        "recommendation": "Strong match - highly recommended to apply"
    }


# Application Agent Tools
@tool
def prepare_application_package(
    job_id: str,
    job_description: str,
    user_profile: dict
) -> dict:
    """
    Prepare complete application package including optimized resume and cover letter.
    """
    return {
        "job_id": job_id,
        "resume": "Optimized resume content...",
        "cover_letter": "Tailored cover letter...",
        "key_talking_points": [
            "Highlight 5 years of Python experience",
            "Emphasize ML project leadership",
            "Mention relevant certifications"
        ],
        "questions_to_ask": [
            "What does the team structure look like?",
            "What are the key challenges for this role?"
        ]
    }


# ============================================================================
# SPECIALIZED AGENT NODES
# ============================================================================

def supervisor_agent(state: EnhancedAgentState) -> EnhancedAgentState:
    """
    Supervisor agent that routes to specialized agents.
    Decides which agent should handle the current task.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = """
    You are a supervisor agent coordinating a team of specialized agents:
    
    1. RESEARCHER: Searches for jobs and gathers information
    2. ANALYST: Analyzes job matches and provides recommendations
    3. APPLICANT: Handles job applications and prepares materials
    4. TRACKER: Monitors application status and follows up
    
    Based on the user's request, route to the appropriate agent.
    If the task is complete, route to FINISH.
    
    Respond with just the agent name: RESEARCHER, ANALYST, APPLICANT, TRACKER, or FINISH
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    # Extract routing decision
    next_agent = response.content.strip().upper()
    
    return {
        "current_agent": next_agent,
        "messages": [response]
    }


def researcher_agent(state: EnhancedAgentState) -> EnhancedAgentState:
    """
    Specialized agent for job search and research.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Import tools from main agent file
    from linkedin_agent.agent import search_linkedin_jobs, get_job_details
    
    tools = [search_linkedin_jobs, get_job_details, deep_job_research]
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """
    You are a research specialist for job searching.
    Your role:
    - Search for relevant job opportunities
    - Gather detailed information about positions
    - Research companies and their culture
    - Compile comprehensive job profiles
    
    Be thorough and detail-oriented.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}


def analyst_agent(state: EnhancedAgentState) -> EnhancedAgentState:
    """
    Specialized agent for analyzing job matches.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    tools = [calculate_job_score]
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """
    You are an expert job match analyst.
    Your role:
    - Analyze how well jobs match user profiles
    - Calculate compatibility scores
    - Identify gaps and requirements
    - Provide strategic recommendations
    
    Be analytical and data-driven.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}


def applicant_agent(state: EnhancedAgentState) -> EnhancedAgentState:
    """
    Specialized agent for job applications.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    from linkedin_agent.agent import apply_to_job, generate_cover_letter
    
    tools = [apply_to_job, generate_cover_letter, prepare_application_package]
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """
    You are an application specialist.
    Your role:
    - Prepare tailored application materials
    - Generate compelling cover letters
    - Optimize resumes for specific jobs
    - Submit applications on behalf of users
    
    Always ask for confirmation before submitting applications.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}


def tracker_agent(state: EnhancedAgentState) -> EnhancedAgentState:
    """
    Specialized agent for tracking applications.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = """
    You are an application tracking specialist.
    Your role:
    - Monitor application statuses
    - Track interview schedules
    - Send follow-up reminders
    - Provide progress reports
    
    Keep users informed and organized.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {"messages": [response]}


# ============================================================================
# ROUTER FUNCTION
# ============================================================================

def route_to_agent(state: EnhancedAgentState) -> str:
    """
    Route to the appropriate agent based on supervisor decision.
    """
    current_agent = state.get("current_agent", "")
    
    if current_agent == "RESEARCHER":
        return "researcher"
    elif current_agent == "ANALYST":
        return "analyst"
    elif current_agent == "APPLICANT":
        return "applicant"
    elif current_agent == "TRACKER":
        return "tracker"
    else:
        return "end"


def should_continue_tools(state: EnhancedAgentState) -> Literal["tools", "supervisor"]:
    """
    Decide if we should execute tools or return to supervisor.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return "supervisor"


# ============================================================================
# BUILD MULTI-AGENT GRAPH
# ============================================================================

def create_multi_agent_system() -> StateGraph:
    """
    Create a multi-agent system with specialized agents.
    """
    # Initialize workflow
    workflow = StateGraph(EnhancedAgentState)
    
    # Add all agent nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("applicant", applicant_agent)
    workflow.add_node("tracker", tracker_agent)
    
    # Add tools node
    from linkedin_agent.agent import search_linkedin_jobs, get_job_details, apply_to_job, generate_cover_letter
    all_tools = [
        search_linkedin_jobs,
        get_job_details,
        apply_to_job,
        generate_cover_letter,
        deep_job_research,
        calculate_job_score,
        prepare_application_package
    ]
    workflow.add_node("tools", ToolNode(all_tools))
    
    # Set entry point
    workflow.add_edge(START, "supervisor")
    
    # Supervisor routes to specialized agents
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "applicant": "applicant",
            "tracker": "tracker",
            "end": END
        }
    )
    
    # Each agent can use tools or return to supervisor
    for agent in ["researcher", "analyst", "applicant"]:
        workflow.add_conditional_edges(
            agent,
            should_continue_tools,
            {
                "tools": "tools",
                "supervisor": "supervisor"
            }
        )
    
    # Tracker returns to supervisor
    workflow.add_edge("tracker", "supervisor")
    
    # Tools return to supervisor
    workflow.add_edge("tools", "supervisor")
    
    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# ============================================================================
# GRAPH INSTANCE
# ============================================================================

# Create the multi-agent graph
multi_agent_graph = create_multi_agent_system()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("Multi-Agent LinkedIn Job System")
    print("=" * 60)
    
    # Initialize state with user context
    initial_state = {
        "messages": [
            HumanMessage(content="Find and analyze AI engineer jobs in SF, then help me apply to the best matches")
        ],
        "user_profile": {
            "skills": ["Python", "Machine Learning", "LangChain"],
            "experience_years": 5
        },
        "preferences": {
            "locations": ["San Francisco, CA"],
            "remote": True,
            "salary_min": 150000
        },
        "search_history": [],
        "found_jobs": [],
        "shortlisted_jobs": [],
        "applied_jobs": [],
        "current_agent": "",
        "next_action": "",
        "job_analyses": {},
        "recommendations": []
    }
    
    # Run the multi-agent system
    config = {"configurable": {"thread_id": "test_session_1"}}
    
    print("\nRunning multi-agent workflow...")
    print("-" * 60)
    
    for event in multi_agent_graph.stream(initial_state, config):
        for node_name, node_output in event.items():
            print(f"\n[{node_name.upper()}]")
            if "messages" in node_output:
                last_msg = node_output["messages"][-1]
                if hasattr(last_msg, "content"):
                    print(f"Output: {last_msg.content[:200]}...")
    
    print("\n" + "=" * 60)
    print("Multi-agent workflow complete!")