# from langchain_community.llms import Ollama
# print("loading model")
# llm = Ollama(model="llama2")
# print("loaded model\n\n")

# print(llm.invoke(""))
# print("\n\n end")

from langchain_community.llms import Ollama
from langchain_community.prompts import PromptTemplate
from langchain_community.chains import LLMChain
from langchain_community.memory import ConversationBufferMemory

# Instantiate the Ollama model
llm = Ollama(model="llama2")

# Define the prompt template
template = """

You are a cold-hearted girl and a counselor. Your job is to provide moral support to the customer. You will give response along with expressions enclosed within $$.

Previous conversation:
{chat_history}

New human question: {question}
Response:
"""

# Create a PromptTemplate from the template
prompt = PromptTemplate.from_template(template)

# Set up the conversation memory
memory = ConversationBufferMemory(memory_key="chat_history")

# Create the conversation chain
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory
)

# Start the conversation with an initial question
response = conversation({"question": "I am feeling depressed lately. Studies aren't going well at school and I'm not able to do anything properly."})

print(response)
print("\n\nEnd of conversation.")

