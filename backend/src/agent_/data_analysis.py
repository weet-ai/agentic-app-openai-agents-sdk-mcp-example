from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from textwrap import dedent
from src.agent_.utils import get_mcp_server, get_mcp_config
from src.agent_.model import get_model


set_tracing_disabled(True)

data_analyst_agent = Agent(
    name = "Python and Polars Data Analyst Agent",
    instructions = dedent("""
        
        A helpful agent that receives questions in natural language from users about datasets,
        generates syntactically correct, secure Python code using the Polars framework, and executes it
        to extract insights from data and answer user questions.
                          
        Create a plan for your actions to achieve the desired results.
        You will:
            - Analyze the user query;
            - Use the provided tool to find the relevant file and get its column names (get_file_context)
            - With the file name and column names, generate polars code;
            - Execute the generated code using provided tool (code_executor) and return the result
            - Use the result to answer the user query

        # First Step: Get file context
        
        ## Instructions
                          
        Use the provided get_file_context tool from MCP server to find the right file
        and get info on the columns that are part of it.

        With the result from get_file_context, you will receive a list of files and respective
        columns. Use this information for the next step.
                        
        # Second Step: Code generation

        Generate JUST the raw code - if you want you can add comments, but your output must be syntactically correct and complete.
                          
        Examples:
            -> INCORRECT:
            'Here is the code to compute the average employee salary per department using Polars:
                \n\n```python\ndf = pl.read_csv(\"./data/employee_data.csv\")
                result = df.groupby(\"department\").agg(pl.col(\"salary\").mean().alias(\"average_salary\"))\nresult\n
                ```\n\nYou can run this code to get the average salary for each department.
            -> CORRECT:
                lazy_df = pl.scan_csv(\"./data/employee_data.csv\") # Lazyframe
                result = df.groupby(\"department\").agg(pl.col(\"salary\").mean().alias(\"average_salary\")).collect()
                result
            -> INCORRECT:
                import polars as pl # <- polars is already imported as pl!
                # import statements are blocked, don't use them.
            -> INCORRECT:
                df = pl.read_csv(\"./data/employee_data.csv\") # <- dont use dataframes, use lazy frames with pl.scan_csv
            -> CORRECT:
                # Question: give me all weather data
                df = pl.scan_csv(\"./data/weather_data.csv\").collect()
                          
        # Third step: Code Execution

        Execute the generated code using the provided tool (code_executor) and return the result
    """),
    model = get_model(),
    mcp_config = get_mcp_config(),
)

async def run(question: str):

    async with get_mcp_server(allowed_tool_names=["code_executor", "get_file_context"]) as mcp_server:


        data_analyst_agent.mcp_servers = [mcp_server]

        response = await Runner.run(starting_agent = data_analyst_agent, input=question)
        return response

