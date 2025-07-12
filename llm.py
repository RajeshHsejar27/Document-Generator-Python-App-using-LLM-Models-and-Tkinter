"""
LLM Module - Local Language Model Integration
Handles loading and interaction with local GPT4All models for text summarization and detailed note expansion.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import GPT4All, handle gracefully if not available
try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    logger.warning("GPT4All not available. Install with: pip install gpt4all")


class LLMManager:
    """Manages local language model operations for text summarization and detailed note generation."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model = None
        self.model_name = model_name
        self.models_dir = os.path.join(os.path.dirname(__file__), 'models')
        self._load_model()
    
    def _find_model_file(self) -> Optional[str]:
        """Find the first available .gguf model file."""
        if not os.path.exists(self.models_dir):
            logger.error(f"Models directory not found: {self.models_dir}")
            return None
        
        # Look for .gguf files
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.gguf')]
        
        if not model_files:
            logger.error("No .gguf model files found in models directory")
            return None
        
        # If specific model name provided, look for it
        if self.model_name:
            for model_file in model_files:
                if self.model_name.lower() in model_file.lower():
                    return os.path.join(self.models_dir, model_file)
        
        # Return first available model
        selected_model = model_files[0]
        logger.info(f"Using model: {selected_model}")
        return os.path.join(self.models_dir, selected_model)
    
    def _load_model(self):
        """Load the GPT4All model."""
        if not GPT4ALL_AVAILABLE:
            logger.warning("GPT4All not available, using fallback processing")
            return
        
        model_path = self._find_model_file()
        if not model_path:
            logger.error("No model file found, using fallback processing")
            return
        
        try:
            logger.info(f"Loading model from: {model_path}")
            self.model = GPT4All(model_path, allow_download=False)
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    def generate_summary(self, text: str, max_tokens: int = 150) -> str:
        """
        Generate a summary of the input text using the local LLM.
        
        Args:
            text: Input text to summarize
            max_tokens: Maximum number of tokens in the summary
            
        Returns:
            Generated summary text
        """
        if not text.strip():
            return "No notes provided."
        
        # Use local model if available
        if self.model and GPT4ALL_AVAILABLE:
            return self._generate_ai_summary(text, max_tokens)
        else:
            return self._generate_fallback_summary(text)
    
    def generate_detailed_notes(self, text: str, max_tokens: int = 500) -> str:
        """
        Generate detailed, expanded version of the input notes using the local LLM.
        
        Args:
            text: Input text to expand
            max_tokens: Maximum number of tokens in the detailed notes
            
        Returns:
            Generated detailed notes
        """
        if not text.strip():
            return "No notes provided to expand."
        
        # Use local model if available
        if self.model and GPT4ALL_AVAILABLE:
            return self._generate_ai_detailed_notes(text, max_tokens)
        else:
            return self._generate_fallback_detailed_notes(text)
    
    def _generate_ai_summary(self, text: str, max_tokens: int) -> str:
        """Generate summary using the local LLM."""
        try:
            # Create a focused prompt for summarization
            prompt = f"""Please summarize the following daily notes in 2-3 concise sentences. Focus on the key activities and outcomes:

{text}

Summary:"""
            
            logger.info("Generating AI summary...")
            
            # Generate response with the model
            with self.model.chat_session():
                response = self.model.generate(
                    prompt,
                    max_tokens=max_tokens,
                    temp=0.3,  # Lower temperature for more consistent summaries
                    top_p=0.9,
                    repeat_penalty=1.1
                )
            
            # Clean up the response
            summary = response.strip()
            
            # Remove any remaining prompt text
            if "Summary:" in summary:
                summary = summary.split("Summary:")[-1].strip()
            
            # Ensure we have content
            if not summary:
                return self._generate_fallback_summary(text)
            
            logger.info("AI summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return self._generate_fallback_summary(text)
    
    def _generate_ai_detailed_notes(self, text: str, max_tokens: int) -> str:
        """Generate detailed notes using the local LLM."""
        try:
            # Create a focused prompt for detailed note expansion
            prompt = f"""Please expand the following brief daily notes into a detailed, professional documentation. Add context, elaborate on activities, include potential outcomes and next steps. Maintain a professional tone suitable for work documentation:

Brief Notes:
{text}

Detailed Documentation:"""
            
            logger.info("Generating detailed AI notes...")
            
            # Generate response with the model
            with self.model.chat_session():
                response = self.model.generate(
                    prompt,
                    max_tokens=max_tokens,
                    temp=0.4,  # Slightly higher temperature for more creative expansion
                    top_p=0.9,
                    repeat_penalty=1.1
                )
            
            # Clean up the response
            detailed_notes = response.strip()
            
            # Remove any remaining prompt text
            if "Detailed Documentation:" in detailed_notes:
                detailed_notes = detailed_notes.split("Detailed Documentation:")[-1].strip()
            
            # Ensure we have content
            if not detailed_notes:
                return self._generate_fallback_detailed_notes(text)
            
            logger.info("AI detailed notes generated successfully")
            return detailed_notes
            
        except Exception as e:
            logger.error(f"Error generating AI detailed notes: {e}")
            return self._generate_fallback_detailed_notes(text)
    
    def _generate_fallback_summary(self, text: str) -> str:
        """Generate a simple extractive summary when AI model is not available."""
        logger.info("Using fallback summary generation")
        
        # Split text into sentences
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
        
        if not sentences:
            return "Daily activities were documented."
        
        # If only one sentence, return it
        if len(sentences) == 1:
            return sentences[0] + "."
        
        # For multiple sentences, take the first two meaningful ones
        meaningful_sentences = []
        for sentence in sentences[:5]:  # Look at first 5 sentences
            if len(sentence.split()) >= 3:  # At least 3 words
                meaningful_sentences.append(sentence)
            if len(meaningful_sentences) >= 2:
                break
        
        if meaningful_sentences:
            summary = ". ".join(meaningful_sentences) + "."
        else:
            summary = f"Today involved {len(sentences)} documented activities and tasks."
        
        return summary
    
    def _generate_fallback_detailed_notes(self, text: str) -> str:
        """Generate expanded notes when AI model is not available."""
        logger.info("Using fallback detailed notes generation")
        
        # Split text into lines and expand each
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return "No activities to expand upon."
        
        detailed_lines = []
        
        for i, line in enumerate(lines, 1):
            # Remove bullet points for processing
            clean_line = line.lstrip('•-* ').strip()
            
            if not clean_line:
                continue
            
            # Add context and structure to each line
            if len(clean_line.split()) < 5:  # Short line, expand more
                expanded = f"**Activity {i}:** {clean_line}. This task involved careful planning and execution, contributing to the overall project objectives. The completion of this activity helps maintain project momentum and ensures quality deliverables."
            else:  # Longer line, add moderate expansion
                expanded = f"**Activity {i}:** {clean_line}. This represents a significant milestone in the daily workflow, requiring coordination and attention to detail."
            
            detailed_lines.append(expanded)
        
        # Add a general conclusion
        conclusion = f"\n**Daily Overview:** Today's activities encompassed {len(detailed_lines)} key areas of focus, each contributing to broader project goals and professional development. The documented tasks reflect a productive day with meaningful progress across multiple initiatives."
        
        return '\n\n'.join(detailed_lines) + conclusion
    
    def enhance_notes_with_context(self, text: str, context_type: str = "professional") -> str:
        """
        Enhance notes with additional context and formatting.
        
        Args:
            text: Input text to enhance
            context_type: Type of context to add ("professional", "personal", "technical")
            
        Returns:
            Enhanced notes with context
        """
        if not text.strip():
            return "No notes provided to enhance."
        
        if self.model and GPT4ALL_AVAILABLE:
            return self._generate_ai_enhanced_notes(text, context_type)
        else:
            return self._generate_fallback_enhanced_notes(text, context_type)
    
    def _generate_ai_enhanced_notes(self, text: str, context_type: str) -> str:
        """Generate enhanced notes with context using AI."""
        try:
            context_prompts = {
                "professional": "Transform these notes into professional documentation suitable for workplace reporting. Add business context and implications.",
                "personal": "Expand these notes with personal reflection and learning insights. Focus on growth and development aspects.",
                "technical": "Enhance these notes with technical details and implementation considerations. Include potential challenges and solutions."
            }
            
            prompt = f"""{context_prompts.get(context_type, context_prompts['professional'])}

Original Notes:
{text}

Enhanced Notes:"""
            
            logger.info(f"Generating AI enhanced notes with {context_type} context...")
            
            with self.model.chat_session():
                response = self.model.generate(
                    prompt,
                    max_tokens=400,
                    temp=0.4,
                    top_p=0.9,
                    repeat_penalty=1.1
                )
            
            enhanced_notes = response.strip()
            
            if "Enhanced Notes:" in enhanced_notes:
                enhanced_notes = enhanced_notes.split("Enhanced Notes:")[-1].strip()
            
            if not enhanced_notes:
                return self._generate_fallback_enhanced_notes(text, context_type)
            
            logger.info("AI enhanced notes generated successfully")
            return enhanced_notes
            
        except Exception as e:
            logger.error(f"Error generating AI enhanced notes: {e}")
            return self._generate_fallback_enhanced_notes(text, context_type)
    
    def _generate_fallback_enhanced_notes(self, text: str, context_type: str) -> str:
        """Generate enhanced notes when AI model is not available."""
        logger.info(f"Using fallback enhanced notes generation with {context_type} context")
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return "No activities to enhance."
        
        context_templates = {
            "professional": {
                "prefix": "**Professional Activity:**",
                "suffix": "This activity aligns with organizational objectives and demonstrates professional competency."
            },
            "personal": {
                "prefix": "**Personal Development:**",
                "suffix": "This experience contributes to personal growth and skill development."
            },
            "technical": {
                "prefix": "**Technical Implementation:**",
                "suffix": "This task required technical expertise and problem-solving capabilities."
            }
        }
        
        template = context_templates.get(context_type, context_templates["professional"])
        enhanced_lines = []
        
        for line in lines:
            clean_line = line.lstrip('•-* ').strip()
            if clean_line:
                enhanced = f"{template['prefix']} {clean_line}. {template['suffix']}"
                enhanced_lines.append(enhanced)
        
        return '\n\n'.join(enhanced_lines)
    
    def is_model_available(self) -> bool:
        """Check if a local model is available and loaded."""
        return self.model is not None and GPT4ALL_AVAILABLE
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        if not self.is_model_available():
            return {
                "status": "No model loaded",
                "model_path": None,
                "gpt4all_available": GPT4ALL_AVAILABLE
            }
        
        return {
            "status": "Model loaded",
            "model_path": self._find_model_file(),
            "gpt4all_available": GPT4ALL_AVAILABLE
        }