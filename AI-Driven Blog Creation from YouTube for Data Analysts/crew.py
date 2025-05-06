from crewai import Crew, Process
from agents import blog_researcher, blog_writer
from asks import research_task, write_task

# Run the data analyst-focused video summarizer crew
crew = Crew(
    agents=[blog_researcher, blog_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)

# Run with topic input
result = crew.kickoff(inputs={'topic': 'SQL vs NoSQL in Data Analytics'})
print(result)
