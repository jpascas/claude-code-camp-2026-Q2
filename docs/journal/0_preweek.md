# Preweek Technical Documentation

## Technical Goal

The technical goal is to explore different Agent Architectures, and see how they fit or not for our business requirements.

Examples of Agent Architecture that scale with effort:

- An agent file with referenced files eg. AGENT.md, @~/docs/\*.MD
- Agent Skills driven by main agent eg. ~/.skills
- Filesystem Subagent driven by a coding harness or Coding Agent SDK eg. ~/subagents
- AI workflow automation platform eg. n8n
- Use a generic AI Agent SDK that leverages plug and plays generic AI packages.
- Use low level first-party LLM SDKs and write our own agentic loop
- Use REST APIs directly, write our own agentic loop
  - The agentic loop is model-driven orchestration with middleware programmatic guidance
  - The agentic loop is code-driven orchestration

## Technical Uncertainty

- Claude Code or any other coding harness is really an effective way to run a non-coding task that requires an agentic loop?
- I'm not sure if LLMs models level of efforts and thinking mode are enough to manage the decision workflow to acomplish our task.

## Technical Hypothesis

- A more reliable and deterministic approach is needed to connect/interface with the MUD. On the Plain 01_plain_agent scenario, the coding harness had a hard time figuring out basic things like login or entering the game. That is why the custom skill approach using scripts, performed better.

- A long-lived telnet session hosted in a daemon performs better that opening, login and disconnecting for each operation. However, maintaining the sessiono may present its challenges.

- After observing the coding harness performance on difficult task, it was clear that a custom specialized agentic loop might be better suited to adapt and respond to task around navigating the MUD world.

## Technical Observations

- The plain agent approach, Agent.md, created bash and python script to try to connect and interact with the MUD, and it failed many times and was unreliable. A deterministic approach to solve this was required.

- The skill and subagents approach that used a script to manage a telnet session performed better, it addressed the issue with the Agent.md file. But improvements could be made to allow it to address the challenges of the game.

- Observed that the memory store on the markdown files that store things like the location of rooms and navigation between them was obscure (and i wonder if how it store it its deterministic or not), so a specialized data store might be needed for this. eg:

```bash
  **Route to Newbie Zone from start (Tournament Yard)**: north (Bar) ->
  west (Entrance Hall) -> north (Main Street) -> west (Main St 2) ->
  west (Market Square) -> north (Temple Square) -> north (Temple of
  Midgaard) -> north (By The Temple Altar) -> north (Behind Temple
  Altar) -> north (Great Field) -> east (structure) -> north (Entrance
  to Newbie Zone) -> north (Beginning of Passage).
```

- Observed that in the plain agent approach, the model selection (Haiku vs Sonnet), influenced the outcomes. (Haiku was stuck locating the bakery litle step by step, but Sonnet was able to do it more efficiently in a single session)

## Technical Conclusions

- Skills and Subagents are capable of driving the MUD.
- Specialized memory is needed for navigation of room and world data.
- Implementing our own specialized loop remains a pending task that will need to explore as we advance.
- We will need a custom agentic loop since without that the task were not be able to complete efficiently, and the navigation could not adapt to player modes and strategies.

## Key Takeaway

In a so specific/specialized scenario like playing a MUD is likely inneficient to use generic SDK for Agents. Specialized tooling like graph/vector databases and custom agentic loops might be needed.
