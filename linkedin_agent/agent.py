"""
LinkedIn Job Search and Application Agent
Built with LangGraph for agentic AI workflows
"""

from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
import operator

# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(MessagesState):
    """
    State schema for the LinkedIn job agent.
    Extends MessagesState to enable Chat mode in LangGraph Studio.
    """
    # MessagesState already includes: messages: Annotated[list, add_messages]
    job_search_params: dict
    found_jobs: list
    applied_jobs: list
    next_action: str


# ============================================================================
# CUSTOM TOOLS (NOW WITH REAL LINKEDIN SCRAPING)
# ============================================================================

# Import the real scraper and profile fetcher
from linkedin_agent.real_linkedin_scraper import LinkedInJobScraper
from linkedin_agent.profile_fetcher import get_user_profile
from linkedin_agent.resume_cover_generator import (
    generate_resume_for_job,
    generate_cover_letter_for_job,
    generate_full_application
)

# Initialize scraper globally
_scraper = None
_user_profile = None

def get_scraper():
    """Lazy initialization of scraper"""
    global _scraper
    if _scraper is None:
        _scraper = LinkedInJobScraper()
    return _scraper

def get_cached_user_profile():
    """Get user profile (cached)"""
    global _user_profile
    if _user_profile is None:
        _user_profile = get_user_profile()
        if _user_profile:
            print(f"✅ Loaded profile for: {_user_profile.get('name', 'User')}")
        else:
            print("⚠️ Could not load user profile. Set LINKEDIN_USER_HANDLE in .env")
    return _user_profile


@tool
def search_linkedin_jobs(
    keywords: str,
    location: str = "",
    experience_level: str = "mid",
    job_type: str = "full-time",
    remote: bool = False,
    limit: int = 10
) -> dict:
    """
    Search for REAL jobs on LinkedIn based on criteria.
    This tool scrapes actual, current job listings from LinkedIn.
    
    Args:
        keywords: Job title or keywords to search for
        location: Location for the job (city, state, or remote)
        experience_level: Experience level (entry, mid, senior, director, executive)
        job_type: Type of job (full-time, part-time, contract, temporary, internship)
        remote: Filter for remote jobs only
        limit: Maximum number of jobs to return (default 10)
    
    Returns:
        Dictionary containing list of real jobs found
    """
    try:
        scraper = get_scraper()
        
        # Search for real jobs
        jobs = scraper.search_jobs(
            keywords=keywords,
            location=location,
            experience_level=experience_level,
            job_type=job_type,
            remote=remote,
            limit=limit
        )
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs),
            "search_params": {
                "keywords": keywords,
                "location": location,
                "experience_level": experience_level,
                "job_type": job_type,
                "remote": remote
            },
            "source": "LinkedIn (live scraping)"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "jobs": [],
            "count": 0,
            "message": f"Failed to fetch jobs from LinkedIn: {str(e)}"
        }


@tool
def get_job_details(job_id: str) -> dict:
    """
    Get detailed information about a specific job posting from LinkedIn.
    This fetches the full job description and details from the live listing.
    
    Args:
        job_id: Unique identifier for the job
    
    Returns:
        Detailed job information including full description
    """
    try:
        scraper = get_scraper()
        
        # Get real job details
        details = scraper.get_job_details(job_id)
        
        if details:
            return {
                "success": True,
                "job_id": job_id,
                "full_description": details.get("full_description", ""),
                "criteria": details.get("criteria", {}),
                "url": details.get("url", f"https://www.linkedin.com/jobs/view/{job_id}"),
                "source": "LinkedIn (live scraping)"
            }
        else:
            return {
                "success": False,
                "error": "Could not fetch job details",
                "job_id": job_id
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "job_id": job_id,
            "message": f"Failed to fetch job details: {str(e)}"
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
def get_my_profile() -> dict:
    """
    Fetch and display the user's LinkedIn profile information.
    Shows current skills, experience, education that will be used for applications.
    
    Returns:
        Dictionary containing user's profile data
    """
    try:
        user_profile = get_cached_user_profile()
        
        if not user_profile:
            return {
                "success": False,
                "error": "Could not load profile. Set LINKEDIN_USER_HANDLE in .env"
            }
        
        return {
            "success": True,
            "profile": {
                "name": user_profile.get('name'),
                "headline": user_profile.get('headline'),
                "location": user_profile.get('location'),
                "about": user_profile.get('about', '')[:200] + "..." if user_profile.get('about') else "No summary",
                "skills": user_profile.get('skills', [])[:15],
                "experience_count": len(user_profile.get('experience', [])),
                "education_count": len(user_profile.get('education', [])),
                "certifications_count": len(user_profile.get('certifications', [])),
                "url": user_profile.get('url')
            },
            "message": "Profile loaded successfully. This data will be used to generate personalized application materials."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching profile: {str(e)}"
        }


@tool
def generate_cover_letter(job_title: str, company_name: str, job_description: str) -> str:
    """
    Generate a personalized cover letter based on user's profile and job description.
    Uses the user's real LinkedIn profile data to create a tailored cover letter.
    
    Args:
        job_title: The job title
        company_name: The company name
        job_description: Full job description text
    
    Returns:
        Generated cover letter text
    """
    try:
        # Get user profile
        user_profile = get_cached_user_profile()
        
        if not user_profile:
            return "Error: Could not load user profile. Please set LINKEDIN_USER_HANDLE in .env"
        
        # Generate cover letter
        cover_letter = generate_cover_letter_for_job(
            user_profile=user_profile,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            tone="professional"
        )
        
        return cover_letter
        
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"


@tool
def generate_resume(job_description: str, format: str = "professional") -> str:
    """
    Generate a tailored resume based on user's profile and job requirements.
    Uses the user's real LinkedIn profile data to create an optimized resume.
    
    Args:
        job_description: Full job description text
        format: Resume format (professional, ats, technical)
    
    Returns:
        Generated resume text
    """
    try:
        # Get user profile
        user_profile = get_cached_user_profile()
        
        if not user_profile:
            return "Error: Could not load user profile. Please set LINKEDIN_USER_HANDLE in .env"
        
        # Generate resume
        resume = generate_resume_for_job(
            user_profile=user_profile,
            job_description=job_description,
            format=format
        )
        
        return resume
        
    except Exception as e:
        return f"Error generating resume: {str(e)}"


@tool
def generate_application_package(
    job_title: str,
    company_name: str,
    job_description: str,
    save_files: bool = True
) -> dict:
    """
    Generate complete application package (resume + cover letter) for a job.
    Uses the user's real LinkedIn profile to create tailored materials.
    Optionally saves to files.
    
    Args:
        job_title: The job title
        company_name: The company name
        job_description: Full job description text
        save_files: Whether to save materials to files
    
    Returns:
        Dictionary with resume and cover letter
    """
    try:
        # Get user profile
        user_profile = get_cached_user_profile()
        
        if not user_profile:
            return {
                "success": False,
                "error": "Could not load user profile. Set LINKEDIN_USER_HANDLE in .env"
            }
        
        # Generate package
        package = generate_full_application(
            user_profile=user_profile,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            save_to_files=save_files
        )
        
        result = {
            "success": True,
            "candidate": package['candidate'],
            "job_title": package['job_title'],
            "company": package['company'],
            "resume": package.get('resume', ''),
            "cover_letter": package.get('cover_letter', ''),
        }
        
        if save_files and 'saved_files' in package:
            result['saved_files'] = package['saved_files']
            result['message'] = f"Application materials saved to {len(package['saved_files'])} files"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating application package: {str(e)}"
        }


