# Pixel Art Game Studio

[← README principal](../../README.md) · Español · Traducción asistida por máquina; pendiente de revisión por hablantes nativos.

<!-- section: overview -->
## Descripción general

Pixel Art Game Studio es una skill de Claude Code junto con un equipo de ocho subagentes
especializados para crear juegos originales en 2D con pixel art. Usted describe el juego que imagina,
lo que no le gusta del resultado actual y lo que quiere cambiar a continuación. Claude planifica el
trabajo, escribe el código, genera los gráficos, ejecuta las pruebas, corrige los errores que puede
reproducir e informa solo de lo que realmente verificó.

Está pensado para aventuras narrativas acogedoras, simuladores de vida y de granja, juegos de rol con
mucho diálogo, juegos de exploración con vista cenital y juegos de puzles, aunque también sirve para
otras ideas originales en 2D. Cuatro partes se mantienen separadas: la **skill** (instrucciones), los
**agentes** (especialistas), los **scripts** (herramientas deterministas) y **su juego** (su propio
directorio de proyecto).

<!-- section: features -->
## Características

- Un flujo de Game Director que convierte una idea suelta en un diseño breve y en un bucle jugable
  mínimo.
- Ocho especialistas con responsabilidades claras, listas de herramientas limitadas e informes
  estructurados.
- Pixel art procedural: las especificaciones JSON se convierten en hojas de sprites PNG reales,
  metadatos y vistas previas. La misma especificación produce siempre los mismos bytes.
- Un contrato de datos para mapas, decoración, diálogos, misiones, objetos y traducciones, con un
  validador que detecta salidas inalcanzables, ramas de diálogo imposibles y claves de texto que faltan.
- Control de calidad con niveles de gravedad, informes de defectos reproducibles y correcciones
  verificadas con pruebas de regresión.
- Un instalador seguro con simulación, detección de conflictos, copias de seguridad y una
  desinstalación cuidadosa.

<!-- section: agents -->
## El equipo de agentes

Hay nueve roles. El **Game Director** es la propia skill y se ejecuta en su sesión principal de Claude
Code: mantiene el diseño, redacta las tareas, revisa cada resultado y decide cuándo algo está
terminado. Los ocho subagentes son:

| Agente | Responsabilidad |
| --- | --- |
| `pixel-artist` | dirección de arte, especificaciones de recursos, sprites y tiles generados |
| `npc-story-engineer` | personajes, diálogos ramificados, indicadores, misiones |
| `world-builder-level-design` | estructura de los mapas, colisiones, puntos de aparición, salidas |
| `world-builder-environmental-content` | decoración, puntos de interés, ambiente de cada región |
| `ui-engineer` | menús, HUD, cuadro de diálogo, pantallas de inventario y guardado |
| `gameplay-engineer` | movimiento, estado del juego, inventario, misiones, guardado |
| `qa-tester` | pruebas, ejecuciones de pruebas, informes de defectos |
| `bug-fixer` | correcciones de la causa raíz con pruebas de regresión |

