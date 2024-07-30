from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
Please format the following contingencies for the substation '{substation_name}':

Content:
{file_content}

Format:
Nº da Contingência, Tipo, Nome Barra De, Tensão Barra De, Nome Barra Para, Tensão Barra Para, Descrição
"""

model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def read_ctg_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_contingency_list(file_path, substation_name):
    file_content = read_ctg_file(file_path)
    formatted_contingency_list = chain.invoke({
        "substation_name": substation_name,
        "file_content": file_content
    })
    return formatted_contingency_list

if __name__ == "__main__":
    file_path = r"D:\PSR Dropbox\Matheus Duarte de Menezes\studies\organon\vale\rns\base\contigencies.ctg"
    substation_name = 'Rio Novo do Sul 500 kV'
    contingency_list = generate_contingency_list(file_path, substation_name)
    print(contingency_list)