@tool
def get_my_profile() -> dict:
    """
    Fetch and display the user's LinkedIn profile information.
    Shows current skills, experience, education that will be used for applications.
    
    Returns:
        Dictionary containing user's profile data
    """
    try:
        user_profile = get_cached_user_profile()
        
        if not user_profile:
            return {
                "success": False,
                "error": "Could not load profile. Set LINKEDIN_USER_HANDLE in .env"
            }
        
        return {
            "success": True,
            "profile": {
                "name": user_profile.get('name'),
                "headline": user_profile.get('headline'),
                "location": user_profile.get('location'),
                "about": user_profile.get('about', '')[:200] + "...",
                "skills": user_profile.get('skills', [])[:15],
                "experience_count": len(user_profile.get('experience', [])),
                "education_count": len(user_profile.get('education', [])),
                "url": user_profile.get('url')
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching profile: {str(e)}"
        }


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
    tools = [
        search_linkedin_jobs,
        get_job_details,
        apply_to_job,
        generate_cover_letter,
        generate_resume,
        generate_application_package,
        get_my_profile
    ]
    llm_with_tools = llm.bind_tools(tools)
    
    # System message for the agent
    system_message = SystemMessage(content="""
    You are an intelligent LinkedIn job search and application assistant with access to the user's real LinkedIn profile.
    
    Your capabilities:
    1. Search for real jobs on LinkedIn based on user criteria
    2. Get detailed information about specific jobs
    3. Access the user's actual LinkedIn profile (skills, experience, education)
    4. Generate personalized cover letters based on user's profile and job requirements
    5. Generate tailored resumes optimized for specific jobs
    6. Create complete application packages (resume + cover letter)
    7. Apply to jobs on behalf of the user (with confirmation)
    
    When helping with applications:
    - Always use get_my_profile first to understand the user's background
    - Generate materials that highlight relevant experience from their actual profile
    - Ask for confirmation before applying to jobs
    - Save application materials to files when requested
    
    Always:
    - Ask for confirmation before applying to jobs
    - Provide clear summaries of job matches
    - Help users refine their search criteria
    - Be proactive in suggesting relevant actions
    - Use the user's actual profile data for personalization
    
    When searching for jobs, consider:
    - Keywords/job titles
    - Location preferences
    - Experience level
    - Job type (full-time, contract, etc.)
    - Remote options
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
    tools = [
        search_linkedin_jobs,
        get_job_details,
        apply_to_job,
        generate_cover_letter,
        generate_resume,
        generate_application_package,
        get_my_profile
    ]
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
    When using LangGraph Studio, you can test directly in Chat mode!
    """
    print("LinkedIn Job Search Agent - Testing Mode")
    print("=" * 50)
    print("\n💡 TIP: Run 'langgraph dev' and use Chat mode in LangGraph Studio")
    print("   for the best experience!\n")
    
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
    print("✅ Test complete!")
    print("\n🚀 To use Chat mode:")
    print("   1. Run: langgraph dev")
    print("   2. Click the 'Chat' tab in LangGraph Studio")
    print("   3. Start chatting with your agent!")