# Herramienta Electoral

Arquitectura hibrida Three-Tier + Pipes and Filters para fact-checking electoral.

## Capas
- frontend/: presentacion (Streamlit)
- backend/: aplicacion (FastAPI) y pipeline de IA
- database: PostgreSQL (configurado desde backend)

## Estructura clave
- backend/app/pipeline/: filtros aislados y orquestador
- backend/app/repositories/: acceso a datos
- backend/app/services/: casos de uso
