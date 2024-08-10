import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from crewai_tools import SerperDevTool  # Importando a ferramenta de pesquisa

load_dotenv()

# Carregando o nome do modelo da variável de ambiente
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME')

def read_ctg_file(file_path):
    print(f"Tentando ler o arquivo: {file_path}")
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo {file_path} não existe.")
        return []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    print(f"Lidas {len(lines)} linhas do arquivo.")
    return lines

def process_ctg_content(ctg_content):
    contingencies = []
    current_contingency = None

    for line in ctg_content:
        line = line.strip()
        if line.startswith("'") and line.endswith("'"):
            if current_contingency:
                contingencies.append(current_contingency)
            current_contingency = {'description': line.strip("'")}
        elif line.startswith("BRANCH"):
            parts = line.split()
            if len(parts) >= 4 and current_contingency:
                current_contingency['from_bus'] = parts[1]
                current_contingency['to_bus'] = parts[2]
                current_contingency['circuit'] = parts[3]

    if current_contingency:
        contingencies.append(current_contingency)

    return contingencies

# Configuração dos agentes
llm = ChatOpenAI(temperature=0)
search_tool = SerperDevTool()  # Configurando a ferramenta de pesquisa na web

substation_expert = Agent(
    role='Especialista em Subestações',
    goal='Identificar corretamente os nomes e tensões das subestações brasileiras, incluindo transformadores',
    backstory="""Você é um especialista em subestações do sistema elétrico brasileiro. 
    Seu conhecimento abrange todas as subestações da Rede Básica de Transmissão do Brasil, 
    do Sistema Interligado Nacional (SIN) e do Operador Nacional do Sistema Elétrico (ONS).
    Você é capaz de identificar com precisão os nomes completos das subestações a partir de suas siglas,
    e distinguir entre linhas de transmissão e transformadores.""",
    tools=[search_tool],  # Adicionando a ferramenta de pesquisa ao agente
    llm=llm,
    verbose=True
)

formatter = Agent(
    role='Formatador de Contingências',
    goal='Formatar corretamente todas as contingências do sistema elétrico conforme o formato solicitado',
    backstory="""Você é especializado em formatar informações de contingências do sistema elétrico 
    de acordo com padrões específicos. Seu trabalho é garantir que todas as informações estejam 
    no formato correto e sejam facilmente compreensíveis. Você sabe diferenciar entre linhas de transmissão (TL) 
    e transformadores (TR) baseado nas tensões e características das subestações envolvidas.""",
    tools=[search_tool],
    llm=llm,
    verbose=True
)

def format_contingencies(file_path, substation_name):
    ctg_content = read_ctg_file(file_path)
    contingencies = process_ctg_content(ctg_content)
    contingencies_str = "\n".join([f"{c['description']}" for c in contingencies])

    identify_task = Task(
        description=f"""Identifique os nomes completos e tensões das subestações para cada contingência.
        Use seu conhecimento sobre o sistema elétrico brasileiro para fornecer informações precisas e completas.
        Formato da saída: número,tipo,de_subestação,tensão_de,para_subestação,tensão_para
        Exemplo: 
        1, TL, CAMPOS-RJ345, 345, RNSUL-ES345, 345, LT 345 kV Campos - Rio Novo do Sul
        2, TR, RNSUL-ES345, 345, RNSULB-ES138, 138, TR 345/138 kV Rio Novo do Sul
        
        Contingências:
        {contingencies_str}
        
        IMPORTANTE: 
        1. Certifique-se de processar e incluir TODAS as contingências listadas acima.
        2. Use os nomes EXATOS das subestações como aparecem no arquivo, incluindo siglas e códigos.
        3. Identifique corretamente se é uma linha de transmissão (TL) ou um transformador (TR) baseado nas tensões.
        4. Para transformadores, a tensão de saída será diferente da tensão de entrada.""",
        agent=substation_expert,
        expected_output="Lista completa de contingências com informações detalhadas e precisas das subestações",
        verbose=2
    )

    format_task = Task(
        description=f"""Formate TODAS as contingências usando as informações fornecidas pelo Especialista em Subestações.
        Use o seguinte formato:
        Nº da Contingência, Tipo, Nome Barra De, Tensão Barra De, Nome Barra Para, Tensão Barra Para, Descrição
        Exemplo: 
        1, TL, CAMPOS-RJ345, 345, RNSUL-ES345, 345, LT 345 kV Campos - Rio Novo do Sul
        2, TR, RNSUL-ES345, 345, RNSULB-ES138, 138, TR 345/138 kV Rio Novo do Sul
        
        Certifique-se de incluir TODAS as contingências e que a descrição siga estas regras:
        1. Use 'LT' para linhas de transmissão e 'TR' para transformadores.
        2. Inclua a tensão e os nomes EXATOS das subestações como fornecidos pelo Especialista.
        3. Para transformadores, use o formato: TR tensão_primário/tensão_secundário kV Nome_Subestação
        
        Subestação de referência: {substation_name}
        
        IMPORTANTE: Verifique se todas as contingências fornecidas pelo Especialista em Subestações foram incluídas na sua formatação.""",
        agent=formatter,
        expected_output="Lista formatada completa de todas as contingências conforme especificações, com alta precisão nos nomes das subestações e identificação correta de LTs e TRs",
        verbose=2
    )

    crew = Crew(
        agents=[substation_expert, formatter],
        tasks=[identify_task, format_task],
        verbose=2
    )

    result = crew.kickoff()
    return result

# Exemplo de uso
if __name__ == "__main__":
    file_path = r"D:\repo\ctgGPT\examples\contingencies.ctg"
    substation_name = "Rio Novo do Sul 500 kV"
    print(f"Iniciando processamento do arquivo: {file_path}")
    formatted_contingencies = format_contingencies(file_path, substation_name)
    print("Resultado do processamento:")
    print(formatted_contingencies)
