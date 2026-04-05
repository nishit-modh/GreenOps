"""
AI Agents for GreenOps application.
Uses CrewAI to create context-aware ESG agents.
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables
load_dotenv()

def get_llm():
    """Initialize and return the Groq LLM instance."""
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.3, # Lowered further to enforce highly factual, non-creative, critical outputs.
        api_key=os.getenv("GROQ_API_KEY")
    )

class GreenOpsAgents:
    def __init__(self):
        """Initialize the GreenOpsAgents class and instantiate the Llama-3 brain."""
        self.llm = get_llm()
        self._create_agents()
    
    def _create_agents(self):
        """Create specialized AI agents with strict ESG domain knowledge."""
        
        self.data_entry_assistant = Agent(
            llm=self.llm,
            role="Data Entry Analyst",
            goal="Classify raw user inputs into exact UI categories without conversational filler.",
            backstory="You are a pedantic, highly technical carbon accounting auditor. You do not use pleasantries. "
                     "When given a messy description, you coldly categorize it into exact UI dropdowns: "
                     "'Energy Consumption', 'Waste Management', or 'Carbon Emissions'.",
            allow_delegation=False,
            verbose=False
        )
        
        self.report_generator = Agent(
            llm=self.llm,
            role="Lead ESG Auditor",
            goal="Convert compressed mathematical data into a highly structured, critical, and information-dense executive summary.",
            backstory="You are a ruthless Lead ESG Analyst. You do not sugarcoat reality, offer praise, or use corporate fluff. "
                     "You deliver direct, medium-length, information-loaded assessments. You expose exact operational inefficiencies "
                     "and format your findings using dense markdown structures, highlighting exactly where the enterprise is bleeding carbon.",
            allow_delegation=False,
            verbose=False
        )
        
        self.offset_advisor = Agent(
            llm=self.llm,
            role="Carbon Offset Strategist",
            goal="Provide highly structured, direct, and financially realistic offset options.",
            backstory="You are a pragmatic sustainability financial advisor. You do not waste time with introductions. "
                     "You provide concise, information-loaded recommendations for verified carbon offset projects tailored "
                     "to specific industry constraints.",
            allow_delegation=False,
            verbose=False
        )
        
        self.regulation_radar = Agent(
            llm=self.llm,
            role="Trade Compliance Assessor",
            goal="Output direct, critical regulatory threat assessments based on export markets.",
            backstory="You are a strict international trade compliance lawyer. You do not soften bad news. You flag exact "
                     "compliance frameworks (CBAM, BRSR, etc.) that will impact profit margins, delivering the analysis "
                     "in a dense, highly structured format.",
            allow_delegation=False,
            verbose=False
        )
        
        self.emission_optimizer = Agent(
            llm=self.llm,
            role="Industrial Efficiency Engineer",
            goal="Provide information-dense, actionable engineering changes to cut emissions.",
            backstory="You are a ruthless industrial efficiency engineer. You analyze 'Worst Carbon Offenders' and provide "
                     "highly technical, direct CapEx/OpEx operational changes. You never use generic advice. You deliver "
                     "structured, critical fixes.",
            allow_delegation=False,
            verbose=False
        )
        
    def create_data_entry_task(self, data_description):
        return Task(
            description=(
                f"Analyze this activity: '{data_description}'\n"
                f"1. State the exact App Scope it belongs to (Choose only from: 'Energy', 'Waste', or 'Direct Carbon & Travel').\n"
                f"2. Mention the standard GHG Protocol Scope (1, 2, or 3).\n"
                f"3. Do not include introductory text, greetings, or filler. Output strictly the classification."
            ),
            expected_output="A strict, no-fluff 2-bullet classification mapping the activity to the UI dropdown and GHG Protocol.",
            agent=self.data_entry_assistant
        )
    
    def create_report_summary_task(self, emissions_data):
        return Task(
            description=(
                f"Analyze this compressed data summary:\n{emissions_data}\n\n"
                f"Generate a structured, information-dense executive report. It must contain:\n"
                f"- **Systemic Impact Overview**: A critical assessment of the total footprint.\n"
                f"- **Scope Imbalance**: Direct analysis of the scope distribution.\n"
                f"- **Primary Bottlenecks**: A ruthless breakdown of the worst offenders and why they are inefficient.\n\n"
                f"Constraints: Do NOT use praise, sugarcoat the data, or include conversational filler. Be extremely direct and analytical."
            ),
            expected_output="A medium-length, structured, information-loaded markdown report detailing carbon inefficiencies.",
            agent=self.report_generator
        )
    
    def create_offset_advice_task(self, emissions_total, location, industry):
        return Task(
            description=(
                f"Profile: Deficit: {emissions_total} kgCO2e | Location: {location} | Industry: {industry}\n\n"
                f"Provide 3 verified carbon offset strategies. Format as a dense, structured list including project type, "
                f"verification standard (e.g., VCS, Gold Standard), and estimated financial impact.\n"
                f"Constraints: No pleasantries or introductory filler. Output the data directly."
            ),
            expected_output="Three concise, information-loaded carbon offset project recommendations with strict financial context.",
            agent=self.offset_advisor
        )
    
    def create_regulation_check_task(self, location, industry, export_markets):
        return Task(
            description=(
                f"Profile: Origin: {location} | Industry: {industry} | Exporting to: {export_markets}\n\n"
                f"List the immediate carbon reporting regulations this company faces. If EU is included, explicitly detail CBAM liability.\n"
                f"Constraints: Use a highly structured, bulleted format. Be critical and direct regarding financial/trade risks. No fluff."
            ),
            expected_output="A structured, direct threat-assessment of regulatory compliance frameworks.",
            agent=self.regulation_radar
        )
    
    def create_optimization_task(self, emissions_data):
        return Task(
            description=(
                f"Data:\n{emissions_data}\n\n"
                f"Provide 3 specific, operational engineering upgrades to reduce the primary emission sources.\n"
                f"Constraints: Provide technical depth. Structure the output clearly. Do not use praise or conversational filler."
            ),
            expected_output="Three structured, information-dense industrial/operational engineering recommendations.",
            agent=self.emission_optimizer
        )
    
    # --- Execution Wrappers ---
    def run_data_entry_crew(self, data_description):
        task = self.create_data_entry_task(data_description)
        return Crew(agents=[self.data_entry_assistant], tasks=[task], verbose=False).kickoff().raw
    
    def run_report_summary_crew(self, emissions_data):
        task = self.create_report_summary_task(emissions_data)
        return Crew(agents=[self.report_generator], tasks=[task], verbose=False).kickoff().raw
    
    def run_offset_advice_crew(self, emissions_total, location, industry):
        task = self.create_offset_advice_task(emissions_total, location, industry)
        return Crew(agents=[self.offset_advisor], tasks=[task], verbose=False).kickoff().raw
    
    def run_regulation_check_crew(self, location, industry, export_markets):
        task = self.create_regulation_check_task(location, industry, export_markets)
        return Crew(agents=[self.regulation_radar], tasks=[task], verbose=False).kickoff().raw
    
    def run_optimization_crew(self, emissions_data):
        task = self.create_optimization_task(emissions_data)
        return Crew(agents=[self.emission_optimizer], tasks=[task], verbose=False).kickoff().raw