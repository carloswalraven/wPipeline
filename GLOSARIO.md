# GLOSARIO.md — v002 — 05-08-2026

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

---

## Conceptos de pipeline

**project root ($JOB)** — La raíz desde la que se escriben todas las rutas del
pipeline; el código nunca escribe rutas absolutas. *Analogía:* `$JOB` en
Houdini, o una sesión de DAW con los samples adentro en vez de rutas absolutas.

**version pinning** — Clavar un proyecto a una versión concreta de cada
software, para que siga siendo reproducible meses después.

**gatekeeper** — La herramienta es la única que crea proyectos, shots y assets,
con validación. Nadie crea carpetas a mano en el Finder.

**work / publish** — Separación entre lo que estás trabajando y lo que ya está
aprobado y es consumible por otros.

**deprecar** — Marcar una versión publicada como no recomendada, en vez de
borrarla. Las versiones publicadas son inmutables.

**MAPA** — Entrega de solo lectura, antes de implementar: qué existe, qué es
reusable, qué supuestos rompe el cambio.
