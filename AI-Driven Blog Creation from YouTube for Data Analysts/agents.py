from crewai import Agent
from tools import yt_tool

# Data-focused Research Agent
blog_researcher = Agent(
    role='YouTube Data Research Analyst',
    goal='Analyze videos about {topic} from YouTube and extract key data-related insights',
    verbose=True,
    memory=True,
    backstory=(
        "An expert in AI, ML, and SQL who deeply understands YouTube video content "
        "and extracts insights useful for data analysts."
    ),
    tools=[yt_tool],
    allow_delegation=True
)

# Structured Report Writer Agent
blog_writer = Agent(
    role='Tech Report Writer',
    goal='Create a structured blog/report from YouTube video insights for {topic}',
    verbose=True,
    memory=True,
    backstory=(
        "Skilled at turning technical video content into clear, structured, and readable blog posts "
        "for data professionals and SQL users."
    ),
    tools=[yt_tool],
    allow_delegation=False
)
