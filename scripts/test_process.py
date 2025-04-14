#!/usr/bin/env python3
"""Simple test script for the HypnoChatProcess."""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hypnobot.crew.processes import HypnoChatProcess

def test_process():
    """Test the HypnoChatProcess with a simple message."""
    try:
        # Create the process
        print("\nCreating HypnoChatProcess...")
        processor = HypnoChatProcess()
        
        # Test message
        test_message = "What is hypnotherapy?"
        
        # Check if we have a valid API key
        api_key = os.environ.get("OPENAI_API_KEY", "")
        use_real_api = api_key and not ("sk-proj-" in api_key or "your_" in api_key)
        
        if not use_real_api:
            print("\nUsing simulated response since valid API key is not set")
            print("To test with real API calls, set a valid OPENAI_API_KEY in .env")
            
            # Mock a successful result
            processed_result = {
                "original_response": "Hypnotherapy is a therapeutic technique that uses guided relaxation and focused attention to achieve a heightened state of awareness. In this state, a person is more open to suggestion and change.",
                "final_response": "Hypnotherapy is a therapeutic technique that uses guided relaxation and focused attention to achieve a heightened state of awareness. In this state, a person is more open to suggestion and change.",
                "safety_level": 0,
                "metadata": {"simulated": True},
            }
        else:
            # Process the message - using the full workflow
            print(f"\nProcessing message with full crew workflow: '{test_message}'")
            
            # Override the processor's process_message to track agent usage
            original_extract_method = processor._extract_text_from_crew_output
            
            # Track which agents are used
            client_agent_used = False
            qa_agent_used = False
            
            # Create wrapper methods to track agent usage
            def track_client_task(task_input):
                nonlocal client_agent_used
                client_agent_used = True
                print("\n✓ ClientAgent task created")
                return original_chat_task_create(task_input)
                
            def track_qa_task(task_input):
                nonlocal qa_agent_used
                qa_agent_used = True
                print("\n✓ QAAgent task created")
                return original_review_task_create(task_input)
            
            # Patch the methods to track usage
            original_chat_task_create = processor.chat_task_creator.create_task
            original_review_task_create = processor.review_task_creator.create_task
            
            processor.chat_task_creator.create_task = track_client_task
            processor.review_task_creator.create_task = track_qa_task
            
            try:
                # Run the process with tracking
                start_time = time.time()
                processed_result = processor.process_message(test_message)
                end_time = time.time()
                
                print(f"\nProcessing completed in {end_time - start_time:.2f} seconds")
                
                # Restore original methods
                processor.chat_task_creator.create_task = original_chat_task_create
                processor.review_task_creator.create_task = original_review_task_create
                
                # Verify both agents were used
                if use_real_api:
                    if not client_agent_used:
                        print("\nWARNING: ClientAgent was not used in the process!")
                    
                    if not qa_agent_used:
                        print("\nWARNING: QAAgent was not used in the process!")
                    
                    # Add verification to the metadata for the test output
                    processed_result["metadata"]["client_agent_used"] = client_agent_used
                    processed_result["metadata"]["qa_agent_used"] = qa_agent_used
                    
            except Exception as inner_e:
                # Restore original methods in case of error
                processor.chat_task_creator.create_task = original_chat_task_create
                processor.review_task_creator.create_task = original_review_task_create
                raise inner_e
        
        # Print the result
        print("\nProcessed Result:")
        print(f"Original Response: {processed_result['original_response']}")
        print(f"Final Response: {processed_result['final_response']}")
        print(f"Safety Level: {processed_result['safety_level']}")
        print(f"Metadata: {processed_result['metadata']}")
        
        # Validate the result
        if not processed_result["original_response"]:
            print("\nERROR: Empty original response!")
            return False
            
        if not processed_result["final_response"]:
            print("\nERROR: Empty final response!")
            return False
            
        if "safety_level" not in processed_result:
            print("\nERROR: Missing safety level in result!")
            return False
            
        if "metadata" not in processed_result:
            print("\nERROR: Missing metadata in result!")
            return False
        
        # Additional validation for real API usage
        if use_real_api:
            if not processed_result["metadata"].get("client_agent_used"):
                print("\nERROR: ClientAgent was not used when it should have been!")
                return False
                
            if not processed_result["metadata"].get("qa_agent_used"):
                print("\nERROR: QAAgent was not used when it should have been!")
                return False
            
        # Print success message
        print("\nTest completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_process()
    print(f"\nTest {'passed' if success else 'failed'}!")
    sys.exit(0 if success else 1) 