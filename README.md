# LinkedIn Job Search & Application Agent

An intelligent agentic AI system built with **LangGraph** and **LangChain** to automate LinkedIn job searching and application processes.

## 🚀 Features

### Current Features
- ✅ Intelligent job search based on user criteria
- ✅ Detailed job information retrieval
- ✅ AI-powered cover letter generation
- ✅ Conversational interface for job hunting
- ✅ Tool-calling agent architecture with LangGraph

### Planned Features (Extensible)
- 🔄 Automated job applications via LinkedIn Easy Apply
- 🔄 Resume optimization for specific jobs
- 🔄 Application tracking and status monitoring
- 🔄 Referral network analysis
- 🔄 Interview preparation assistance
- 🔄 Salary research and negotiation tips
- 🔄 Browser automation with Playwright
- 🔄 Persistent storage with MongoDB/PostgreSQL

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key (or other LLM provider)
- LangSmith account (optional, for monitoring)

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Create project directory
mkdir linkedin-job-agent
cd linkedin-job-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Bash:
source .venv/Scripts/activate

# Install LangGraph CLI
pip install langgraph-cli
```

### 2. Project Structure

Create the following structure:

```
linkedin-job-agent/
├── linkedin_agent/
│   ├── __init__.py
│   ├── agent.py          # Main agent code
│   ├── tools.py          # Extended tools
│   └── utils.py          # Utility functions
├── .env                   # Environment variables
├── .env.example          # Example environment file
├── requirements.txt      # Python dependencies
├── langgraph.json        # LangGraph configuration
└── README.md             # This file
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required variables:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Optional but recommended:**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=linkedin-job-agent
```

## 🚀 Running the Agent

### Option 1: Using LangGraph Studio (Recommended)

Start the development server with hot reloading:

```bash
langgraph dev
```

This will:
1. Start the LangGraph server on `http://127.0.0.1:2024`
2. Open LangGraph Studio in your browser
3. Enable hot-reloading for development

**LangGraph Studio URL:**
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Option 2: Using Python SDK

```python
from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://localhost:2024")

# Stream responses
for chunk in client.runs.stream(
    None,
    "linkedin_job_agent",
    input={
        "messages": [{
            "role": "human",
            "content": "Find me AI engineer jobs in San Francisco"
        }]
    },
    stream_mode="values"
):
    print(chunk)
```

### Option 3: Direct Python Execution

```bash
python linkedin_agent/agent.py
```

## 🎯 Usage Examples

### Example 1: Basic Job Search

```
User: Find me machine learning engineer jobs in New York

Agent: I'll search for machine learning engineer positions in New York for you.
[Searches LinkedIn...]
Found 15 jobs matching your criteria:

1. Senior ML Engineer at TechCorp - $150k-$200k
   Location: New York, NY (Remote option)
   Posted: 2 days ago
   
2. Machine Learning Engineer at AI Startup
   Location: New York, NY
   Posted: 1 week ago

Would you like more details on any of these positions?
```

### Example 2: Job Application with Cover Letter

```
User: Apply to the TechCorp position and generate a cover letter

Agent: I'll generate a personalized cover letter for the Senior ML Engineer 
position at TechCorp. Let me analyze the job requirements first...

[Generates cover letter based on job description and your profile]

Here's your cover letter:
[Shows generated cover letter]

Would you like me to proceed with the application?
```

### Example 3: Filtering and Analysis

```
User: Show me only remote positions that mention Python and deep learning

Agent: Filtering jobs for remote positions with Python and deep learning...
[Applies filters...]
Found 8 matching positions. Here are the top 3:
[Shows filtered results with match scores]
```

## 🏗️ Architecture

### Agent Flow

```mermaid
graph TD
    A[User Input] --> B[Agent Node]
    B --> C{Tool Call?}
    C -->|Yes| D[Tools Node]
    C -->|No| E[End]
    D --> F[Execute Tool]
    F --> B
```

### Key Components

