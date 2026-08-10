# GLOSARIO.md — v005 — 10-08-2026

Cada término: nombre en inglés, definición en una frase, analogía si la hay.

---

## Programación general

**git** — Control de versiones: guarda una foto completa del proyecto cada vez
que se lo pides y te deja volver a cualquiera. *Analogía:* incrementales de
`.hip`, pero automáticos y con nota de qué cambió. El nombre no es sigla; Linus
Torvalds lo eligió medio en broma (en inglés británico es un insulto suave).

**repo (repository)** — La carpeta que git vigila, más su historial completo.

**commit** — Una de esas fotos: guardar y anotar qué hiciste.

**.gitignore** — Lista de archivos que git debe ignorar y nunca subir.

**path (ruta)** — La dirección de un archivo o carpeta en el disco. *Analogía:*
la ruta de un nodo en Houdini, `/obj/geo1/scatter1`, pero en disco.

**~ (tilde)** — Abreviatura de "mi carpeta de usuario". Sirve para que el mismo
texto funcione en cualquier máquina.

**PATH** — La lista **ordenada** de carpetas donde el sistema busca los
programas; gana la primera coincidencia.

**cd (change directory)** — Moverte a una carpeta en la terminal.

**grep** — Buscador de texto de la terminal: le das un patrón y una
lista de archivos, e imprime cada línea donde aparece. No abre ni edita
nada. Banderas comunes: `-n` agrega el número de línea; `-B3`/`-A3`
muestran 3 líneas de contexto antes (*Before*) y después (*After*) de
cada coincidencia. *Analogía:* Cmd+F, pero para archivos que no tienes
abiertos y varios a la vez.

**mkdir (make directory)** — Crear una carpeta. La bandera `-p` crea también las
intermedias que falten.

**pwd (print working directory)** — "Dime dónde estoy parado".

**bandera / flag** — Opción extra que se le pasa a un comando, empieza con
guiones.

**directorio de trabajo** — La carpeta donde estás parado; los comandos actúan
sobre ella. Claude Code trabaja sobre la carpeta desde donde se lanza.

**&&** — "Y si eso salió bien, haz lo siguiente". Se corta al primer error.

**variable de entorno** — Un valor que se le pasa a un programa al arrancarlo;
vive solo mientras ese programa corre y no toca la instalación.

**hardcodear** — Escribir un valor fijo dentro del código en vez de leerlo de
configuración. Lo que rompe un pipeline en cada actualización.

**configuración externalizada** — Lo contrario: los valores que cambian según la
máquina viven en un archivo de configuración, no en el código.

**fail fast** — Detectar el problema en el primer segundo y fallar con mensaje
claro, en vez de reventar a mitad de una operación.

**orden lexicográfico vs. orden numérico** — Ordenar como texto vs. como número.
Como texto, `21.0.671` le gana a `21.0.1000`, porque compara carácter por
carácter. Bug clásico y silencioso.

**Homebrew** — Gestor de programas de terminal en Mac. *Analogía:* el App Store
de las herramientas de desarrollo.

**gh** — La herramienta de GitHub para terminal: crear repos y subir código sin
abrir el navegador.

**scope (OAuth)** — El alcance de lo que una autorización permite. *Analogía:*
una llave que abre unas puertas y no otras.

**email noreply de GitHub** — Alias que te identifica en GitHub sin exponer tu
correo real en el historial público.

**CLI (Command Line Interface)** — La herramienta se maneja por comandos escritos
en la terminal. *Analogía:* los controles reales de un rig, que existen antes que
su picker.

**GUI (Graphical User Interface)** — La interfaz de ventanas y botones.
*Analogía:* el picker — una cáscara encima de los controles.

**YAML** — Mismo papel que JSON (datos que el código lee), pero legible para
humanos: sin llaves ni comillas, pura indentación.

**headless** — Correr un programa sin interfaz, solo por comando. Es la condición
para que la máquina lo pueda encadenar con otros pasos.

**JSON** — Formato de datos que el código lee y escribe: llaves, comillas y
listas. Es el único formato del proyecto: project file, política y configuración
de máquina. *Analogía:* la ficha técnica de un plano — no es para leerla en voz
alta, es para que otra herramienta la use.

**módulo / paquete** — Un módulo es un archivo `.py`; un paquete es una carpeta
de módulos que se importa como una unidad. *Analogía:* un HDA suelto vs. una
librería de HDAs con su estructura.

**importar** — Cargar código de otro archivo para usar sus funciones, **sin
ejecutarlo como programa**. Un archivo bien hecho no hace nada al importarse.

**excepción (exception) / raise / try-except** — Una excepción es un error que
interrumpe lo que se estaba haciendo; `raise` es lanzarla, `try-except` es
atraparla y decidir qué hacer. *Analogía:* el nodo que se pone rojo en vez de
cerrar Houdini — quien lo mira decide si es fatal o no.

**exit code (código de salida)** — El número que un programa deja al terminar:
`0` es "todo bien", cualquier otro es falla. Es cómo un script sabe si el
comando anterior funcionó, sin leer su texto.

**stdout / stderr** — Los dos canales de salida de un programa: `stdout` es el
resultado y `stderr` son los errores. Están separados para que una máquina pueda
leer el resultado sin que los avisos se le mezclen.

