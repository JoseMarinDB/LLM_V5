from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import get_openai_callback



def llm_invoke(prompt_string): # Renombrado para claridad
    llm = ChatOpenAI(model="o4-mini", temperature=1)

    try:
        with get_openai_callback() as cb:
            # Si el prompt_string es el texto final y no una plantilla con variables
            result = llm.invoke(prompt_string)
            return result.content, cb.total_cost
    except Exception as e:
        print(f"Error LLM: {e}")
        return None, None