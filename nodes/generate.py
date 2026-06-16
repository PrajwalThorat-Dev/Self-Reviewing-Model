from langchain_ollama import ChatOllama
from state.schema import AgentState

llm =ChatOllama(model="llama3.2",temperature=0.7)

def generate_node(state: AgentState) -> str:
      response=llm.invoke(state["user_input"])

      return {
            "draft":response.content,
            "iteration":state["iteration"]+1
      }