**subcomando** — Una acción dentro de un mismo comando: `wpipeline
create-project` en vez de un programa distinto por acción. *Analogía:* `git
commit` y `git push` — un solo git.

**dataclass** — Una clase de Python que solo guarda campos, escrita en pocas
líneas. *Analogía:* una ficha con casillas fijas.

**unittest / suite de pruebas** — `unittest` viene incluido en Python y corre
pruebas automáticas; la suite es el conjunto completo. Cada prueba afirma algo y
falla ruidosamente si deja de ser cierto. *Analogía:* volver a abrir el mismo
`.hip` de prueba después de cada cambio, pero automático y de golpe.

**biblioteca estándar** — Lo que Python ya trae sin instalar nada. Todo este
proyecto vive ahí: cero dependencias.

**capa de abstracción** — Código que se pone en medio para que quien pregunta no
sepa quién contesta. *Analogía:* un bus de audio — cambias qué está enchufado
atrás sin tocar la mezcla.

---

## Houdini específico

**HDA (Houdini Digital Asset)** — Un grupo de nodos empaquetado como un nodo
nuevo que aparece en el tab menu. *Analogía:* guardar una cadena de efectos como
preset propio.

**.hdanc / .hdalc / .hda** — Extensiones según licencia: Apprentice/Education,
Indie, comercial. Los archivos "nc" no son compatibles con otras licencias.

**hou** — El módulo de Python de Houdini: todas las funciones para hablar con
Houdini desde código.

**hython** — El intérprete de Python que viene **dentro** de Houdini, con `hou`
ya cargado. *Analogía:* Houdini sin ventanas. Un Python normal no puede importar
`hou`.

**tab menu** — El menú que sale al presionar Tab; donde aparecen los nodos
disponibles.

**HOUDINI_OTLSCAN_PATH** — Variable de entorno con las carpetas donde Houdini
busca HDAs al arrancar.

**& (en paths de Houdini)** — Token que significa "y además, inserta aquí el
valor por defecto". Sin él, Houdini pierde sus HDAs de fábrica en esa sesión.

**namespace (en HDAs)** — Prefijo en el nombre interno del operador para evitar
colisiones entre assets con el mismo nombre.

**sesinetd / hserver** — Servidor de licencias local de Houdini. Es la misma
arquitectura del servidor de licencias de un estudio, en tu máquina.

**Houdini packages** — Mecanismo moderno de SideFX para declarar variables y
rutas en un archivo JSON. Es el estándar actual.

**.bgeo.sc** — El formato de cache de geometría de Houdini, comprimido. Es lo que
un shot de FX publica para que lighting lo consuma.

---

## Conceptos de pipeline

**project root ($JOB)** — La raíz desde la que se escriben todas las rutas del
pipeline; el código nunca escribe rutas absolutas. *Analogía:* `$JOB` en
Houdini, o una sesión de DAW con los samples adentro en vez de rutas absolutas.

**version pinning** — Clavar un proyecto a una versión concreta de cada
software, para que siga siendo reproducible meses después.

**gatekeeper** — La herramienta es la única que crea proyectos, shots y assets,
con validación. Nadie crea carpetas a mano en el Finder.

**fuente de verdad (source of truth)** — Quién contesta oficialmente qué existe.
Hoy son los `project.json`; mañana podría ser Flow o Kitsu. Las carpetas son
consecuencia de la fuente de verdad, no al revés.

**schema_version** — Número de versión del formato de un archivo de datos, dentro
del archivo mismo. Sirve para que un cambio de estructura sea declarado y no
silencioso. *Analogía:* la versión de Houdini con la que se guardó un `.hip`.

**nombre lógico (de una raíz)** — El apodo con el que la configuración declara una
raíz de producción (`main`, `internal`); el proyecto guarda ese apodo y nunca la
ruta absoluta. *Analogía:* el nombre de un bus en la consola — la señal sigue
llegando aunque muevas el cable.

**unicidad global** — El código de proyecto es único en **todas** las raíces, no
dentro de cada una, porque el prefijo viaja pegado a cada archivo publicado y dos
shows pueden terminar abiertos en la misma sesión.

**work / publish** — Separación entre lo que estás trabajando y lo que ya está
aprobado y es consumible por otros.

**deprecar** — Marcar una versión publicada como no recomendada, en vez de
borrarla. Las versiones publicadas son inmutables.

**MAPA** — Entrega de solo lectura, antes de implementar: qué existe, qué es
reusable, qué supuestos rompe el cambio.

**job scheduler** — El programa del farm que ejecuta trabajos respetando sus
dependencias: Deadline, Tractor, OpenCue. *Analogía:* ruteo MIDI entre programas
— no le importa quién recibe, mientras hable el protocolo.

**dependencia (de jobs)** — "Yo arranco cuando termine aquel": la relación que
encadena sim → export → render sin que haya un humano apretando el siguiente
paso.

**dev (secuencia reservada)** — La secuencia donde se explora sin cámara ni
layout de producción. Los shots `dev` nunca se gradúan por renombre: lo que
madura se publica como asset o se rehace en el shot real.
