"""
Running this program creates a phone call using a Single Prompt Retell AI Agent. 
It then polls until the reponse is received and prints that to console.
"""
import os
import time
import logging
from dotenv import load_dotenv
from retell import Retell

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Load environment variables from .env file
load_dotenv()

def load_and_validate_env(var_name):
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

api_key = load_and_validate_env("RETELL_API_KEY")
# agent_id = load_and_validate_env("SINGLE_PROMPT_AGENT_ID")
from_phone_num = load_and_validate_env("FROM_PHONE_NUMBER")
to_phone_num = load_and_validate_env("TO_PHONE_NUMBER")

sync_client = Retell(api_key=api_key)

def create_phone_call():
    try:
        response = sync_client.call.create_phone_call(
            from_number=from_phone_num,
            to_number=to_phone_num
        )
        logging.info(f"Call initiated, call_id: {response.call_id}")
        return response.call_id
    except Exception as e:
        logging.error(f"Error creating phone call: {e}")
        raise

def get_call_details(call_id):
    try:
        return sync_client.call.retrieve(call_id=call_id)
    except Exception as e:
        logging.error(f"Error retrieving call details: {e}")
        raise

def main():
    call_id = create_phone_call()
    max_wait_sec = 180   # e.g., 10 minute timeout
    wait_interval = 6
    waited = 0

    while waited < max_wait_sec:
        call_response = get_call_details(call_id)
        status = getattr(call_response, 'call_status', None)
        logging.info(f"Current call status: {status}")
        if status == 'ended':
            break
        time.sleep(wait_interval)
        waited += wait_interval
    else:
        logging.warning("Call monitoring timed out. Exiting loop.")

    # Extract and log call summary safely
    try:
        duration = getattr(call_response.call_cost, 'total_duration_seconds', '-')
        cost = getattr(call_response.call_cost, 'combined_cost', '-')
        summary = getattr(call_response.call_analysis, 'call_summary', '-')
        recording = getattr(call_response, 'recording_url', '-')
    except Exception as e:
        logging.error(f"Error extracting call details: {e}")
        duration = cost = summary = recording = 'Unavailable'

    logging.info(f"Recording URL: {recording}")
    logging.info(f"Call duration: {duration}")
    logging.info(f"Call cost: {cost}")
    logging.info(f"Call Summary: {summary}")

if __name__ == "__main__":
    main()
