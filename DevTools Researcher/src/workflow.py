from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl_service import FirecrawlService
from .prompts import DeveloperToolsPrompts

from typing import Dict, Any


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()


    def _build_workflow(self):
        graph = StateGraph(ResearchState)

        graph.add_node("extract_tools", self._extract_tools)
        graph.add_node("research", self._research)
        graph.add_node("analyze", self._analyze)
        graph.set_entry_point("extract_tools")

        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)

        return graph.compile()


    def _extract_tools(self, state: ResearchState) -> Dict[str, Any]:
        print(f"*Finding articles about: {state.query}*")

        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.firecrawl.search_companies(query=article_query, limit=3)

        all_pages = []
        for result in search_results.data:
            url = result.get("url", "")
            url_content = self.firecrawl.scrape_page(url)
            all_pages.append(url_content[:1500])

        content = "\n\n".join(all_pages)

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(query=state.query, content=content)),
        ]

        response = self.llm.invoke(messages)
        tool_names = [
            name
            for name in response.content.strip().split("\n")
            if name
        ]
        print(f"Extracted tools: {', '.join(tool_names)}")
        return {"extracted_tools": tool_names}


    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name=company_name, content=content)),
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[]
            )


    def _research(self, state: ResearchState) -> Dict[str, Any]:
        tool_names = getattr(state, "extracted_tools", [])

        if not tool_names:
            print("Not found any tools, falling back to direct search")
            research_results = self.firecrawl.search_companies(query=state.query, limit=3)
            tool_names = [
                result.get("metadata", {}).get("name", "")
                for result in research_results.data
            ]
        print(f"Researching specific tools: {', '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site", limit=1)

            if tool_search_results:
                print(tool_search_results)
                result = tool_search_results.data[0]
                url = result.get("url", "")
                company = CompanyInfo(
                    name=tool_name,
                    description=result.get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                scraped = self.firecrawl.scrape_page(url)
                content = scraped.markdown
                analysis = self._analyze_company_content(company_name=company.name, content=content)

                company.description = analysis.description
                company.pricing_model = analysis.pricing_model
                company.is_open_source = analysis.is_open_source
                company.tech_stack = analysis.tech_stack
                company.competitors = analysis.competitors
                company.api_available = analysis.api_available
                company.language_support = analysis.language_support
                company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}


    def _analyze(self, state: ResearchState) -> Dict[str, Any]:
        print("Generating recommendations")
        company_data = ", ".join(
            [
                company.model_dump_json() for company in state.companies
            ]
        )

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(query=state.query, company_data=company_data)),
        ]

        response = self.llm.invoke(messages)
        return {"analysis": response.content}


    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query.strip())
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)