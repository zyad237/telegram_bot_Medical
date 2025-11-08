"""
AI integration with college PDF context - UPDATED FOR HISTOLOGY
"""
import os
import logging
import requests
import json
import asyncio
from typing import Dict, List, Optional

from pdf_manager import PDFManager
from college_config import COLLEGE_PDFS, get_college_pdf_path

logger = logging.getLogger(__name__)

class AIManager:
    def __init__(self):
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "http://localhost:5001/ai")
        self.pdf_manager = PDFManager()
        
    async def explain_question(self, question_data: Dict, user_question: str, subject: str) -> str:
        """Explain a quiz question using college PDF context"""
        # Get relevant content from college PDFs
        pdf_context = self.pdf_manager.get_subject_context(
            f"{question_data['question']} {user_question}", 
            subject, 
            top_k=3
        )
        
        prompt = f"""
        You are a tutor at our medical college. Use EXCLUSIVELY OUR COLLEGE MATERIALS as reference.
        
        QUESTION: {question_data['question']}
        
        OPTIONS:
        A) {question_data['options'][0]}
        B) {question_data['options'][1]}
        C) {question_data['options'][2]}
        D) {question_data['options'][3]}
        
        CORRECT ANSWER: {question_data['correct']}
        
        STUDENT'S REQUEST: {user_question}
        
        COLLEGE MATERIALS CONTEXT:
        {pdf_context}
        
        CRITICAL INSTRUCTION: Base your explanation SOLELY on our college curriculum and materials provided above. Do not use any external knowledge.
        
        Please provide explanation that:
        1. References our specific college textbook and lecture notes
        2. Explains why correct answer is right based on our teachings
        3. Mentions why other options are incorrect according to our materials
        4. Uses terminology and definitions from our specific curriculum
        5. Cites specific pages or sections when possible
        
        Keep it concise and focused exclusively on our college approach.
        """
        
        return await self._call_ai(prompt, "explain")
    
    async def give_hint(self, question_data: Dict, subject: str) -> str:
        """Give a hint using college PDF context"""
        pdf_context = self.pdf_manager.get_subject_context(
            question_data['question'], subject, top_k=2
        )
        
        prompt = f"""
        Give a helpful hint for this question based EXCLUSIVELY on our COLLEGE CURRICULUM.
        
        QUESTION: {question_data['question']}
        
        COLLEGE CONTEXT:
        {pdf_context}
        
        CRITICAL: Use ONLY the college materials provided above. Do not add external knowledge.
        
        Provide a hint that:
        - References our specific teaching approach from the materials
        - Points to key concepts from our textbook
        - Uses our college's specific terminology
        - Doesn't give away the answer
        - Mentions relevant sections from our curriculum
        
        Make it encouraging and reference our specific resources.
        """
        
        return await self._call_ai(prompt, "hint")
    
    async def evaluate_short_essay(self, question: str, answer: str, subject: str, expected_points: List[str]) -> Dict:
        """Evaluate short essay answers using college standards"""
        pdf_context = self.pdf_manager.get_subject_context(
            f"{question} evaluation criteria", subject, top_k=2
        )
        
        prompt = f"""
        Evaluate this short answer based EXCLUSIVELY on OUR COLLEGE'S STANDARDS and materials.
        
        QUESTION: {question}
        STUDENT ANSWER: {answer}
        EXPECTED POINTS: {expected_points}
        
        COLLEGE GRADING CONTEXT:
        {pdf_context}
        
        CRITICAL: Use ONLY our college materials for evaluation. Do not reference external standards.
        
        Evaluate based on our college criteria:
        - Accuracy according to our curriculum (0-2 points)
        - Completeness covering expected points (0-2 points) 
        - Use of college terminology (0-1 point)
        
        Provide evaluation that references our specific materials and standards.
        
        Format as JSON:
        {{
            "score": 0-5,
            "strengths": ["point1", "point2"],
            "improvements": ["point1", "point2"], 
            "explanation": "brief correct answer from our materials",
            "suggestion": "how to improve based on college standards"
        }}
        """
        
        response = await self._call_ai(prompt, "evaluate")
        try:
            return json.loads(response)
        except:
            return self._create_fallback_evaluation()
    
    async def chat_with_ai(self, user_message: str, context: str, subject: str) -> str:
        """General AI chat using college PDFs"""
        pdf_context = self.pdf_manager.get_subject_context(
            user_message, subject, top_k=3
        )
        
        prompt = f"""
        You are a tutor at our medical college. Answer using EXCLUSIVELY OUR COLLEGE MATERIALS.
        
        STUDENT QUESTION: {user_message}
        CONVERSATION CONTEXT: {context}
        
        COLLEGE MATERIALS CONTEXT:
        {pdf_context}
        
        CRITICAL: Base your answer SOLELY on the college materials provided above. Do not use any external knowledge or information.
        
        Provide answer that:
        - References our specific college materials exclusively
        - Uses terminology from our curriculum
        - Connects to our teaching approach
        - Mentions relevant pages/sources from our PDFs when possible
        - Stays strictly aligned with our college standards
        
        If the information is not found in our college materials, say: "This topic is not covered in our current college materials. Please consult your instructor."
        
        Be helpful and reference our specific resources.
        """
        
        return await self._call_ai(prompt, "chat")
    
    async def search_college_materials(self, query: str, subject: str) -> str:
        """Direct search in college materials"""
        results = self.pdf_manager.search_pdf(query, subject, top_k=3)
        
        if not results:
            return f"❌ No specific information found in college {subject} materials for: '{query}'\n\nPlease check if this topic is covered in your textbook or ask your instructor."
        
        response = f"🔍 **Found in college {subject} materials:**\n\n"
        
        for i, result in enumerate(results, 1):
            response += f"**{i}. {result['source']} (Page {result['page']})**\n"
            response += f"{result['text']}\n\n"
        
        response += "💡 *This information comes exclusively from your college materials.*"
        
        return response
    
    def get_available_college_subjects(self) -> List[str]:
        """Get list of subjects with college PDFs"""
        return self.pdf_manager.list_available_subjects()
    
    def get_subject_pdfs(self, subject: str) -> List[str]:
        """Get PDF files available for a subject"""
        return self.pdf_manager.get_pdf_info(subject)
    
    async def _call_ai(self, prompt: str, action: str) -> str:
        """Call AI service with proper error handling"""
        try:
            payload = {
                "prompt": prompt,
                "action": action,
                "max_tokens": 500
            }
            
            response = requests.post(
                self.ai_service_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "I apologize, but I couldn't process your request.")
            else:
                logger.error(f"AI service error: {response.status_code}")
                return self._get_fallback_response(action)
                
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return self._get_fallback_response(action)
    
    def _get_fallback_response(self, action: str) -> str:
        """Fallback responses when AI is unavailable"""
        fallbacks = {
            "explain": "I'm currently unavailable for explanations. Please consult your college textbook or ask your instructor.",
            "hint": "Try to recall the main concepts from this topic. Review the related chapter in your college textbook.",
            "evaluate": "Evaluation service is temporarily unavailable. Compare your answer with your textbook content.",
            "chat": "I'm currently unavailable. Please check your college textbook or other learning resources."
        }
        return fallbacks.get(action, "Service temporarily unavailable.")
    
    def _create_fallback_evaluation(self) -> Dict:
        """Create fallback evaluation when AI fails"""
        return {
            "score": 3,
            "strengths": ["Answer submitted successfully"],
            "improvements": ["Compare with textbook content for accuracy"],
            "explanation": "Review the key concepts in your college textbook",
            "suggestion": "Focus on understanding the core principles from our materials"
        }