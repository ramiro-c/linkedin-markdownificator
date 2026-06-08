# Mejoras propuestas — linkedin-markdownificator

## CLI (argparse)

- [x] `--template` para elegir template sin editar `processer.py`
- [x] `--cached` para skipear scraping y usar HTML local
- [x] `--headless` para no abrir la ventana del browser
- [x] `--omit` para excluir secciones desde consola

## Headless mode

- [x] Agregar `--headless` que pase `options.add_argument("--headless")`
- [x] Útil después del primer login (la sesión queda cacheada en `selenium/`)

## Selectores frágiles

- [x] Extraer los CSS selectors de `processer.py` a un archivo `selectors.json`
- [x] Documentar cada selector con su propósito y alternativa
- [x] Considerar selectores más semánticos si LinkedIn los expone (nada mejor disponible actualmente)

## Error handling

- [x] Agregar `try/except` en el pipeline de extracción
- [x] Mensajes de error claros cuando un selector no matchea
- [x] Manejar timeout de selenium gracefulmente

## Separar enrichment de markdownify()

- [x] Mover la lógica de agrupación de experiencia a `_enrich_experience()`
- [x] Hacerla testeable unitariamente
- [x] Aplicar mismo patrón a otras secciones si aplica (solo Experience tiene anidamiento company/role)

## Type hints

- [x] Agregar tipos a todas las funciones de source
- [x] Type hints en tests

## Tests

- [x] Test para la lógica de enrichment de experiencia (`test_enrich_experience.py`)
- [x] Test para `repeated_string()` con edge cases
- [x] Test de integración que corra el pipeline completo con HTML de ejemplo

## Export JSON intermedio

- [x] `--json` para dump de datos extraídos antes de renderizar
- [x] Útil para debuggear selectores sin scrapear de nuevo

## Waits configurables

- [x] Reemplazar `time.sleep(3)` y `time.sleep(2)` por `WebDriverWait` con expected conditions
- [x] Configurar timeouts por sección

## Reintentar en error de scraping

- [x] Si una página falla, reintentar N veces (default 3) con backoff
- [x] No abortar todo el pipeline por una sección

## webdriver-manager

- [x] Integrar `webdriver-manager` para evitar tener ChromeDriver manual
- [x] Ya está en `requirements.txt` y ahora se usa

## Lint & formatting

- [x] `ruff` para linting y formateo
- [x] `pyproject.toml` con configuración de ruff
- [x] Script de `make format` o equivalente (Makefile con format/lint/check/test/all)
- [x] CI check de lint en PRs (.github/workflows/lint.yml)
- [x] `pre-commit` hook con ruff para formatear antes de commitear (.pre-commit-config.yaml)
