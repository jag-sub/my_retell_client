"""
Running this program creates a phone call using a Single Prompt Retell AI Agent. 
It then polls until the response is received, downloads relevant files,
and optionally scrubs sensitive data from the call record.
"""

import os
import time
import logging
import requests
from dotenv import load_dotenv
from retell import Retell
from datetime import datetime
from typing import Optional, Dict, Any


def setup_logging() -> None:
    """
    Set up logging configuration:
    - Creates application and call log directories if they don't exist.
    - Configures file logging with a daily file based on current date.
    - Adds console logging to output logs to stdout.
    """
    current_date = datetime.now().strftime("%Y%m%d")
    appl_log_dir = './logs/appl_logs'
    call_log_dir = './logs/call_logs'

    # Ensure directories exist
    os.makedirs(appl_log_dir, exist_ok=True)
    os.makedirs(call_log_dir, exist_ok=True)

    # Configure logging to file and console
    logging.basicConfig(
        filename=f'{appl_log_dir}/appl_log_{current_date}.log',
        filemode='a+',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    # Also log to console (stdout)
    logging.getLogger().addHandler(logging.StreamHandler())


def load_and_validate_env(var_name: str, cast_type: type = str) -> Any:
    """
    Load an environment variable and cast to the specified type.
    Raise an error if the variable is missing or cannot be cast.

    Args:
        var_name: Name of the environment variable
        cast_type: Type to cast the environment variable to (default: str)

    Returns:
        The environment variable value casted to `cast_type`.

    Raises:
        EnvironmentError: If the environment variable is missing.
        ValueError: If the environment variable cannot be cast to `cast_type`.
    """
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    try:
        return cast_type(value)
    except ValueError:
        raise ValueError(f"Environment variable {var_name} must be of type {cast_type.__name__}")


def download_file(url: str, output_file_path: str) -> None:
    """
    Download a file from a given URL and save it to the specified location.
    Includes logging and error handling.

    Args:
        url: URL to download the file from.
        output_file_path: Local file path where the file will be saved.
    """
    if not url or url == '-':
        logging.warning(f"Invalid or missing URL provided for downloading: '{url}'")
        return

    try:
        logging.info(f"Starting download from {url} to {output_file_path}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(output_file_path, 'wb') as f:
            f.write(response.content)
        logging.info(f"File saved as {output_file_path}")
    except requests.RequestException as e:
        logging.error(f"Failed to download file from {url}. Error: {e}")
    except IOError as e:
        logging.error(f"Failed to write file {output_file_path}. Error: {e}")


def create_phone_call(
    sync_client: Retell,
    from_phone_num: str,
    to_phone_num: str,
    variables: Dict[str, str]
) -> str:
    """
    Initiate a phone call via the Retell client.

    Args:
        sync_client: An instance of Retell client.
        from_phone_num: The phone number from which the call is made.
        to_phone_num: The phone number to call.
        variables: Dictionary of dynamic variables for the Retell LLM prompt.

    Returns:
        The call ID string if call is successfully initiated.

    Raises:
        Exception if unable to create the phone call.
    """
    try:
        response = sync_client.call.create_phone_call(
            from_number=from_phone_num,
            to_number=to_phone_num,
            retell_llm_dynamic_variables=variables
        )
        logging.info(f"Call initiated, call_id: {response.call_id}")
        return response.call_id
    except Exception as e:
        logging.error(f"Error creating phone call: {e}", exc_info=True)
        raise


def get_call_details(sync_client: Retell, call_id: str) -> Any:
    """
    Retrieve details of a previously created phone call.

    Args:
        sync_client: An instance of Retell client.
        call_id: The ID of the call to retrieve details for.

    Returns:
        The call details object returned by the Retell client.

    Raises:
        Exception if unable to retrieve call details.
    """
    try:
        return sync_client.call.retrieve(call_id=call_id)
    except Exception as e:
        logging.error(f"Error retrieving call details: {e}", exc_info=True)
        raise


def poll_call_status(
    sync_client: Retell,
    call_id: str,
    max_wait_sec: int,
    wait_interval: int
) -> Optional[Any]:
    """
    Polls the Retell API for the call status until it ends or timeout occurs.

    Args:
        sync_client: Retell client instance.
        call_id: Call identifier string.
        max_wait_sec: Maximum total time (in seconds) to wait before timing out.
        wait_interval: Time (in seconds) to wait between polling attempts.

    Returns:
        The final call response when the call ends, or None if timed out or error occurs.
    """
    waited = 0
    while waited < max_wait_sec:
        try:
            call_response = get_call_details(sync_client, call_id)
            status = getattr(call_response, 'call_status', None)
            logging.info(f"Current call status: {status}")
            if status == 'ended':
                return call_response
        except Exception:
            logging.error("Error getting call details during polling.", exc_info=True)
            break

        time.sleep(wait_interval)
        waited += wait_interval

    logging.warning("Call monitoring timed out. Exiting loop.")
    try:
        return call_response
    except NameError:
        return None


def scrub_call_data(sync_client: Retell, call_id: str) -> Any:
    """
    Update the call to scrub sensitive data by opting out of sensitive data storage.

    Args:
        sync_client: Retell client instance.
        call_id: Call identifier string.

    Returns:
        The updated call response object.

    Raises:
        Exception if the update fails.
    """
    try:
        updated_call_response = sync_client.call.update(
            call_id=call_id,
            metadata={},
            opt_out_sensitive_data_storage=True,
        )
        logging.info(f"Call scrubbed successfully, call_id: {call_id}")
        return updated_call_response
    except Exception as e:
        logging.error(f"Error scrubbing phone call details: {e}", exc_info=True)
        raise


def main() -> None:
    """
    Main entry point for the script:
    - Sets up logging
    - Loads environment variables
    - Initiates phone call
    - Polls call status until it ends or times out
    - Downloads recording and call log files
    - Logs summary information about the call
    - Optionally scrubs sensitive call data
    """
    setup_logging()

    logging.info("Loading environment variables")
    load_dotenv()

    try:
        scrub_sensitive_data = load_and_validate_env("SCRUB_SENSITIVE_CALL_DATA").strip().lower()
        api_key = load_and_validate_env("RETELL_API_KEY")
        from_phone_num = load_and_validate_env("FROM_PHONE_NUMBER")
        to_phone_num = load_and_validate_env("TO_PHONE_NUMBER")
        max_wait_time = load_and_validate_env("MAX_WAIT_TIME", int)
        wait_interval = load_and_validate_env("WAIT_INTERVAL", int)
        my_full_name = load_and_validate_env("MY_FULL_NAME")
        my_phone_number = load_and_validate_env("MY_PHONE_NUMBER")
        my_ssn = load_and_validate_env("MY_SSN")
    except Exception as e:
        logging.error(f"Environment setup failed: {e}", exc_info=True)
        return

    sync_client = Retell(api_key=api_key)
    current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
    call_log_dir = './logs/call_logs'

    variables = {
        "my_full_name": my_full_name,
        "my_phone_number": my_phone_number,
        "my_ssn": my_ssn
    }

    try:
        call_id = create_phone_call(sync_client, from_phone_num, to_phone_num, variables)
    except Exception:
        logging.error("Failed to initiate phone call. Exiting.")
        return

    call_response = poll_call_status(sync_client, call_id, max_wait_time, wait_interval)
    if not call_response:
        logging.error("No call response retrieved. Exiting.")
        return
    
    try:
        # Save the call_response JSON
        json_file_path = f"{call_log_dir}/{current_date_time}_{call_id}.json"
        call_response_json = call_response.to_json()
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json_file.write(call_response_json)
        logging.info(f"Call response saved as JSON at: {json_file_path}")
    except Exception as e:
        logging.error(f"Failed to save call response JSON: {e}", exc_info=True)

    try:
        # Safely extract call details or use placeholder if missing
        duration = getattr(call_response.call_cost, 'total_duration_seconds', '-')
        cost = getattr(call_response.call_cost, 'combined_cost', '-')
        summary = getattr(call_response.call_analysis, 'call_summary', '-')
        recording_url = getattr(call_response, 'recording_url', '-')
        log_url = getattr(call_response, 'public_log_url', '-')

        recording_file_path = f"{call_log_dir}/{current_date_time}_{call_id}.wav"
        download_file(recording_url, recording_file_path)

        call_log_file = f"{call_log_dir}/{current_date_time}_{call_id}.log"
        download_file(log_url, call_log_file)

    except Exception as e:
        logging.error(f"Error extracting or downloading call details: {e}", exc_info=True)
        duration = cost = summary = recording_url = log_url = 'Unavailable'
        recording_file_path = "Unavailable"

    # Log call summary details
    logging.info(f"Recording file saved at: {recording_file_path}")
    logging.info(f"Call duration (seconds): {duration}")
    logging.info(f"Call cost: {cost}")
    logging.info(f"Call Summary: {summary}")

    # Optionally scrub sensitive call data
    if scrub_sensitive_data in ('yes', 'true', '1'):
        logging.info("Scrubbing sensitive call data as requested.")
        try:
            updated_call = scrub_call_data(sync_client=sync_client, call_id=call_id)
            logging.info("Sensitive call data scrubbed successfully.")
        except Exception:
            logging.error("Failed to scrub sensitive call data.", exc_info=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.critical("Unhandled exception occurred.", exc_info=True)
