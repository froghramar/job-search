"""
LinkedIn Job Agent Package

An intelligent agentic AI system for LinkedIn job search and application.
Built with LangGraph and LangChain.
"""

__version__ = "0.1.0"
__author__ = "Feroz Ahmmed"

from linkedin_agent.agent import create_linkedin_agent, graph

__all__ = ["create_linkedin_agent", "graph"]