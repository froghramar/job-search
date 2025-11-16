"""
LinkedIn Job Search and Application Agent
Built with LangGraph for agentic AI workflows
"""

from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
import operator

# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """State schema for the LinkedIn job agent"""
    messages: Annotated[list, add_messages]
    job_search_params: dict
    found_jobs: list
    applied_jobs: list
    next_action: str


# ============================================================================
# CUSTOM TOOLS
# ============================================================================

@tool
def search_linkedin_jobs(
    keywords: str,
    location: str = "",
    experience_level: str = "entry",
    job_type: str = "full-time"
) -> dict:
    """
    Search for jobs on LinkedIn based on criteria.
    
    Args:
        keywords: Job title or keywords to search for
        location: Location for the job (city, state, or remote)
        experience_level: Experience level (entry, mid, senior)
        job_type: Type of job (full-time, part-time, contract, internship)
    
    Returns:
        Dictionary containing list of jobs found
    """
    # TODO: Implement actual LinkedIn job search
    # This is a placeholder that simulates the search
    # In production, you would:
    # 1. Use LinkedIn API (requires authentication)
    # 2. Use web scraping with Playwright/Selenium
    # 3. Use third-party APIs like RapidAPI LinkedIn scrapers
    
    mock_jobs = [
        {
            "job_id": "job_001",
            "title": f"{keywords} - Senior Position",
            "company": "TechCorp Inc.",
            "location": location or "Remote",
            "description": f"Looking for experienced {keywords} professional...",
            "url": "https://linkedin.com/jobs/view/job_001",
            "posted_date": "2 days ago",
            "easy_apply": True
        },
        {
            "job_id": "job_002",
            "title": f"{keywords} Engineer",
            "company": "InnovateTech",
            "location": location or "San Francisco, CA",
            "description": f"Join our team as a {keywords}...",
            "url": "https://linkedin.com/jobs/view/job_002",
            "posted_date": "1 week ago",
            "easy_apply": True
        }
    ]
    
    return {
        "success": True,
        "jobs": mock_jobs,
        "count": len(mock_jobs),
        "search_params": {
            "keywords": keywords,
            "location": location,
            "experience_level": experience_level,
            "job_type": job_type
        }
    }


@tool
def get_job_details(job_id: str) -> dict:
    """
    Get detailed information about a specific job posting.
    
    Args:
        job_id: Unique identifier for the job
    
    Returns:
        Detailed job information
    """
    # TODO: Implement actual job details retrieval
    return {
        "job_id": job_id,
        "full_description": "Detailed job description here...",
        "requirements": ["Python", "AI/ML", "3+ years experience"],
        "benefits": ["Health insurance", "401k", "Remote work"],
        "salary_range": "$120k - $180k"
    }


@tool
def apply_to_job(job_id: str, cover_letter: str = "") -> dict:
    """
    Apply to a job on LinkedIn (Easy Apply).
    
    Args:
        job_id: Unique identifier for the job
        cover_letter: Optional cover letter text
    
    Returns:
        Application status
    """
    # TODO: Implement actual job application
    # This would require:
    # 1. LinkedIn authentication
    # 2. Browser automation (Playwright/Selenium)
    # 3. Form filling and submission
    
    return {
        "success": True,
        "job_id": job_id,
        "status": "applied",
        "message": f"Successfully applied to job {job_id}",
        "timestamp": "2025-11-16T10:30:00Z"
    }


@tool
def generate_cover_letter(job_description: str, user_resume: str = "") -> str:
    """
    Generate a tailored cover letter for a job application.
    
    Args:
        job_description: The job description
        user_resume: User's resume or professional summary
    
    Returns:
        Generated cover letter text
    """
    # TODO: Use LLM to generate personalized cover letter
    return f"Generated cover letter based on the job requirements..."


# ============================================================================
# NODE FUNCTIONS
# ============================================================================

def agent_node(state: AgentState) -> AgentState:
    """
    Main agent node that decides what action to take.
    Uses the LLM to determine next steps based on conversation.
    """
    messages = state["messages"]
    
    # Initialize the LLM with tools - Using Claude Sonnet 4
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        max_tokens=4096
    )
    tools = [search_linkedin_jobs, get_job_details, apply_to_job, generate_cover_letter]
    llm_with_tools = llm.bind_tools(tools)
    
    # System message for the agent
    system_message = SystemMessage(content="""
    You are an intelligent LinkedIn job search and application assistant.
    
    Your capabilities:
    1. Search for jobs on LinkedIn based on user criteria
    2. Get detailed information about specific jobs
    3. Generate personalized cover letters
    4. Apply to jobs on behalf of the user (with confirmation)
    
    Always:
    - Ask for confirmation before applying to jobs
    - Provide clear summaries of job matches
    - Help users refine their search criteria
    - Be proactive in suggesting relevant actions
    
    When searching for jobs, consider:
    - Keywords/job titles
    - Location preferences
    - Experience level
    - Job type (full-time, contract, etc.)
    """)
    
    # Invoke the LLM
    response = llm_with_tools.invoke([system_message] + messages)
    
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Conditional edge function to determine if we should continue to tools or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are tool calls, continue to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end the conversation
    return "end"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_linkedin_agent() -> StateGraph:
    """
    Create the LinkedIn job search agent graph.
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    
    # Create tools node
    tools = [search_linkedin_jobs, get_job_details, apply_to_job, generate_cover_letter]
    workflow.add_node("tools", ToolNode(tools))
    
    # Add edges
    workflow.add_edge(START, "agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # After tools, go back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()


# ============================================================================
# MAIN GRAPH INSTANCE
# ============================================================================

# Create the compiled graph for LangGraph server
graph = create_linkedin_agent()


# ============================================================================
# TESTING / USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage for testing the agent locally.
    """
    print("LinkedIn Job Search Agent - Testing Mode")
    print("=" * 50)
    
    # Test the agent with a sample query
    initial_state = {
        "messages": [
            HumanMessage(content="Find me AI engineer jobs in San Francisco")
        ],
        "job_search_params": {},
        "found_jobs": [],
        "applied_jobs": [],
        "next_action": ""
    }
    
    # Run the agent
    result = graph.invoke(initial_state)
    
    # Print results
    print("\nAgent Response:")
    print("-" * 50)
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            print(f"AI: {message.content}")
        elif isinstance(message, HumanMessage):
            print(f"Human: {message.content}")
    
    print("\n" + "=" * 50)
    print("Test complete. Use 'langgraph dev' to run with studio.")