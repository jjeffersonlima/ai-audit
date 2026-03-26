import os
import argparse

def create_client_structure(client_name: str, base_path: str = "."):
    """
    Creates the standard folder structure for a new AI Audit client.
    """
    safe_name = "".join([c for c in client_name if c.isalpha() or c.isdigit() or c==' ' or c=='-']).strip()
    root_folder = os.path.join(base_path, f"{safe_name} - AI Audit")
    
    structure = {
        "directories": [
            ".tmp",
            "Meeting Transcripts",
            "Meeting Transcripts/Sales Calls",
            "Meeting Transcripts/Discovery Calls",
            "Meeting Transcripts/Process Mapping Calls",
            "Client Context",
            "Process Documentation",
            "Process Documentation/Onboarding Responses",
            "AI Audit",
        ],
        "files": {
            "Client Context/Client_Profile.md": "# Client Profile\n\n**Company Name:** {client_name}\n**Website:** [URL]\n**Industry:** [Industry]\n**Description:** [Brief description of what they do]\n\n## Key Stakeholders\n- Name / Role\n",
            "Process Documentation/Onboarding Responses/Pre-Discovery Questionnaire.md": """# Pre-Discovery Questionnaire

## Seção 1 — Perfil da Empresa e Contexto
1. Nome da empresa:
2. Website:
3. Segmento / Indústria principal:
4. Modelo de negócio (B2B, B2C, B2B2C, Marketplace):
5. Faturamento anual:
6. Tempo de mercado (anos):
7. Composição do time de vendas (BDRs, SDRs, Closers, Team Leaders, Outros):
8. Existe gestor/diretor comercial dedicado?
9. Nível de adoção de tecnologia no time comercial (Básico, Intermediário, Avançado, De ponta):

## Seção 2 — Processo de Vendas Atual
10. Descreva as etapas do seu funil de vendas atual:
11. Qual o ciclo médio de vendas?
12. Leads/mês:
13. Taxa de conversão geral:
14. Ticket médio:
15. CAC:
16. Tempo dedicado à prospecção/dia:
17. Ligações/dia:
18. E-mails/mensagens por dia:
19. Reuniões/semana:
20. Negócios fechados/mês:

## Seção 3 — Canais e Estratégias de Aquisição
21. Quais canais de aquisição você utiliza atualmente? (Outbound, Inbound, Indicação, Parcerias, Eventos, Redes Sociais):
22. Qual canal traz MAIS leads?
23. Qual canal traz leads de MELHOR qualidade?
24. Qual canal você otimizaria para conseguir bater suas metas?
25. Como vocês fazem prospecção ativa hoje? (Ligação, Linkedin DM, E-mail frio, Redes sociais):
26. Como vocês geram listas de leads hoje? (6 opções):
27. Quanto tempo o vendedor gasta por dia em prospecção?
28. Como vocês nutrem leads que não estão prontos para comprar?

## Seção 4 — Mapeamento de Micro-Processos
*(Para cada cargo ativo: BDRs, SDRs, Closers, Leaders, Outros)*
29. Cargo 1 - Subprocesso 1 (Nome e Descrição):
30. Cargo 1 - Subprocesso 2 (Nome e Descrição):
31. Cargo 1 - Subprocesso 3 (Nome e Descrição):
*(Repetir para outros cargos)*

## Seção 5 — Stack Tecnológico e Ferramentas
32. Vocês usam CRM?
33. Qual CRM?
34. Nível de utilização do CRM pelo time:
35. O CRM está integrado com outras ferramentas? Quais?
36. Ferramentas que o time comercial usa (Nome, Finalidade, Frequência — dinâmico):
37. Vocês têm alguma automação implementada hoje?

## Seção 6 — Dores, Gargalos e Objetivos
38. Quais são os 3 maiores gargalos no processo de vendas hoje?
39. Onde o time comercial MAIS perde tempo? (Ranking 1-5: Prospecção manual, Qualificação de leads, Tarefas administrativas, Follow-up, Relatórios/CRM):
40. Se o time de vendas pudesse pedir ao gênio da lâmpada alguma solução, qual seria?
41. Qual o principal objetivo com automação e IA em vendas? (até 3 de 8 opções):
42. Qual seria uma "vitória rápida" que mostraria valor imediato?
43. Algo mais que gostaria de compartilhar?
""",
            "AI Audit/VALUE Scoring Matrix.csv": "Category,Criteria,Score,Notes\nEthics,Fairness,,\nTech,Robustness,,\n",
            "AI Audit/Final Audit Report.md": "# Final Audit Report\n\n*Pending completion of audit phases.*"
        }
    }

    if os.path.exists(root_folder):
        print(f"Warning: Directory '{root_folder}' already exists.")
        return

    os.makedirs(root_folder)
    print(f"Created directory: {root_folder}")

    for directory in structure["directories"]:
        dir_path = os.path.join(root_folder, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created subdirectory: {dir_path}")

    for filename, content in structure["files"].items():
        file_path = os.path.join(root_folder, filename)
        
        # Format content if it has placeholders
        if "{client_name}" in content:
            content = content.format(client_name=client_name)
            
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Created template: {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Client Audit Structure")
    parser.add_argument("name", help="Name of the client")
    args = parser.parse_args()
    
    create_client_structure(args.name)
