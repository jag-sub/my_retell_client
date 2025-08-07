# Retell AI Client Implementation
My Retell AI client implementation to call the CA EDD PFL phone number, navigate the IVR system and transfer the call to me if successful

## Summary
This Python script automates the process of creating a phone call using a Single Prompt Retell AI Agent. It:

- Initiates a phone call via the Retell API
- Polls the call status until it ends or a timeout occurs
- Downloads the call recording WAV file and phone call log files locally
- Saves the full call response data as JSON
- Optionally scrubs sensitive data from the call record via the Retell Update Call API, to delete call transcripts and sensitive data from Retell's platform.
- Logs all relevant events and errors to both, files and console

## Features

- Secure environment variable loading with type validation
- Robust polling mechanism with timeout and logging
- Download of recording and call log files with error handling
- Optional sensitive data scrubbing controlled by environment variable
- Call response saved as JSON for audit or debugging purposes
- Detailed logging to app logs and call logs directories

## Prerequisites

- Python 3.13.5+
- Retell Python SDK installed (`retell`)
- `requests` library for HTTP downloads
- `python-dotenv` to load `.env` configurations

## Installation

`pip install -r requirements.txt`


## Setup

1. **Clone or download the repository**, then navigate to the project directory.

2. **Create a `.env` file** in the project root with the following variables:

    ```
    RETELL_API_KEY="your_retell_api_key_here"
    FROM_PHONE_NUMBER="+1234567890"
    TO_PHONE_NUMBER="+987654321"
    MAX_WAIT_TIME=180                 # Maximum wait time in seconds (e.g., 180 for 3 minutes)
    WAIT_INTERVAL=5                  # Polling interval in seconds
    MY_FULL_NAME="John Doe"
    MY_PHONE_NUMBER="+1234567890"
    MY_SSN="123456789"
    SCRUB_SENSITIVE_CALL_DATA="yes"  # Set to 'yes', 'true', or '1' to enable scrubbing; otherwise no scrubbing
    ```

3. **Ensure Python virtual environment is activated (recommended):**

    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt  # Or install packages manually as above
    ```
4. **Create a Single Prompt Agent in Retell AI:** Signup/Login to Retell AI. Under Build > Agents, Import the `CA EDD PFL Agent.json` file to create the Single Prompt agent.

## Usage

Run the script with:

`python your_script_filename.py`


The script will:

- Create a phone call from `FROM_PHONE_NUMBER` to `TO_PHONE_NUMBER`.
- Periodically poll the call status every `WAIT_INTERVAL` seconds up to `MAX_WAIT_TIME`.
- Upon call completion, download recording file, call logs, and save the full call response JSON to `./logs/call_logs`.
- If `SCRUB_SENSITIVE_CALL_DATA` is enabled, scrub sensitive data such as the SSN via the Retell's update call API.
- Log all application and phone call events in `./logs/appl_logs` and `./logs/call_logs`.

## File Outputs

- Application logs: `./logs/appl_logs/appl_log_YYYYMMDD.log`
- Call recording WAV file: `./logs/call_logs/YYYYMMDDHHMMSS_<call_id>.wav`
- Call log file: `./logs/call_logs/YYYYMMDDHHMMSS_<call_id>.log`
- Call response JSON: `./logs/call_logs/YYYYMMDDHHMMSS_<call_id>.json`

## Environment Variables Description

| Variable                   | Description                                                  | Required | Type    |
|----------------------------|--------------------------------------------------------------|----------|---------|
| RETELL_API_KEY             | Your Retell API key for authentication                      | Yes      | String  |
| FROM_PHONE_NUMBER          | The phone number to initiate the call from, e.g. a Twilio number bought on the Retell platform                   | Yes      | String  |
| TO_PHONE_NUMBER            | The destination phone number to transfer the call to                         | Yes      | String  |
| MAX_WAIT_TIME              | Max seconds to wait before timing out waiting for call end  | Yes      | Integer |
| WAIT_INTERVAL              | Interval in seconds between call status polling attempts    | Yes      | Integer |
| MY_FULL_NAME               | Your full name. Only used as a dynamic variable for Retell prompt context                   | Yes      | String  |
| MY_PHONE_NUMBER            | Your phone number. Only used as a dynamic variable for Retell prompt context                   | Yes      | String  |
| MY_SSN                     | Your SSN. EDD's IVR system prompts for it to lookup your details                  | Yes      | String  |
| SCRUB_SENSITIVE_CALL_DATA  | Set to "yes", "true", or "1" to enable call data scrubbing to delete SSNs and call transcripts from Retell's platform | No       | String  |

## Troubleshooting

- **ModuleNotFoundError: No module named 'requests'**

  Install required dependencies with:

`pip install requests python-dotenv retell`


- **VS Code not using the correct Python environment**

Use the command palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and select `Python: Select Interpreter` to choose your virtual environment.

- **API authentication or call creation issues**

Double-check your `RETELL_API_KEY` and phone numbers are correct and formatted as expected.

## Logging

- Logs are recorded both to daily log files inside `./logs/appl_logs` and streamed to console.
- Errors and stack traces are logged with context for easier debugging.

## License

This script is provided as-is. Adjust and extend it according to your own project needs.

## Credits and Acknowledgments
This script leverages APIs and tools from Retell AI.

 [Retell AI](https://www.retellai.com/) ([GitHub](https://github.com/RetellAI))

 The author acknowledges the assistance of [Perplexity AI](https://www.perplexity.ai/) in providing research, code debugging, and documentation recommendations throughout this project.
 
