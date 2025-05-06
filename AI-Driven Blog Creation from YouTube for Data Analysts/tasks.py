from crewai import Task
from tools import yt_tool
from agents import blog_researcher, blog_writer

# Task 1: Research from YouTube
research_task = Task(
    description=(
        "Search the YouTube channel for videos related to '{topic}' and extract important "
        "insights useful for data analysts working with SQL, ML, or AI."
    ),
    expected_output=(
        "Bullet points or summary notes based on video about '{topic}', "
        "with a focus on applications in data analytics."
    ),
    tools=[yt_tool],
    agent=blog_researcher
)

# Task 2: Write Report
write_task = Task(
    description=(
        "Using the researched content, write a 3-paragraph structured blog report explaining "
        "the video insights in simple language for data analysts."
    ),
    expected_output=(
        "A Markdown file with a clear and engaging write-up for data professionals, "
        "summarizing the YouTube video content on '{topic}'."
    ),
    tools=[yt_tool],
    agent=blog_writer,
    async_execution=False,
    output_file='data-analyst-report.md'
)
