from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
You are provided with a list of contingencies for the substation '{substation_name}'. Each contingency involves two bus 
bars, and we need to format these contingencies into a specific format. Below is the content of the contingencies file 
and an example of how each contingency should be formatted.

Example format:
Nº da Contingência, Tipo, Nome Barra De, Tensão Barra De, Nome Barra Para, Tensão Barra Para, Descrição
1, TL, CAMPOS-RJ345, 345, RNSUL-ES345, 345, LT 345 kV Campos - Rio Novo do Sul
2, TR, RNSUL-ES345, 345, RNSULB-ES138, 138, TR 345/138 kV Rio Novo do Sul

Observations:
- TL: Transmission Line
- TR: Transformer
- In the description, you have to specify the complete name of the transmission line or transformer.
- If in doubt, use geographical references to identify the substations.

Content:
{file_content}

Please format the contingencies as shown in the example.
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
    file_path = r"D:\repo\ctgGPT\examples\contingencies.ctg"
    substation_name = "Rio Novo do Sul 500 kV"
    contingency_list = generate_contingency_list(file_path, substation_name)
    print(contingency_list)