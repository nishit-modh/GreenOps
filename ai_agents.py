"""
AI Agents for GreenOps application.
Uses CrewAI to create context-aware ESG agents.
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables
load_dotenv()

# Force Groq API key into the exact variable LiteLLM demands
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

def get_llm():
    """Initialize and return the Groq LLM instance."""
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.4 # Lowered from 0.7. We want factual analytics, not creative writing.
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
            role="Data Entry Assistant",
            goal="Classify raw user inputs into the app's specific UI categories.",
            backstory="You are a pedantic carbon accounting auditor. Users will give you messy descriptions "
                     "of their industrial activities. You must coldly categorize them into the exact UI dropdowns "
                     "available in the system: 'Energy Consumption', 'Waste Management', or 'Carbon Emissions'. "
                     "You may mention if it aligns with Scope 1, 2, or 3, but the primary mapping must match the UI.",
            allow_delegation=False,
            verbose=False
        )
        
        self.report_generator = Agent(
            llm=self.llm,
            role="Report Summary Generator",
            goal="Convert a compressed mathematical data string into an executive ESG compliance summary.",
            backstory="You are a Lead ESG Analyst. You do not need raw database rows. You take high-level "
                     "aggregated metrics (Total Impact, Scope Breakdown, Worst Offenders) and generate a brutal, "
                     "no-nonsense executive summary. You highlight exactly where the enterprise is bleeding carbon.",
            allow_delegation=False,
            verbose=False
        )
        
        self.offset_advisor = Agent(
            llm=self.llm,
            role="Carbon Offset Advisor",
            goal="Suggest verified, financially realistic offset options based on the SME's profile.",
            backstory="You are a pragmatic sustainability financial advisor. You know that Indian SMEs cannot "
                     "afford million-dollar direct air capture technologies. You suggest realistic, verified "
                     "carbon offset projects (like local afforestation, renewable energy credits) tailored to "
                     "their specific industry and regional constraints.",
            allow_delegation=False,
            verbose=False
        )
        
        self.regulation_radar = Agent(
            llm=self.llm,
            role="Regulation Radar",
            goal="Assess regulatory threat levels based on the user's location and target export markets.",
            backstory="You are an international trade compliance lawyer. You specialize in the EU Carbon Border "
                     "Adjustment Mechanism (CBAM), India's BRSR, and global carbon taxes. When given a company's "
                     "export markets, you immediately flag exactly which compliance frameworks will hit their profit margins.",
            allow_delegation=False,
            verbose=False
        )
        
        self.emission_optimizer = Agent(
            llm=self.llm,
            role="Emission Optimizer",
            goal="Use the compressed data summary to suggest CapEx/OpEx operational changes.",
            backstory="You are a ruthless industrial efficiency engineer. You look at the 'Worst Carbon Offenders' "
                     "list and provide 3 immediate, actionable engineering or logistical changes to cut emissions. "
                     "No generic 'turn off the lights' advice—you give industrial-grade operational fixes.",
            allow_delegation=False,
            verbose=False
        )
    def create_data_entry_task(self, data_description):
        return Task(
            description=(
                f"Analyze this activity: '{data_description}'\n"
                f"1. State the exact App Scope it belongs to (Choose only from: 'Energy Consumption', 'Waste Management', or 'Carbon Emissions').\n"
                f"2. Mention the standard GHG Protocol Scope (1, 2, or 3) for context.\n"
                f"3. Do not invent math. Just provide the classification structure."
            ),
            expected_output="A strict 2-bullet classification mapping the activity to the UI dropdown and GHG Protocol.",
            agent=self.data_entry_assistant
        )
    
    def create_report_summary_task(self, emissions_data):
        return Task(
            description=(
                f"Analyze this compressed data summary:\n{emissions_data}\n\n"
                f"1. Write a 2-paragraph executive overview of the carbon footprint.\n"
                f"2. Explicitly call out the highest-emitting Scope.\n"
                f"3. Identify the worst offender and state why it's a bottleneck."
            ),
            expected_output="A concise, professional executive summary of the provided data.",
            agent=self.report_generator
        )
    
    def create_offset_advice_task(self, emissions_total, location, industry):
        return Task(
            description=(
                f"Organization Profile:\n- Deficit: {emissions_total} kgCO2e\n- Location: {location}\n- Industry: {industry}\n\n"
                f"Provide 3 verified carbon offset strategies (e.g., Gold Standard, VCS) realistic for an SME in this sector. "
                f"Mention potential cost brackets."
            ),
            expected_output="Three actionable carbon offset project recommendations with financial context.",
            agent=self.offset_advisor
        )
    
    def create_regulation_check_task(self, location, industry, export_markets):
        return Task(
            description=(
                f"Profile:\n- Origin: {location}\n- Industry: {industry}\n- Exporting to: {export_markets}\n\n"
                f"List the immediate carbon reporting regulations this company faces. If EU is in the export list, "
                f"you MUST detail CBAM reporting requirements. Keep it strictly focused on financial/trade compliance."
            ),
            expected_output="A bulleted threat-assessment of regulatory compliance frameworks.",
            agent=self.regulation_radar
        )
    
    def create_optimization_task(self, emissions_data):
        return Task(
            description=(
                f"Look at the worst offenders in this data:\n{emissions_data}\n\n"
                f"Provide 3 highly specific, operational engineering changes to reduce this specific footprint. "
                f"Focus on practical SME upgrades, not sci-fi technology."
            ),
            expected_output="Three industrial/operational engineering recommendations to reduce the primary emission source.",
            agent=self.emission_optimizer
        )
    
    # --- Execution Wrappers ---
    def run_data_entry_crew(self, data_description):
        task = self.create_data_entry_task(data_description)
        return Crew(agents=[self.data_entry_assistant], tasks=[task], verbose=False).kickoff()
    
    def run_report_summary_crew(self, emissions_data):
        task = self.create_report_summary_task(emissions_data)
        return Crew(agents=[self.report_generator], tasks=[task], verbose=False).kickoff()
    
    def run_offset_advice_crew(self, emissions_total, location, industry):
        task = self.create_offset_advice_task(emissions_total, location, industry)
        return Crew(agents=[self.offset_advisor], tasks=[task], verbose=False).kickoff()
    
    def run_regulation_check_crew(self, location, industry, export_markets):
        task = self.create_regulation_check_task(location, industry, export_markets)
        return Crew(agents=[self.regulation_radar], tasks=[task], verbose=False).kickoff()
    
    def run_optimization_crew(self, emissions_data):
        task = self.create_optimization_task(emissions_data)
        return Crew(agents=[self.emission_optimizer], tasks=[task], verbose=False).kickoff()