#!/usr/bin/env python3
"""Conversation manager example - maintains chat history and context."""

import json
import os
from datetime import datetime
from typing import List, Optional

from openrouter_py import OpenRouterClient
from openrouter_py.models.chat import ChatMessage


class ConversationManager:
    """Manages multi-turn conversations with context persistence."""
    
    def __init__(self, client: OpenRouterClient, model: str = "google/gemma-3n-e2b-it:free"):
        self.client = client
        self.model = model
        self.messages: List[ChatMessage] = []
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.max_tokens = 150
        self.temperature = 0.7
    
    def set_system_message(self, content: str):
        """Set the system message that defines AI behavior."""
        # Remove existing system message if present
        self.messages = [msg for msg in self.messages if msg.role != "system"]
        
        # Add new system message at the beginning
        system_msg = ChatMessage(role="system", content=content)
        self.messages.insert(0, system_msg)
        print(f"🎭 System message set: {content}")
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        user_msg = ChatMessage(role="user", content=content)
        self.messages.append(user_msg)
        print(f"👤 User: {content}")
    
    def get_ai_response(self) -> str:
        """Get AI response and add it to conversation history."""
        completion = self.client.chat_completion(
            messages=self.messages,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        if completion.message:
            self.messages.append(completion.message)
            response = completion.content or ""
            print(f"🤖 Assistant: {response}")
            return response
        
        return ""
    
    def chat(self, user_input: str) -> str:
        """Complete chat interaction: add user message and get AI response."""
        self.add_user_message(user_input)
        return self.get_ai_response()
    
    def get_conversation_summary(self) -> dict:
        """Get a summary of the current conversation."""
        return {
            "conversation_id": self.conversation_id,
            "message_count": len(self.messages),
            "model": self.model,
            "has_system_message": any(msg.role == "system" for msg in self.messages),
            "user_messages": len([msg for msg in self.messages if msg.role == "user"]),
            "assistant_messages": len([msg for msg in self.messages if msg.role == "assistant"])
        }
    
    def save_conversation(self, filename: Optional[str] = None):
        """Save conversation to JSON file."""
        if not filename:
            filename = f"conversation_{self.conversation_id}.json"
        
        conversation_data = {
            "metadata": self.get_conversation_summary(),
            "messages": [msg.model_dump() for msg in self.messages]
        }
        
        with open(filename, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        print(f"💾 Conversation saved to {filename}")
    
    def load_conversation(self, filename: str):
        """Load conversation from JSON file."""
        with open(filename, 'r') as f:
            conversation_data = json.load(f)
        
        self.messages = [ChatMessage(**msg) for msg in conversation_data["messages"]]
        self.conversation_id = conversation_data["metadata"]["conversation_id"]
        
        print(f"📁 Conversation loaded from {filename}")
        print(f"📊 {len(self.messages)} messages loaded")
    
    def clear_conversation(self, keep_system: bool = True):
        """Clear conversation history."""
        if keep_system:
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            self.messages = system_messages
        else:
            self.messages = []
        
        print("🧹 Conversation cleared")
    
    def print_conversation(self):
        """Print the full conversation."""
        print(f"\n📋 Conversation {self.conversation_id}")
        print("=" * 50)
        
        for i, msg in enumerate(self.messages, 1):
            role_emoji = {"system": "⚙️", "user": "👤", "assistant": "🤖"}.get(msg.role, "❓")
            print(f"{i:2d}. {role_emoji} {msg.role.title()}: {msg.content}")
        
        print("=" * 50)


def demo_basic_conversation():
    """Demo basic conversation management."""
    print("🦈 Basic Conversation Demo")
    
    with OpenRouterClient() as client:
        conv = ConversationManager(client)
        
        # Set a system message
        conv.set_system_message("You are a helpful programming tutor who explains concepts clearly.")
        
        # Have a conversation
        conv.chat("What is a variable in programming?")
        conv.chat("Can you give me an example in Python?")
        conv.chat("What's the difference between a variable and a constant?")
        
        # Show conversation summary
        summary = conv.get_conversation_summary()
        print(f"\n📊 Conversation Summary: {summary}")


def demo_character_conversation():
    """Demo conversation with character personality."""
    print("\n🎭 Character Conversation Demo")
    
    with OpenRouterClient() as client:
        conv = ConversationManager(client, model="mistralai/mistral-small-3.2-24b-instruct:free")
        
        # Set character personality
        conv.set_system_message(
            "You are a wise old wizard who speaks in riddles and metaphors. "
            "You have vast knowledge but prefer to guide rather than give direct answers."
        )
        
        # Have a magical conversation
        conv.chat("How do I learn programming?")
        conv.chat("What programming language should I start with?")
        
        # Print full conversation
        conv.print_conversation()


def demo_conversation_persistence():
    """Demo saving and loading conversations."""
    print("\n💾 Conversation Persistence Demo")
    
    with OpenRouterClient() as client:
        # Create first conversation
        conv1 = ConversationManager(client)
        conv1.set_system_message("You are a helpful math tutor.")
        conv1.chat("What is calculus?")
        conv1.chat("When was it invented?")
        
        # Save conversation
        filename = "math_tutorial.json"
        conv1.save_conversation(filename)
        
        # Create new conversation manager and load saved conversation
        conv2 = ConversationManager(client)
        conv2.load_conversation(filename)
        
        # Continue the conversation
        conv2.chat("Who were the main inventors?")
        
        # Clean up
        os.remove(filename)
        print(f"🗑️  Cleaned up {filename}")


def demo_interactive_conversation():
    """Interactive conversation demo."""
    print("\n🎮 Interactive Conversation Demo")
    
    with OpenRouterClient() as client:
        conv = ConversationManager(client)
        
        print("🎭 Choose a personality for the AI:")
        print("1. Helpful programmer")
        print("2. Creative writer")
        print("3. Science teacher")
        print("4. Custom personality")
        
        choice = input("Choose (1-4): ").strip()
        
        personalities = {
            "1": "You are a helpful programmer who loves clean code and best practices.",
            "2": "You are a creative writer who sees stories and metaphors everywhere.",
            "3": "You are an enthusiastic science teacher who makes complex topics simple.",
            "4": input("Enter custom personality: ")
        }
        
        conv.set_system_message(personalities.get(choice, personalities["1"]))
        
        print("\n💬 Start chatting! (type 'quit' to exit, 'clear' to reset, 'summary' for info)")
        
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                conv.clear_conversation()
                continue
            elif user_input.lower() == 'summary':
                print(f"📊 {conv.get_conversation_summary()}")
                continue
            elif user_input.lower() == 'save':
                conv.save_conversation()
                continue
            elif not user_input:
                continue
            
            try:
                conv.chat(user_input)
            except KeyboardInterrupt:
                print("\n⚠️  Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Run conversation manager examples."""
    print("🦈 OpenRouter Conversation Manager Examples")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    demo_basic_conversation()
    demo_character_conversation()
    demo_conversation_persistence()
    
    # Interactive demo (optional)
    response = input("\n🎮 Run interactive conversation demo? (y/N): ")
    if response.lower() in ['y', 'yes']:
        demo_interactive_conversation()
    
    print("\n✅ Conversation manager examples completed!")


if __name__ == "__main__":
    main()