# Triagem estruturada de riscos

Use depois de gerar oportunidades para revisar IA, dados pessoais, decisões
automatizadas, segurança, transparência e governança.

- Confirme a jurisdição no `working/audit_manifest.json`.
- Não dê parecer jurídico ou declare conformidade definitiva.
- Para categorias de alto impacto (saúde, financeiro, biométrico, crianças,
  emprego ou crédito), marque a necessidade de revisão jurídica/privacidade e
  não trate a oportunidade como executável sem validação dos controles.
- Vincule cada observação à oportunidade e às evidências existentes.
- Registre controles ausentes como perguntas pendentes.

A avaliação oficial é recalculada pelo núcleo:

```bash
ai-audit analyze-risks --workspace /path/to/workspace
ai-audit validate-result --workspace /path/to/workspace
```
