"""Base AI Agent implementation using LangChain"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import json

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

from ..core.config import config
from ..core.logger import logger


class BaseEdgeAgent(ABC):
    """Base class for edge AI agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = ChatOpenAI(
            openai_api_key=config.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._initialize_tools()
        self.agent_executor = self._create_agent()
        
    @abstractmethod
    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize agent-specific tools"""
        pass
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor"""
        # System prompt for the agent
        system_prompt = f"""
        You are {self.name}, {self.description}.
        
        You have access to various tools to interact with edge devices, particularly air conditioning systems.
        
        Key capabilities:
        - Monitor device status and health
        - Control device operations (power, temperature, mode, fan speed)
        - Implement energy-efficient strategies
        - Respond to user queries about device status
        - Execute automation policies
        
        Always provide clear, helpful responses and explain your actions.
        When controlling devices, prioritize safety and energy efficiency.
        If you encounter errors, provide helpful troubleshooting information.
        """
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user message and return response"""
        try:
            # Add context if provided
            if context:
                context_str = f"Context: {json.dumps(context, indent=2)}\n\n"
                message = context_str + message
            
            # Execute agent
            result = await self.agent_executor.ainvoke({
                "input": message,
                "chat_history": self.memory.chat_memory.messages
            })
            
            response = result.get("output", "I apologize, but I couldn't process your request.")
            
            logger.info(f"Agent {self.name} processed message: {message[:100]}...")
            logger.debug(f"Agent response: {response}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            return f"I encountered an error while processing your request: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        logger.info(f"Cleared memory for agent {self.name}")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        messages = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                messages.append({"role": "human", "content": message.content})
            elif isinstance(message, SystemMessage):
                messages.append({"role": "system", "content": message.content})
            else:
                messages.append({"role": "assistant", "content": message.content})
        return messages