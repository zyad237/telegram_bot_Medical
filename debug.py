#!/usr/bin/env python3
"""
Debug script to check file discovery
"""
import os
from config import CONFIG, TOPIC_DISPLAY_NAMES, SUBPROJECT_DISPLAY_NAMES
from telegram import Update
print("🔍 DEBUG FILE DISCOVERY")
print("=" * 50)

# Check data directory
data_dir = CONFIG["data_dir"]
print(f"Data directory: {data_dir}")
print(f"Exists: {os.path.exists(data_dir)}")

if os.path.exists(data_dir):
    print(f"Contents: {os.listdir(data_dir)}")

print("\n📊 CONFIGURATION CHECK")
print("=" * 50)
print(f"TOPIC_DISPLAY_NAMES: {TOPIC_DISPLAY_NAMES}")
print(f"SUBPROJECT_DISPLAY_NAMES: {SUBPROJECT_DISPLAY_NAMES}")

print("\n📁 FILE STRUCTURE CHECK")
print("=" * 50)
for topic in TOPIC_DISPLAY_NAMES:
    topic_path = os.path.join(data_dir, topic)
    print(f"\nTopic: {topic}")
    print(f"Path: {topic_path}")
    print(f"Exists: {os.path.exists(topic_path)}")
    
    if os.path.exists(topic_path):
        files = os.listdir(topic_path)
        print(f"Files: {files}")
        
        for file in files:
            if file.endswith('.csv'):
                subtopic = file[:-4]
                print(f"  CSV: {file} -> subtopic: '{subtopic}'")
                if topic in SUBPROJECT_DISPLAY_NAMES:
                    if subtopic in SUBPROJECT_DISPLAY_NAMES[topic]:
                        print(f"    ✅ IN CONFIG")
                    else:
                        print(f"    ❌ NOT IN CONFIG")
async def send_next_question(self, update: Update, context: CallbackContext):
    """Send the next question in the quiz"""
    user_data = context.user_data
    
    print(f"🔍 SEND_NEXT_QUESTION called")
    print(f"   Quiz active: {user_data.get('quiz_active')}")
    print(f"   Current question: {user_data.get('current_question')}")
    print(f"   Total questions: {len(user_data.get('questions', []))}")
    
    if not user_data.get("quiz_active"):
        print(f"❌ Quiz not active - returning")
        return
    
    current_index = user_data["current_question"]
    questions = user_data["questions"]
    chat_id = user_data["chat_id"]
    
    if current_index >= len(questions):
        print(f"🎯 Quiz finished - calling finish_quiz")
        await self.finish_quiz(update, context)
        return
    
    print(f"📝 Sending question {current_index + 1}/{len(questions)}")
    
    original_question = questions[current_index]
    shuffled_question = self.shuffle_choices(original_question)
    user_data["current_shuffled"] = shuffled_question
    
    progress = f"Question {current_index + 1}/{len(questions)}\n\n"
    question_text = progress + shuffled_question["question"]
    
    try:
        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question_text,
            options=shuffled_question["options"],
            type="quiz",
            correct_option_id=shuffled_question["correct_index"],
            is_anonymous=False,
        )
        
        user_data["active_poll_id"] = message.poll.id
        user_data["poll_message_id"] = message.message_id
        
        print(f"✅ Question {current_index + 1} sent successfully")
        print(f"   Poll ID: {message.poll.id}")
        print(f"   Message ID: {message.message_id}")
        
    except Exception as e:
        print(f"❌ Error sending question {current_index + 1}: {e}")
        user_data["current_question"] += 1
        await asyncio.sleep(2)
        await self.send_next_question(update, context)