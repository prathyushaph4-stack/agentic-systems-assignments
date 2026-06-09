from langchain_ollama import ChatOllama  # Import the LangChain wrapper used to talk to Ollama chat models.
from langchain_core.prompts import ChatPromptTemplate  # Import the chat prompt template builder from LangChain Core.
from langchain_core.output_parsers import StrOutputParser  # Import the parser that converts model output into plain text.


def build_chain():  # Define a reusable function that will create and return the LCEL chain.
    prompt = ChatPromptTemplate.from_messages(  # Create a chat-style prompt using system and human messages.
        [  # Start the list of chat messages.
            (  # Start the first message tuple.
                "system",  # Mark this message as the system instruction for the model.
                "You are a beginner-friendly programming instructor. "  # Tell the model its teaching role.
                "Explain concepts clearly in simple language. "  # Ask the model to explain in simple language.
                "Use short bullet points and avoid unnecessary introduction.",  # Ask for concise output.
            ),  # End the first message tuple.
            (  # Start the second message tuple.
                "human",  # Mark this message as the user request.
                "Explain {topic} using a simple analogy from {analogy_domain}.",  # Use placeholders for dynamic inputs.
            ),  # End the second message tuple.
        ]  # End the list of chat messages.
    )  # Finish creating the chat prompt template.

    llm = ChatOllama(  # Create the Ollama chat model object.
        model="qwen:1.8b",  # Choose the Ollama model name available on your machine.
        base_url="http://localhost:11434",  # Tell LangChain where the local Ollama server is running.
        temperature=1,  # Set a balanced creativity level for the model output.
        num_predict=100,  # Ask the model to keep the generated output around a small size.
    )  # Finish creating the ChatOllama object.

    parser = StrOutputParser()  # Create a parser that converts the model response object into a plain string.

    chain = prompt | llm | parser  # Compose prompt, model, and parser into one LCEL pipeline.

    return chain  # Return the complete chain so another file can reuse it.


if __name__ == "__main__":  
    chain = build_chain()  
    response = chain.invoke(  
        {  
            "topic": "LangChain Expression Language",  
            "analogy_domain": "school assembly line",  
        }  
    )  
    print(response)  
