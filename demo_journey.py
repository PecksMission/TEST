#!/usr/bin/env python3
"""
Surgery Day Builder Demo Script
Test the Journey Generator without needing Flask

Usage:
    python3 demo_journey.py

You'll have an interactive conversation with Claude to build a journey.
"""

import os
import sys
import json
from datetime import datetime

# Import the journey generator
sys.path.insert(0, os.path.dirname(__file__))

try:
    from services_journey_generator import JourneyGenerator
except ImportError:
    print("Error: Could not import JourneyGenerator")
    print("Make sure services_journey_generator.py is in the same directory")
    sys.exit(1)


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_assistant_message(text):
    """Print assistant message nicely"""
    print(f"\n🤖 Assistant:\n{text}\n")


def print_user_prompt():
    """Print user input prompt"""
    print("👤 You:", end=" ")


def print_structure(structure):
    """Print the generated journey structure nicely"""
    print_header("✅ Journey Structure Generated!")
    
    print(f"Title: {structure.get('title')}")
    print(f"Condition: {structure.get('condition')}")
    print(f"Procedure: {structure.get('procedure_type', 'N/A')}")
    print(f"Dates: {structure.get('start_date')} to {structure.get('end_date', 'ongoing')}")
    
    print(f"\nStages ({len(structure.get('stages', []))}):")
    for i, stage in enumerate(structure.get('stages', []), 1):
        print(f"  {i}. {stage['name']} (color: {stage.get('color', 'N/A')})")
        print(f"     {stage.get('description', '')}")
    
    print(f"\nTimeline Entries ({len(structure.get('timeline_entries', []))}):")
    for i, entry in enumerate(structure.get('timeline_entries', []), 1):
        print(f"  {i}. [{entry['date']}] {entry['type'].upper()}: {entry['title']}")
        print(f"     {entry['content'][:60]}...")
    
    if structure.get('milestones'):
        print(f"\nMilestones:")
        for milestone in structure['milestones']:
            print(f"  • {milestone}")


def main():
    """Main demo loop"""
    print_header("Surgery Day Builder - Demo")
    
    print("Welcome! This is a demo of the Surgery Day Builder AI chat interface.")
    print("You'll describe your health journey, and Claude will help organize it.")
    print("\nCommands:")
    print("  'quit' - Exit the demo")
    print("  'export' - Export journey structure as JSON")
    print("  'reset' - Start over with a new journey")
    print()
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        print()
        try:
            api_key = input("Enter your Anthropic API key (or press Enter to skip): ").strip()
            if not api_key:
                print("Cannot continue without API key")
                return
        except KeyboardInterrupt:
            return
    
    # Initialize generator
    try:
        generator = JourneyGenerator(api_key=api_key)
    except Exception as e:
        print(f"Error initializing generator: {e}")
        return
    
    print_header("Let's Create Your Health Journey")
    
    # Initial prompt from Claude
    initial_message = """Hello! I'm here to help you create a meaningful timeline for your health journey.

Tell me about your experience. What condition or procedure are you documenting? What dates did it span? Any key milestones or moments you want to remember?

(For example: "I had Chiari malformation surgery on February 26, 2026. I spent 6 weeks recovering. Both the surgery and my faith were really important to me.")"""
    
    print_assistant_message(initial_message)
    
    # Conversation loop
    conversation_count = 0
    max_turns = 15
    
    while conversation_count < max_turns:
        try:
            print_user_prompt()
            user_input = input().strip()
        except KeyboardInterrupt:
            print("\n\nDemo ended by user.")
            return
        except EOFError:
            print("\n\nEnd of input.")
            return
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("Thanks for trying Surgery Day Builder!")
            return
        
        if user_input.lower() == 'reset':
            generator.reset_conversation()
            print_header("Conversation reset. Starting over...")
            print_assistant_message(initial_message)
            conversation_count = 0
            continue
        
        if user_input.lower() == 'export' and generator.journey_data:
            # Try to get structure
            if generator.conversation_history:
                last_response = generator.conversation_history[-1]['content']
                structure = generator._extract_journey_json(last_response)
                if structure:
                    filename = f"journey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(structure, f, indent=2)
                    print(f"\n✅ Journey exported to {filename}")
                else:
                    print("\n⚠️  No journey structure to export yet")
            continue
        
        # Process with Claude
        try:
            result = generator.process_user_input(user_input)
            
            print_assistant_message(result['response'])
            
            conversation_count += 1
            
            # If journey structure is complete
            if result['journey_structure']:
                print_structure(result['journey_structure'])
                
                # Ask if user wants to continue
                print("\n" + "="*70)
                print("✅ Your journey structure is complete!")
                print("\nWhat would you like to do?")
                print("  1. Export journey to JSON")
                print("  2. Continue editing (ask for changes)")
                print("  3. Start over with a new journey")
                print("  4. Exit")
                
                try:
                    choice = input("\nEnter choice (1-4): ").strip()
                except (KeyboardInterrupt, EOFError):
                    return
                
                if choice == '1':
                    filename = f"journey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(result['journey_structure'], f, indent=2)
                    print(f"✅ Exported to {filename}")
                    
                    # Show file location
                    abs_path = os.path.abspath(filename)
                    print(f"Full path: {abs_path}")
                    
                    return
                elif choice == '2':
                    print("\nYou can continue asking for changes. For example:")
                    print('  "Add more faith moments"')
                    print('  "Make the surgery day entry more emotional"')
                    print('  "Split the recovery into more detailed stages"')
                    print_user_prompt()
                elif choice == '3':
                    generator.reset_conversation()
                    print_header("Starting a new journey...")
                    print_assistant_message(initial_message)
                    conversation_count = 0
                elif choice == '4':
                    return
            
            # Show progress
            turns = result['turn']
            stage = result['conversation_stage']
            print(f"\n[Turn {turns} | Stage: {stage} | Needs more info: {result['needs_more_info']}]")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")
            continue
    
    print_header("Demo Complete")
    print("Thanks for trying Surgery Day Builder!")


if __name__ == '__main__':
    main()