Más detalles: [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Arquitectura

El Director es la skill y no un subagente, porque necesita ver sus peticiones y mantener una única
fuente de verdad (`design/GAME_DESIGN.md`, `ART_DIRECTION.md` y otros cinco documentos breves). Los
especialistas reciben tareas concretas, trabajan en los archivos que les corresponden y devuelven un
informe; no pueden lanzar otros agentes. El contenido del juego vive en una carpeta `data/`
independiente del motor, de modo que la historia, los niveles y el entorno pueden avanzar en paralelo y
comprobarse sin arrancar el motor. Si los subagentes no están disponibles, el Director realiza los
mismos pasos por sí mismo, uno tras otro. Consulte [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Requisitos previos

- Claude Code (comprobado con la versión 2.1.312).
- Python 3.9 o posterior; no se necesitan paquetes adicionales.
- Para juegos reales, el motor que elija, como Godot 4 o el SDK de .NET para MonoGame. La skill
  comprueba lo que está instalado y pregunta antes de instalar cualquier cosa.

<!-- section: installation -->
## Instalación

La forma más sencilla es instalarlo como plugin desde Claude Code. La skill se llama entonces `/pixel-art-game-studio:pixel-art-game-studio` y los agentes llevan el prefijo `pixel-art-game-studio:`:

```text
/plugin marketplace add Rodinyamert48/pixel-art-game-studio
/plugin install pixel-art-game-studio@pixel-art-game-studio
```

O bien, sin el sistema de plugins: Clone el repositorio y luego elija cómo instalar. Revise primero cada cambio con `--dry-run`:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

El ámbito de proyecto escribe en `<project>/.claude/` y el de usuario en `~/.claude/`. Los archivos
existentes que el instalador no creó nunca se reemplazan. Use `--update` para actualizar una
instalación (los archivos antiguos se respaldan) y `--uninstall` para eliminar solo los archivos sin
cambios que instaló. También puede ejecutar Claude Code directamente dentro de este repositorio o
copiar las carpetas a mano. Todas las opciones están en [INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Inicio rápido

Abra Claude Code en la carpeta de su proyecto y escriba:

```text
/pixel-art-game-studio Crea un juego original y acogedor de pixel art con vista cenital, con un pequeño pueblo, un bosque, tres personajes, diálogos ramificados, ciclo de día y noche y sistema de guardado.
```

El Director elige valores predeterminados razonables, escribe un diseño breve y construye primero una
versión jugable pequeña. Para llamar directamente a un especialista, menciónelo, por ejemplo
`@agent-qa-tester`.

<!-- section: examples -->
## Peticiones de ejemplo

```text
/pixel-art-game-studio Añade una región pantanosa con niebla, dos personajes y una misión con dos finales.
/pixel-art-game-studio El pueblo se ve vacío. Añade detalles y pequeños descubrimientos, pero deja libres los caminos.
/pixel-art-game-studio Revisa este juego, ejecuta todas las pruebas disponibles y corrige los errores reproducibles.
```

Puede escribir sus peticiones en cualquier idioma. Hay un ejemplo completo en
[examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Flujos de trabajo

- **Crear un juego**: de la idea a la entrega en 14 etapas, empezando por un bucle jugable mínimo.
- **Ampliar un juego**: examinar el proyecto existente, hacer el cambio coherente más pequeño y
  comprobar que no haya regresiones.
- **Probar y corregir**: ejecutar pruebas reales, informar de defectos y corregir los confirmados con
  un número limitado de intentos.
- **Generar recursos**: primero la dirección de arte, después las especificaciones, los PNG y las
  vistas previas.
- **Revisión de lanzamiento**: un veredicto respaldado por pruebas: listo, listo con problemas conocidos
  o no listo.

Resumen: [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Pruebas y corrección de errores

El agente de QA descubre qué herramientas tiene realmente el juego, convierte los criterios de
aceptación en pruebas, las ejecuta y redacta informes de defectos con gravedad, pasos y evidencias. El
corrector de errores reproduce cada defecto, corrige la causa raíz, añade una prueba de regresión y
vuelve a ejecutar las comprobaciones. Nunca se permite debilitar ni borrar pruebas. Para probar este
repositorio:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Detalles: [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Limitaciones

- No crea por sí solo juegos comerciales terminados; espere una base que funciona y que crece con sus
  comentarios.
- Sin un motor instalado, solo se pueden verificar los datos, los recursos y la lógica independiente
  del motor.
- Las comprobaciones estructurales no pueden juzgar si el arte se ve bien o si un juego es divertido;
  para eso hace falta una persona.
- Las traducciones son asistidas por máquina y esperan la revisión de hablantes nativos.

<!-- section: troubleshooting -->
## Solución de problemas

Si la skill no aparece, compruebe que `SKILL.md` esté en `.claude/skills/pixel-art-game-studio/`. Si no
se encuentran los agentes, reinicie Claude Code después de crear `.claude/agents/`. Si el instalador
termina con el código 2, encontró un archivo que no creó; lea el plan que mostró. Encontrará más
respuestas en [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Contribuir

Las contribuciones son bienvenidas, sobre todo las revisiones de estas traducciones por hablantes
nativos. Lea [CONTRIBUTING.md](../CONTRIBUTING.md) y el [Código de conducta](../CODE_OF_CONDUCT.md)
antes de abrir una pull request.

<!-- section: license -->
## Licencia

Pixel Art Game Studio se publica bajo una [licencia de solo uso](../../LICENSE): puede usarlo gratis, pero no
puede venderlo, modificarlo ni redistribuirlo. Los juegos que cree con él le pertenecen.
