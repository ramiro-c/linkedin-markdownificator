# Mejoras propuestas — linkedin-markdownificator

## CLI (argparse)

- [ ] `--template` para elegir template sin editar `processer.py`
- [ ] `--cached` para skipear scraping y usar HTML local
- [ ] `--headless` para no abrir la ventana del browser
- [ ] `--omit` para excluir secciones desde consola

## Headless mode

- [ ] Agregar `--headless` que pase `options.add_argument("--headless")`
- [ ] Útil después del primer login (la sesión queda cacheada en `selenium/`)

## Selectores frágiles

- [ ] Extraer los CSS selectors de `processer.py` a un archivo `selectors.json`
- [ ] Documentar cada selector con su propósito y alternativa
- [ ] Considerar selectores más semánticos si LinkedIn los expone

## Error handling

- [ ] Agregar `try/except` en el pipeline de extracción
- [ ] Mensajes de error claros cuando un selector no matchea
- [ ] Manejar timeout de selenium gracefulmente

## Separar enrichment de markdownify()

- [ ] Mover la lógica de agrupación de experiencia (líneas 59-83 de `processer.py`) a su propia función
- [ ] Hacerla testeable unitariamente
- [ ] Aplicar mismo patrón a otras secciones si aplica

## Type hints

- [ ] Agregar tipos a todas las funciones
- [ ] `def markdownify() -> None`, `def repeated_string(s: str) -> str`, etc.

## Tests

- [ ] Test para la lógica de enrichment de experiencia
- [ ] Test para `repeated_string()` con edge cases
- [ ] Test de integración que corra el pipeline completo con HTML de ejemplo

## Export JSON intermedio

- [ ] `--json` para dump de datos extraídos antes de renderizar
- [ ] Útil para debuggear selectores sin scrapear de nuevo

## Waits configurables

- [ ] Reemplazar `time.sleep(3)` y `time.sleep(2)` por `WebDriverWait` con expected conditions
- [ ] Configurar timeouts por sección

## Reintentar en error de scraping

- [ ] Si una página falla, reintentar N veces (default 3) con backoff
- [ ] No abortar todo el pipeline por una sección

## webdriver-manager

- [ ] Integrar `webdriver-manager` para evitar tener ChromeDriver manual
- [ ] Ya está en `requirements.txt` pero no se usa

## Lint & formatting

- [x] Agregar `ruff` para linting y formateo (reemplaza flake8 + isort + black)
- [x] `pyproject.toml` con configuración de ruff
- [ ] Script de `make format` o equivalente
- [ ] CI check de lint en PRs
- [ ] `pre-commit` hook con ruff para formatear antes de commitear
