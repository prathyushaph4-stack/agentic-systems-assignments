from build_chain import build_chain  # Import the reusable chain-building function from build_chain.py.
from typing import Any, Tuple, List


def is_response_valid(response: Any) -> Tuple[bool, List[str]]:  # Define a function that returns validity and error messages.
    errors: List[str] = []  # Create an empty list to store validation errors.

    if not isinstance(response, str):  # If it's not a string, record but continue after coercion.
        errors.append("Response is not a string.")

    # Coerce to string for the rest of the checks so we can validate content.
    response_text = str(response) if response is not None else ""

    if not response_text.strip():  # Remove extra spaces and check whether anything meaningful is left.
        errors.append("Response is empty.")  # Add an error message when the response has no real content.

    word_count = len(response_text.split())  # Split the response by spaces and count the number of words.

    if word_count > 100:  # Check whether the response is longer than the allowed limit.
        errors.append("Response is too long: more than 100 words.")  # Add an error message when output is too long.

    return len(errors) == 0, errors  # Return True if there are no errors, otherwise return False with errors.


def extract_text_from_chain_output(output: Any) -> str:
    """Try to extract a human-readable string from common chain output shapes."""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        # common keys that may contain text
        for key in ("text", "output", "response", "result"):
            if key in output and isinstance(output[key], str):
                return output[key]
        # otherwise return first string value if present
        for v in output.values():
            if isinstance(v, str):
                return v
        return str(output)
    # fallback to string conversion
    return str(output)


def main() -> None:
    chain = build_chain()  # Build the LCEL chain once so it can be tested.

    test_case = {  # Create one test input for the chain.
        "topic": "LangChain Expression Language",
        "analogy_domain": "school assembly line",
    }

    try:
        response = chain.invoke(test_case)  # Run the chain with the test input and collect the response.
    except Exception as e:
        print("Chain invocation raised an exception:", e)
        return

    # Extract readable text from the chain output
    response_text = extract_text_from_chain_output(response)

    print("Generated Response:")
    print(response_text)

    is_valid, errors = is_response_valid(response_text)  # Validate the response using the success criteria.

    if is_valid:  # Check whether the validation result is successful.
        print("Valid response.")  # Print success message when all checks pass.
    else:  # Run this block when validation fails.
        print("Invalid response.")  # Print failure message.
        print(errors)  # Print the list of validation errors.


if __name__ == "__main__":
    main()
