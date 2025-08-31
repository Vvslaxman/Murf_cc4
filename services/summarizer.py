"""
Summarization Service - Uses LangChain to summarize and filter social media content
Supports multiple LLM providers and local models
"""
from dotenv import load_dotenv
load_dotenv()
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

@dataclass
class SummarizationConfig:
    """Configuration for summarization"""
    max_length: int = 200
    min_length: int = 50
    use_local_model: bool = False
    local_model_name: str = "facebook/bart-large-cnn"
    temperature: float = 0.7
    provider: str = "openai"  # openai, cohere, local

class ContentFilter:
    """Filters out low-quality content"""
    
    @staticmethod
    def is_spam(text: str) -> bool:
        """Check if text is spam or low-value content"""
        # Convert to lowercase for easier matching
        text_lower = text.lower().strip()
        
        # Very short messages
        if len(text_lower) < 5:
            return True
        
        # Common spam patterns
        spam_patterns = [
            r'^ok$', r'^k$', r'^yes$', r'^no$', r'^haha$', r'^lol$', r'^lmao$',
            r'^thanks$', r'^thx$', r'^ty$', r'^cool$', r'^nice$', r'^wow$',
            r'^\?+$', r'^!+$', r'^\.+$',  # Just punctuation
            r'^[😀-🙏🌀-🗿]+$',  # Just emojis
            r'^[a-z]{1,3}$',  # Very short words
        ]
        
        for pattern in spam_patterns:
            if re.match(pattern, text_lower):
                return True
        
        # Check if it's mostly emojis
        emoji_count = len(re.findall(r'[😀-🙏🌀-🗿]', text))
        if emoji_count > len(text) * 0.5:  # More than 50% emojis
            return True
        
        return False
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions (@username)
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags but keep the text
        text = re.sub(r'#(\w+)', r'\1', text)
        
        return text.strip()

class SummarizerService:
    """Main summarization service"""
    
    def __init__(self, config: SummarizationConfig):
        self.config = config
        self.local_model = None
        self.llm_chain = None
        self._setup_model()
    
    def _setup_model(self):
        """Setup the appropriate model based on configuration"""
        if self.config.use_local_model:
            self._setup_local_model()
        else:
            self._setup_cloud_model()
    
    def _setup_local_model(self):
        """Setup local transformer model"""
        try:
            self.local_model = pipeline(
                "summarization",
                model=self.config.local_model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Loaded local model: {self.config.local_model_name}")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            # Fallback to cloud model
            self.config.use_local_model = False
            self._setup_cloud_model()
    
    def _setup_cloud_model(self):
        """Setup cloud-based LLM"""
        if self.config.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required for cloud summarization")
            
            llm = ChatOpenAI(
                model_name="gpt-4o-mini",
                temperature=self.config.temperature,
                max_tokens=self.config.max_length
            )
        else:
            # Fallback to OpenAI
            llm = ChatOpenAI(
                model_name="gpt-4o-mini",
                temperature=self.config.temperature,
                max_tokens=self.config.max_length
            )
        
        # Create summarization prompt
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
            Summarize the following social media post into a clear, concise sentence suitable for text-to-speech narration.
            Focus on the main message and make it conversational.
            
            Post: {text}
            
            Summary:"""
        )
        
        self.llm_chain = LLMChain(llm=llm, prompt=prompt_template)
        logger.info(f"Setup cloud model: {self.config.provider}")
    
    def summarize_text(self, text: str) -> Optional[str]:
        """
        Summarize text using the configured model
        Returns None if text should be filtered out
        """
        # Clean the text
        cleaned_text = ContentFilter.clean_text(text)
        
        # Check if it's spam
        if ContentFilter.is_spam(cleaned_text):
            logger.info(f"Filtered out spam content: {cleaned_text[:50]}...")
            return None
        
        # Check length limits
        if len(cleaned_text) < int(os.getenv("MIN_POST_LENGTH", "10")):
            return None
        
        if len(cleaned_text) > int(os.getenv("MAX_POST_LENGTH", "1000")):
            # Truncate if too long
            cleaned_text = cleaned_text[:int(os.getenv("MAX_POST_LENGTH", "1000"))]
        
        try:
            if self.config.use_local_model and self.local_model:
                return self._summarize_local(cleaned_text)
            else:
                return self._summarize_cloud(cleaned_text)
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Fallback to simple summarization
            return self._simple_summarize(cleaned_text)
    
    def _simple_summarize(self, text: str) -> str:
        """Simple summarization without heavy models"""
        # Take first sentence or first 100 characters
        sentences = text.split('. ')
        if sentences:
            summary = sentences[0]
            if not summary.endswith('.'):
                summary += '.'
            
            # Limit length
            if len(summary) > 150:
                summary = summary[:147] + '...'
            
            return summary
        
        # Fallback to truncation
        if len(text) > 150:
            return text[:147] + '...'
        return text
    
    def _summarize_local(self, text: str) -> str:
        """Summarize using local transformer model"""
        result = self.local_model(
            text,
            max_length=self.config.max_length,
            min_length=self.config.min_length,
            do_sample=True,
            temperature=self.config.temperature
        )
        return result[0]['summary_text']
    
    def _summarize_cloud(self, text: str) -> str:
        """Summarize using cloud LLM"""
        result = self.llm_chain.run(text=text)
        return result.strip()
    
    def batch_summarize(self, texts: List[str]) -> List[Optional[str]]:
        """Summarize multiple texts in batch"""
        results = []
        for text in texts:
            summary = self.summarize_text(text)
            results.append(summary)
        return results
    
    def prioritize_content(self, texts: List[str]) -> List[Dict]:
        """
        Prioritize content based on importance
        Returns list of dicts with text, priority, and summary
        """
        prioritized = []
        
        for text in texts:
            summary = self.summarize_text(text)
            if summary:
                # Calculate priority score
                priority = self._calculate_priority(text, summary)
                
                prioritized.append({
                    "original_text": text,
                    "summary": summary,
                    "priority": priority,
                    "length": len(text)
                })
        
        # Sort by priority (highest first)
        prioritized.sort(key=lambda x: x["priority"], reverse=True)
        return prioritized
    
    def _calculate_priority(self, text: str, summary: str) -> float:
        """Calculate priority score for content"""
        score = 0.0
        
        # Length factor (moderate length is good)
        length = len(text)
        if 50 <= length <= 300:
            score += 2.0
        elif length > 300:
            score += 1.0
        
        # Keyword importance
        important_keywords = [
            "job", "career", "opportunity", "hiring", "position",
            "ai", "artificial intelligence", "machine learning",
            "event", "meeting", "conference", "workshop",
            "update", "announcement", "news", "important",
            "deadline", "urgent", "critical"
        ]
        
        text_lower = text.lower()
        for keyword in important_keywords:
            if keyword in text_lower:
                score += 1.0
        
        # Question factor (questions might be important)
        if "?" in text:
            score += 0.5
        
        # Engagement indicators
        engagement_words = ["please", "help", "need", "urgent", "important"]
        for word in engagement_words:
            if word in text_lower:
                score += 0.3
        
        return score

# Global instance
summarizer_config = SummarizationConfig(
    max_length=int(os.getenv("SUMMARY_MAX_LENGTH", "200")),
    use_local_model=os.getenv("USE_LOCAL_MODEL", "False").lower() == "true",
    local_model_name=os.getenv("LOCAL_MODEL_NAME", "facebook/bart-large-cnn"),
    provider=os.getenv("SUMMARIZATION_PROVIDER", "openai")
)

summarizer_service = SummarizerService(summarizer_config)

