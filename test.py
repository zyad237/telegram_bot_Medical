"""
Test script for histology PDF integration
"""
import asyncio
from ai_manager import AIManager

async def test_histology_ai():
    print("🧪 Testing Histology AI Integration...")
    
    ai_manager = AIManager()
    
    # Test questions that should be answered from your PDF
    test_questions = [
        "Explain the structure of the cell membrane according to our histology materials",
        "What are the different types of epithelial tissue?",
        "Describe the functions of mitochondria",
        "What is the paraffin technique in histology?",
        "Explain the difference between apoptosis and necrosis"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("🤖 AI is searching college materials...")
        
        try:
            response = await ai_manager.chat_with_ai(
                question, 
                "Student is studying histology", 
                "histology"
            )
            print(f"💡 Response: {response[:200]}...")  # First 200 chars
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_histology_ai())