1. **StateGraph**: Manages conversation state and job search context
2. **Agent Node**: Main reasoning node using LLM with tool binding
3. **Tools Node**: Executes tools (search, apply, generate cover letter)
4. **Conditional Edges**: Routes between agent and tools based on LLM decision

### Tools Available

| Tool | Description | Status |
|------|-------------|--------|
| `search_linkedin_jobs` | Search LinkedIn for jobs | ✅ Implemented |
| `get_job_details` | Get detailed job information | ✅ Implemented |
| `apply_to_job` | Apply to a job posting | ✅ Stub |
| `generate_cover_letter` | Create personalized cover letter | ✅ Implemented |
| `update_user_preferences` | Save job search preferences | 📋 Planned |
| `analyze_job_match` | Match score for job fit | 📋 Planned |
| `find_referrals` | Find connections at companies | 📋 Planned |

## 🔧 Configuration

### langgraph.json

```json
{
  "dependencies": ["."],
  "graphs": {
    "linkedin_job_agent": "./linkedin_agent/agent.py:graph"
  },
  "env": ".env"
}
```

### Customizing the Agent

**Change the LLM model:**

```python
llm = ChatOpenAI(model="gpt-4o", temperature=0)  # Change model here
```

**Add custom tools:**

```python
@tool
def my_custom_tool(param: str) -> dict:
    """Your tool description"""
    # Implementation
    return {"result": "success"}

# Add to tools list
tools = [search_linkedin_jobs, my_custom_tool]
```

**Modify system prompt:**

Edit the `SystemMessage` content in `agent_node()` function.

## 📊 Monitoring with LangSmith

Enable tracing to monitor agent performance:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_api_key
export LANGCHAIN_PROJECT=linkedin-job-agent
```

View traces at: https://smith.langchain.com

## 🔐 Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit `.env` file** - Add to `.gitignore`
2. **LinkedIn credentials** - Use environment variables only
3. **Rate limiting** - Implement to avoid account restrictions
4. **API quotas** - Monitor OpenAI/LLM usage
5. **User data** - Encrypt stored resumes and applications

## 🚧 Implementing LinkedIn Integration

To enable actual LinkedIn functionality:

### 1. Browser Automation (Playwright)

```python
from playwright.async_api import async_playwright

async def login_to_linkedin(email: str, password: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.linkedin.com/login")
        # Login flow...
```

### 2. LinkedIn API (Limited Access)

- Apply for LinkedIn API access
- Use OAuth 2.0 for authentication
- Access limited to certain endpoints

### 3. Third-Party Services

- RapidAPI LinkedIn scrapers
- ProxyCrawl for web scraping
- ScrapingBee for browser automation

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_agent.py -v

# With coverage
pytest --cov=linkedin_agent tests/
```

## 📈 Future Enhancements

- [ ] Multi-agent system (researcher, applier, tracker)
- [ ] RAG for job description analysis
- [ ] Resume parsing and optimization
- [ ] Interview scheduling assistant
- [ ] Salary negotiation advisor
- [ ] Network analysis for referrals
- [ ] Email integration for application tracking
- [ ] Mobile app interface
- [ ] Voice interface
- [ ] Analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangSmith](https://smith.langchain.com/)
- [LinkedIn Developer Portal](https://developer.linkedin.com/)

## 💡 Tips

- Start with the mock implementation to understand the flow
- Test thoroughly before connecting to real LinkedIn
- Use LangSmith for debugging agent behavior
- Implement rate limiting to avoid API restrictions
- Store user data securely with encryption

## 🐛 Troubleshooting

### "Graph not found" error
- Check that `langgraph.json` is in the project root
- Verify the graph path in configuration
- Ensure the graph variable is named correctly

### Import errors
- Activate virtual environment
- Run `pip install -r requirements.txt`
- Check Python version (3.10+)

### LangGraph Studio not opening
- Ensure port 2024 is not in use
- Try `langgraph dev --port 8080`
- Check firewall settings

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check LangChain Discord
- Review LangGraph documentation

---

Built with ❤️ using LangGraph and LangChain