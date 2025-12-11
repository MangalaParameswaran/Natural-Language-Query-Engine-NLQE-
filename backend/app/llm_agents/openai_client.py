# openai_client.py
import os
import asyncio
import logging
from openai import OpenAI
from openai import RateLimitError, APIError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def create_chat_completion_with_retry(
    model: str,
    messages: list,
    temperature: float = 0,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
):
    """
    Create a chat completion with automatic retry on rate limit errors.
    
    Args:
        model: The model to use
        messages: List of message dicts
        temperature: Temperature setting
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before retry
        max_delay: Maximum delay in seconds between retries
        backoff_factor: Factor to multiply delay by on each retry
    
    Returns:
        ChatCompletion response object
    
    Raises:
        RateLimitError: If rate limit is exceeded after all retries
        APIError: For other API errors
    """
    delay = initial_delay
    agent_name = "Unknown"
    
    # Try to identify which agent is calling (for debugging)
    import inspect
    try:
        caller = inspect.stack()[1]
        agent_name = caller.filename.split('/')[-1] or caller.filename.split('\\')[-1]
    except:
        pass
    
    logger.info(f"[{agent_name}] Starting API call to model: {model}, temperature: {temperature}")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[{agent_name}] Attempt {attempt + 1}/{max_retries} - Calling OpenAI API...")
            
            # Make the API call in a thread pool to avoid blocking the event loop
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            logger.info(f"[{agent_name}] ✅ Success! Got response from OpenAI")
            return response
            
        except RateLimitError as e:
            # Check if error message contains retry-after information
            error_message = str(e)
            retry_after = None
            rate_limit_type = "unknown"
            wait_time_hours = None
            
            logger.warning(f"[{agent_name}] ⚠️ RateLimitError on attempt {attempt + 1}: {error_message}")
            
            # Check error response for detailed rate limit info
            if hasattr(e, 'response') and e.response:
                headers = getattr(e.response, 'headers', {})
                logger.info(f"[{agent_name}] Error response status: {getattr(e.response, 'status_code', 'N/A')}")
                
                # Extract retry-after from headers (most reliable)
                # Headers can be accessed case-insensitively or as dict
                retry_after_header = None
                if isinstance(headers, dict):
                    retry_after_header = headers.get('retry-after') or headers.get('Retry-After')
                else:
                    # Headers might be a case-insensitive dict-like object
                    retry_after_header = headers.get('retry-after', headers.get('Retry-After'))
                
                if retry_after_header:
                    try:
                        retry_after = int(retry_after_header)
                        wait_time_hours = retry_after / 3600
                        logger.info(f"[{agent_name}] ✅ Found retry-after in headers: {retry_after} seconds ({wait_time_hours:.2f} hours)")
                        
                        # Fail fast if wait time is more than 1 hour (TPM exhaustion)
                        if retry_after > 3600:
                            logger.error(f"[{agent_name}] ❌ TPM exhaustion detected! Wait time: {wait_time_hours:.2f} hours")
                            logger.error(f"[{agent_name}] 💡 Recommendation: Wait {wait_time_hours:.1f} hours or upgrade your OpenAI plan")
                            # Re-raise the original exception with a clear message
                            error_msg = (
                                f"Rate limit exceeded (TPM - Tokens Per Minute exhausted). "
                                f"Please wait {wait_time_hours:.1f} hours or upgrade your OpenAI plan. "
                                f"Visit https://platform.openai.com/account/billing to increase limits."
                            )
                            # Create a new exception with the message
                            raise Exception(error_msg) from e
                    except (ValueError, TypeError) as ve:
                        logger.warning(f"[{agent_name}] ⚠️ Could not parse retry-after header '{retry_after_header}': {ve}")
                
                # Check rate limit type and remaining tokens
                if 'x-ratelimit-remaining-tokens' in headers:
                    remaining_tokens = headers.get('x-ratelimit-remaining-tokens', '0')
                    limit_tokens = headers.get('x-ratelimit-limit-tokens', '0')
                    try:
                        remaining_int = int(remaining_tokens)
                        limit_int = int(limit_tokens)
                        usage_percent = ((limit_int - remaining_int) / limit_int * 100) if limit_int > 0 else 0
                        logger.info(f"[{agent_name}] Token limits: {remaining_tokens}/{limit_tokens} remaining ({usage_percent:.1f}% used)")
                        if remaining_int == 0:
                            rate_limit_type = "TPM (Tokens Per Minute)"
                            logger.error(f"[{agent_name}] ❌ TPM limit exhausted!")
                        elif remaining_int < limit_int * 0.1:  # Less than 10% remaining
                            logger.warning(f"[{agent_name}] ⚠️ TPM limit nearly exhausted! Only {remaining_int} tokens remaining.")
                    except (ValueError, TypeError):
                        logger.warning(f"[{agent_name}] Could not parse token limits")
                
                if 'x-ratelimit-remaining-requests' in headers:
                    remaining_requests = headers.get('x-ratelimit-remaining-requests', '0')
                    limit_requests = headers.get('x-ratelimit-limit-requests', '0')
                    logger.info(f"[{agent_name}] Request limits: {remaining_requests}/{limit_requests} remaining")
                    if int(remaining_requests) < 2:
                        if rate_limit_type == "unknown":
                            rate_limit_type = "RPM (Requests Per Minute)"
                        logger.warning(f"[{agent_name}] ⚠️ RPM limit nearly exhausted!")
            
            # Try to extract retry-after time from error message (fallback)
            if retry_after is None and "try again in" in error_message.lower():
                import re
                # Try seconds format: "try again in 20s"
                match = re.search(r"try again in (\d+)s", error_message.lower())
                if match:
                    retry_after = int(match.group(1))
                    logger.info(f"[{agent_name}] Extracted retry-after from message: {retry_after} seconds")
                else:
                    # Try hours format: "try again in 34h29m42.72s"
                    match = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?", error_message.lower())
                    if match:
                        hours = int(match.group(1) or 0)
                        minutes = int(match.group(2) or 0)
                        seconds = float(match.group(3) or 0)
                        retry_after = int(hours * 3600 + minutes * 60 + seconds)
                        wait_time_hours = hours + minutes/60 + seconds/3600
                        logger.warning(f"[{agent_name}] ⚠️ Long wait time detected: {wait_time_hours:.2f} hours ({retry_after} seconds)")
            
            # Determine wait time
            if retry_after:
                wait_time = retry_after
                # If wait time is more than 1 hour, it's probably TPM exhaustion - don't retry
                if wait_time > 3600:
                    logger.error(f"[{agent_name}] ❌ Rate limit wait time too long ({wait_time/3600:.2f} hours). This is likely TPM exhaustion.")
                    logger.error(f"[{agent_name}] 💡 Recommendation: Wait {wait_time_hours:.1f} hours or upgrade your OpenAI plan")
                    error_msg = (
                        f"Rate limit exceeded ({rate_limit_type}). "
                        f"Please wait {wait_time_hours:.1f} hours or upgrade your OpenAI plan. "
                        f"Visit https://platform.openai.com/account/billing to increase limits."
                    )
                    raise Exception(error_msg) from e
            else:
                wait_time = delay
            
            if attempt < max_retries - 1:
                wait_minutes = wait_time / 60
                logger.warning(f"[{agent_name}] ⏳ Rate limit exceeded ({rate_limit_type}). Waiting {wait_time} seconds ({wait_minutes:.1f} minutes) before retry {attempt + 2}/{max_retries}")
                print(f"⚠️ [{agent_name}] Rate limit exceeded ({rate_limit_type}). Retrying in {wait_time} seconds ({wait_minutes:.1f} min)... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
                # Increase delay for next attempt (exponential backoff)
                delay = min(delay * backoff_factor, max_delay)
                logger.info(f"[{agent_name}] Retry delay updated to: {delay} seconds")
            else:
                logger.error(f"[{agent_name}] ❌ Rate limit exceeded after {max_retries} attempts. Giving up.")
                error_msg = f"Rate limit exceeded ({rate_limit_type}) after {max_retries} attempts."
                if wait_time_hours:
                    error_msg += f" Please wait {wait_time_hours:.1f} hours or upgrade your OpenAI plan."
                print(f"❌ [{agent_name}] {error_msg}")
                # Re-raise the original exception with additional context
                raise Exception(error_msg) from e
                
        except APIError as e:
            error_message = str(e)
            logger.error(f"[{agent_name}] ❌ APIError on attempt {attempt + 1}: {error_message}")
            
            # For other API errors, retry with exponential backoff
            if attempt < max_retries - 1:
                logger.warning(f"[{agent_name}] ⏳ API error occurred. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                print(f"⚠️ [{agent_name}] API error occurred. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(f"[{agent_name}] ❌ API error after {max_retries} attempts.")
                raise e
                
        except Exception as e:
            # For unexpected errors, don't retry
            logger.error(f"[{agent_name}] ❌ Unexpected error: {type(e).__name__}: {str(e)}")
            print(f"❌ [{agent_name}] Unexpected error: {type(e).__name__}: {str(e)}")
            raise e
    
    # This should never be reached, but just in case
    logger.error(f"[{agent_name}] ❌ Failed to get response after all retries")
    raise Exception("Failed to get response after all retries")

