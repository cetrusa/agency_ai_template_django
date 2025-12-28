# Agency Manifest

## Principios
- Transparencia radical en objetivos, entregables y bloqueos.
- IA como copiloto: nunca desplazar criterio humano, siempre justificar decisiones.
- Documentación continua y versionada.
- Seguridad por defecto: credenciales fuera del repositorio, revisión de dependencias.

## Flujo recomendado
1. Definir alcance usando `PROMPTS/00_MASTER_PROMPT.md`.
2. Encadenar roles (producto → arquitectura → backend → frontend → devops → documentación).
3. Validar avances en `PROJECT_BASE` y registrar aprendizajes en `HOW_TO_USE.md`.

## Métricas de calidad
- Cobertura de pruebas mínima 80%.
- Tiempo de onboarding < 30 minutos siguiendo `SCRIPTS/first_run.md`.
- Deploy reproducible via `docker-compose` + scripts provistos.
