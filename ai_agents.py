"""
AI Agents for GreenOps application.
Uses CrewAI to create agents for various tasks.
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables
load_dotenv()

# Get Groq API key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

# Initialize LLM
def get_llm():
    """Initialize and return the Groq LLM."""
    return LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.7
)

# Create AI agents
class CarbonFootprintAgents:
    def __init__(self):
        """Initialize the CarbonFootprintAgents class."""
        self.llm = get_llm()
        self._create_agents()
    
    def _create_agents(self):
        """Create all the agents."""
        # Data Entry Assistant
        self.data_entry_assistant = Agent(
            llm=self.llm,
            role="Data Entry Assistant",
            goal="Help users classify emissions, map to scopes, and validate data entries",
            backstory="You are an expert in carbon accounting who helps users correctly categorize "
                     "their emissions data and ensure it's properly mapped to the right scope. "
                     "You understand the nuances of Scope 1, 2, and 3 emissions and can guide "
                     "users to make accurate entries.",
            allow_delegation=False,
            verbose=False
        )
        
        # Report Summary Generator
        self.report_generator = Agent(
            llm=self.llm,
            role="Report Summary Generator",
            goal="Convert emission data into human-readable summaries",
            backstory="You are a skilled analyst who can take raw emissions data and transform it "
                     "into clear, concise summaries that highlight key trends, areas of concern, "
                     "and opportunities for improvement. You make complex data accessible to "
                     "non-technical stakeholders.",
            allow_delegation=False,
            verbose=False
        )
        
        # Carbon Offset Advisor
        self.offset_advisor = Agent(
            llm=self.llm,
            role="Carbon Offset Advisor",
            goal="Suggest verified offset options based on user profile and location",
            backstory="You are a sustainability expert who understands the carbon offset market "
                     "and can recommend high-quality, verified offset projects that align with "
                     "the user's industry, values, and location. You help users navigate the "
                     "complex world of carbon credits and offsets.",
            allow_delegation=False,
            verbose=False
        )
        
        # Regulation Radar
        self.regulation_radar = Agent(
            llm=self.llm,
            role="Regulation Radar",
            goal="Notify users of upcoming compliance requirements",
            backstory="You are a regulatory expert who tracks carbon-related regulations across "
                     "different regions, with a focus on EU CBAM, Japan GX League, and Indonesia "
                     "ETS/ETP. You help users understand what compliance requirements apply to "
                     "them and how to prepare for upcoming changes.",
            allow_delegation=False,
            verbose=False
        )
        
        # Emission Optimizer
        self.emission_optimizer = Agent(
            llm=self.llm,
            role="Emission Optimizer",
            goal="Use historical data to suggest reductions and savings",
            backstory="You are a carbon reduction specialist who analyzes emissions data to "
                     "identify patterns and opportunities for reduction. You provide practical, "
                     "actionable recommendations that can help organizations reduce their "
                     "carbon footprint while also saving costs.",
            allow_delegation=False,
            verbose=False
        )
    
    def create_data_entry_task(self, data_description):
        """Create a task for the Data Entry Assistant."""
        return Task(
            description=(
                f"Analyze the following data and help classify it into the appropriate "
                f"emission scope and category: {data_description}\n"
                f"1. Determine if this is Scope 1, 2, or 3\n"
                f"2. Suggest the most appropriate category\n"
                f"3. Recommend an appropriate emission factor if possible\n"
                f"4. Validate the data for completeness and accuracy"
            ),
            expected_output="A detailed classification of the emissions data with scope, "
                           "category, and recommended emission factor.",
            agent=self.data_entry_assistant
        )
    
    def create_report_summary_task(self, emissions_data):
        """Create a task for the Report Summary Generator."""
        return Task(
            description=(
                f"Generate a comprehensive summary of the following emissions data: "
                f"{emissions_data}\n"
                f"1. Highlight key trends and patterns\n"
                f"2. Identify the largest sources of emissions\n"
                f"3. Compare performance across different time periods if data is available\n"
                f"4. Suggest areas for potential improvement"
            ),
            expected_output="A clear, concise summary of the emissions data with key insights "
                           "and recommendations.",
            agent=self.report_generator
        )
    
    def create_offset_advice_task(self, emissions_total, location, industry):
        """Create a task for the Carbon Offset Advisor."""
        return Task(
            description=(
                f"Recommend carbon offset options for an organization with the following profile:\n"
                f"- Total emissions: {emissions_total} kgCO2e\n"
                f"- Location: {location}\n"
                f"- Industry: {industry}\n"
                f"1. Suggest 3-5 verified offset projects that would be suitable\n"
                f"2. Provide estimated costs for offsetting their emissions\n"
                f"3. Explain the benefits and limitations of each option\n"
                f"4. Recommend a balanced portfolio approach if appropriate"
            ),
            expected_output="A list of recommended carbon offset options with costs, benefits, "
                           "and limitations for each.",
            agent=self.offset_advisor
        )
    
    def create_regulation_check_task(self, location, industry, export_markets):
        """Create a task for the Regulation Radar."""
        return Task(
            description=(
                f"Analyze the regulatory requirements for an organization with the following profile:\n"
                f"- Location: {location}\n"
                f"- Industry: {industry}\n"
                f"- Export markets: {export_markets}\n"
                f"1. Identify current compliance requirements related to carbon emissions\n"
                f"2. Highlight upcoming regulatory changes in the next 1-2 years\n"
                f"3. Assess the potential impact of these regulations on the organization\n"
                f"4. Recommend preparation steps to ensure compliance"
            ),
            expected_output="A comprehensive overview of current and upcoming regulatory "
                           "requirements with recommendations for compliance preparation.",
            agent=self.regulation_radar
        )
    
    def create_optimization_task(self, emissions_data):
        """Create a task for the Emission Optimizer."""
        return Task(
            description=(
                f"Analyze the following emissions data and identify opportunities for reduction: "
                f"{emissions_data}\n"
                f"1. Identify the top 3-5 sources of emissions that could be reduced\n"
                f"2. Suggest practical measures to reduce emissions in each area\n"
                f"3. Estimate potential emission reductions and cost savings where possible\n"
                f"4. Prioritize recommendations based on impact and feasibility"
            ),
            expected_output="A prioritized list of emission reduction opportunities with "
                           "estimated impacts and implementation guidance.",
            agent=self.emission_optimizer
        )
    
    def run_data_entry_crew(self, data_description):
        """Run a crew with the Data Entry Assistant."""
        task = self.create_data_entry_task(data_description)
        crew = Crew(
            agents=[self.data_entry_assistant],
            tasks=[task],
            verbose=False
        )
        return crew.kickoff()
    
    def run_report_summary_crew(self, emissions_data):
        """Run a crew with the Report Summary Generator."""
        task = self.create_report_summary_task(emissions_data)
        crew = Crew(
            agents=[self.report_generator],
            tasks=[task],
            verbose=False
        )
        return crew.kickoff()
    
    def run_offset_advice_crew(self, emissions_total, location, industry):
        """Run a crew with the Carbon Offset Advisor."""
        task = self.create_offset_advice_task(emissions_total, location, industry)
        crew = Crew(
            agents=[self.offset_advisor],
            tasks=[task],
            verbose=False
        )
        return crew.kickoff()
    
    def run_regulation_check_crew(self, location, industry, export_markets):
        """Run a crew with the Regulation Radar."""
        task = self.create_regulation_check_task(location, industry, export_markets)
        crew = Crew(
            agents=[self.regulation_radar],
            tasks=[task],
            verbose=False
        )
        return crew.kickoff()
    
    def run_optimization_crew(self, emissions_data):
        """Run a crew with the Emission Optimizer."""
        task = self.create_optimization_task(emissions_data)
        crew = Crew(
            agents=[self.emission_optimizer],
            tasks=[task],
            verbose=False
        )
        return crew.kickoff()
