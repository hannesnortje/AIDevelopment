import os
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic # Assuming already installed or we add it
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph_scrum.config import config

def get_llm(agent_config: dict) -> BaseChatModel:
    """
    Factory to create an LLM instance based on configuration.
    
    Args:
        agent_config: Dictionary containing 'provider', 'model', 'temperature', etc.
    
    Returns:
        A LangChain ChatModel instance.
    """
    provider = agent_config.get("provider", "anthropic").lower()
    model_name = agent_config.get("model", "claude-3-5-sonnet-20240620")
    temperature = float(agent_config.get("temperature", 0.7))
    
    print(f"[LLM Factory] Creating {provider} model: {model_name} (temp={temperature})")
    
    if provider == "openai":
        api_key = config.get("OPENAI_API_KEY")
        if not api_key:
            print("[LLM Factory] Warning: OPENAI_API_KEY not found")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
    elif provider == "google":
        api_key = config.get("GOOGLE_API_KEY") # We should add this to config/settings
        if not api_key:
            print("[LLM Factory] Warning: GOOGLE_API_KEY not found")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key
        )
        
    elif provider == "anthropic":
        # We need to ensure langchain-anthropic is installed or use ChatAnthropic from community
        # For now, let's assume we use the standard one
        try:
            from langchain_anthropic import ChatAnthropic
            api_key = config.get("ANTHROPIC_API_KEY")
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                api_key=api_key
            )
        except ImportError:
            print("[LLM Factory] langchain-anthropic not installed, falling back to mock/error")
            raise ImportError("Please install langchain-anthropic")

    else:
        # Fallback or Mock
        print(f"[LLM Factory] Unknown provider {provider}, returning OpenAI default")
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
