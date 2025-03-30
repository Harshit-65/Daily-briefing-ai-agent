import os
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI
from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions
import tiktoken

load_dotenv()

class BriefingAgent:
    def __init__(self):
        self.pica_client = PicaClient(
            secret=os.getenv("PICA_SECRET_KEY"),
            options=PicaClientOptions(connectors=["*"])
        )
       
        self.llm = ChatOpenAI(
            temperature=0.2,
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=1000
        )
       
        self.agent = create_pica_agent(
            client=self.pica_client,
            llm=self.llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    def count_tokens(self, text, model="gpt-4o"):
        """Count the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
   
    def generate_briefing(self, traffic_info=None):
        """Generate a daily briefing by collecting and processing data from various sources."""
        
        input_prompt = f"""
        You will create a daily briefing and send it to Slack. Follow these steps:

        STEP 1: Collect information
        - Fetch the latest 3 AI technology news headlines using NewsData.io.
          Use these parameters: category=technology, query=AI, language=en, limit=3
        
        - Get the current weather for Pune, India.
        
        """

        # Add traffic information if available
        if traffic_info:
            input_prompt += f"""
        - Include this traffic information for my commute:
          Distance: {traffic_info['distance']}
          Current duration with traffic: {traffic_info['duration_in_traffic']}
          {traffic_info['traffic_delay']}
        """
        else:
            input_prompt += f"""
        - Calculate the current traffic conditions for my commute from {os.getenv('HOME_ADDRESS')}
          to {os.getenv('OFFICE_ADDRESS')}.
        """

        input_prompt += f"""
        STEP 2: Format the briefing
        - Create a concise daily briefing with all the information collected.
        - Format it as a conversational script that sounds natural when read aloud.
        - Keep it very concise but informative, with a friendly tone.
        - Limit the total briefing to 300 words maximum.
        - DO NOT include any URLs, links, or markdown formatting.
        - DO NOT use bullet points, numbered lists, or any special characters.
        - DO NOT include [Read more] or similar link text.
        - Present the news as simple statements without references to sources.
        - Use plain text only - this will be converted to speech.
        - End with a positive, motivational note.

        STEP 3: Send to Slack
        - Send the briefing to Slack.
        - Use this connection key: {os.getenv('SLACK_CHANNEL_CONNECTION_KEY')}
        - Send to this channel ID: {os.getenv('SLACK_CHANNEL_ID')}
        - Include a simple header: "Daily Briefing for {datetime.now().strftime('%A, %B %d, %Y')}"
        
        STEP 4: Return the briefing text
        - After sending to Slack, return ONLY the briefing text (without the Slack confirmation).
        - This text will be used for text-to-speech conversion.
        """

        # Check token count and simplify if needed
        token_count = self.count_tokens(input_prompt)
        if token_count > 4000:
            input_prompt = f"""
            Create a very brief daily summary with:
            1. One AI news headline from NewsData.io
            2. Current weather for {os.getenv('HOME_ADDRESS')}
            3. Basic traffic info for commute from {os.getenv('HOME_ADDRESS')} to {os.getenv('OFFICE_ADDRESS')}
            
            Format as plain text, no links or markdown. Keep it under 200 words.
            
            Then send it to Slack channel ID {os.getenv('SLACK_CHANNEL_ID')} using connection key {os.getenv('SLACK_CHANNEL_CONNECTION_KEY')}.
            
            Return ONLY the briefing text for text-to-speech conversion.
            """

        result = self.agent.invoke({"input": input_prompt})
        
        return result["output"]


