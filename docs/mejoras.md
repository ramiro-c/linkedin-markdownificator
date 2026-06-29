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

---

# Automatizar carga de datos a Linkedin

## Respuesta cruda de Gemini 

¡Ah, vale! Te entendí perfectamente ahora. Quieres meterle código o usar una herramienta para que tu propio perfil de LinkedIn se actualice solo, sin tener que pasar una tarde entera copiando, pegando y haciendo clics en la web.

```
Como la API oficial de LinkedIn te va a cerrar la puerta en la cara (por las restricciones que te comenté antes), en el mundo del desarrollo usamos **vías alternativas** para saltarnos ese muro. Aquí tienes las dos opciones reales para lograrlo:

---

## Opción 1: Automatización del Navegador (La vía de código)
En lugar de comunicarte con una API, creas un script que simula que tú mismo estás sentado frente a la pantalla introduciendo los datos. 

* **Herramientas:** Python (con **Selenium** o **Playwright**) o Node.js (con **Puppeteer**).
* **Cómo funciona:** El código abre un navegador (como Chrome), inicia sesión con tu cuenta, navega hasta tu perfil, hace clic en el botón de "Editar sección" y rellena los campos automáticamente usando los datos que tengas guardados en un archivo JSON, Excel o base de datos.

## Opción 2: Herramientas de automatización y APIs "no oficiales"
Existen plataformas y scripts en GitHub que se saltan la API oficial conectándose a la "API interna" que usa la propia página web de LinkedIn.
* **El truco de la Cookie:** Inicias sesión en LinkedIn en tu navegador, abres las herramientas de desarrollador (F12), vas a la pestaña de *Cookies* y buscas una llamada **`li_at`**. Ese es tu token secreto de sesión.
* **Cómo se usa:** Le entregas esa cookie a herramientas como **Phantombuster**, **TexAu** o a un script propio. Al tener esa cookie, el script puede enviar peticiones directamente a los servidores de LinkedIn para actualizar tu perfil como si fueras tú.

---

> ⚠️ **Consejo de colega:** A LinkedIn le obsesiona cazar bots y cuentas automatizadas. Si usas un script que actualiza 20 puestos de trabajo en un milisegundo, el algoritmo va a sospechar y te pueden bloquear la cuenta. Si vas a programar esto, asegúrate de ponerle **delays** (esperas de 3 a 5 segundos) entre acción y acción para que parezca un comportamiento humano.

¿Tienes conocimientos de programación (como Python o JavaScript) para armar un pequeño script de automatización, o prefieres que busquemos una herramienta ya lista donde no haya que picar código?

```