import asyncio
import json
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_client():
    # Import after path is set
    from mcp.client import ClientSession
    import tempfile
    import time
    import os
    
    print("Testing screen capture MCP server...")
    
    # Connect to the MCP server
    async with ClientSession(transport="stdio") as session:
        # Test 1: Get initial recording status
        status = await session.call("get_recording_status")
        print(f"Initial recording status: {status}")
        assert not status["is_recording"], "Should not be recording initially"
        
        # Test 2: Take a screenshot
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            screenshot_path = tmpfile.name
        
        result = await session.call("take_screenshot", output_path=screenshot_path)
        print(f"Screenshot saved to: {result}")
        assert os.path.exists(result), "Screenshot file not created"
        assert os.path.getsize(result) > 0, "Screenshot file is empty"
        
        # Test 3: Start recording
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmpfile:
            recording_path = tmpfile.name
        
        await session.call("start_recording", output_path=recording_path)
        
        # Check recording status
        status = await session.call("get_recording_status")
        print(f"Recording status after start: {status}")
        assert status["is_recording"], "Should be recording after start"
        
        # Record for 3 seconds
        print("Recording for 3 seconds...")
        await asyncio.sleep(3)
        
        # Test 4: Stop recording
        result = await session.call("stop_recording")
        print(f"Recording stopped. Video saved to: {result}")
        assert result == recording_path, "Returned path does not match expected"
        assert os.path.exists(result), "Recording file not created"
        assert os.path.getsize(result) > 0, "Recording file is empty"
        
        # Check recording status after stopping
        status = await session.call("get_recording_status")
        print(f"Recording status after stop: {status}")
        assert not status["is_recording"], "Should not be recording after stop"
        
        print("All tests passed successfully!")
        
        # Cleanup temporary files
        os.unlink(screenshot_path)
        os.unlink(recording_path)

if __name__ == "__main__":
    asyncio.run(test_client())