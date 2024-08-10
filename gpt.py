import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME')

def read_ctg_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def generate_contingency_list(file_path, substation_name):
    file_content = read_ctg_file(file_path)
    prompt = f"""
    Por favor, formate as seguintes contingências para a subestação '{substation_name}' em uma lista estruturada.
    Use o formato fornecido abaixo e garanta que todas as contingências sejam incluídas. 
    Certifique-se de que as descrições estejam completas e forneçam informações suficientes para identificação.
    Utilize informações da Rede Básica de Transmissão do Brasil, do Sistema Interligado Nacional (SIN) e do Operador Nacional do Sistema Elétrico (ONS).
    Nunca deixe de fazer todas as contigências do arquivo .ctg.
    Você deve se comportar como um programa de computador que está formatando um arquivo .ctg.
    Garanta que a saída corresponda ao formato do exemplo, identificando TL para linhas de transmissão e TR para transformadores,
    com descrições corretas e nomes completos e precisos das subestações.
    
    Formato:
    Nº da Contingência, Tipo, Nome Barra De, Tensão Barra De, Nome Barra Para, Tensão Barra Para, Descrição
    
    Exemplo:
    1, TL, CAMPOS-RJ345, 345, RNSUL-ES345, 345, LT 345 kV Campos - Rio Novo do Sul
    2, TR, RNSUL-ES345, 345, RNSULB-ES138, 138, TR 345/138 kV Rio Novo do Sul
    
    Conteúdo:
    {file_content}
    """

    response = client.chat.completions.create(model='gpt-4o',
                                              messages=[
                                                  {"role": "system",
                                                   "content": "Você é um engenheiro de estudos elétricos brasileiro."},
                                                  {"role": "user", "content": prompt}
                                              ])
    return response.choices[0].message.content


if __name__ == "__main__":
    file_path = r"D:\repo\ctgGPT\examples\contingencies.ctg"
    substation_name = "Rio Novo do Sul 500 kV"
    contingency_list = generate_contingency_list(file_path, substation_name)
    print(contingency_list)
