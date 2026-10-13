"""Run the crew on a topic and print each step."""
import sys
from graph import app

topic = " ".join(sys.argv[1:]) or "the agent loop"
start = {"topic": topic, "notes": "", "draft": "", "feedback": "", "drafts": 0}

# stream() hands us each node's update as it happens
for step in app.stream(start):
    print(step)