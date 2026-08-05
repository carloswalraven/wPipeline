# PENDIENTES.md — v001 — 05-08-2026

Decisiones selladas, **no construidas**. Cada entrada tiene un nombre de spec:
las referencias cruzadas entre documentos se hacen por ese nombre, nunca por
número, para que reordenar la lista no rompa nada.

Lo que sí está construido vive en CLAUDE.md.

---

## Siguiente etapa

**Árbol de carpetas y naming v001**
Estructura completa de proyecto: secuencia, shot, assets, `work`/`publish`,
departamentos. Se decide mirando un árbol-mockup completo de una sola vez, no
respondiendo pregunta por pregunta — la forma del árbol solo se juzga viéndolo
entero.

---

## Arquitectura sellada

**Raíces de producción múltiples y configurables**
La configuración guarda una **lista** de raíces de producción, no una sola, y
cada proyecto sabe en cuál vive. Hoy hay una sola raíz, pero la arquitectura ya
lo soporta. Razón: en un estudio los shows suelen vivir en volúmenes distintos,
y descubrir eso tarde obliga a reescribir todas las rutas.

**Version pinning de Houdini por proyecto**
La versión de Houdini es un atributo del proyecto en la fuente de verdad, no una
preferencia de la máquina. Elegir la más reciente instalada pasa a ser el
**fallback** para proyectos que no declaran ninguna, no la regla. Razón: las
sims y los HDAs no se garantizan reproducibles entre versiones, y un show tiene
que seguir siendo reproducible meses después de cerrado.

**Fuente de verdad abstraída**
Un archivo local JSON o YAML, detrás de una capa de abstracción, para poder
enchufar Flow o Kitsu en fase 2 sin reescribir el pipeline que la consume.

**Sistema de estados**
WIP → review → approved → published.

**Publish de HDAs**
Tres pasos: Validar → Extraer → Integrar. Las versiones publicadas son
**inmutables**. Nunca se borran: se deprecan.

**Detección de licencia para extensión**
`hou.licenseCategory()` decide la extensión de salida entre `.hda`, `.hdalc` y
`.hdanc`.

**Integración Houdini vía packages**
Houdini packages y variables de entorno. Es el mecanismo actual de SideFX y
reemplaza el manejo suelto de variables.

---

## Herramienta

**Chequeo de licencia al arrancar**
Verificar que el servidor de licencias responde, leer los días restantes y
avisar con anticipación. **No puede renovar sola**: la activación de Apprentice
requiere la cuenta de SideFX. Se construye junto con el launcher. Modelado en el
aviso de licencias de Zoic y Laika.

**Hook de portapapeles en Claude Code**
Copiar automáticamente la última respuesta al portapapeles. Se monta antes de la
etapa 1.

---

## Portafolio

**README del repo**
Incluye la declaración, con palabras de Carlos, de cómo se usó IA en el proyecto
y qué decidió él. Decisión sellada: **no se pone `Co-Authored-By` en los
commits**; la atribución va una sola vez en el README, explicada. Es más honesto
y más informativo que repetir una línea automática en cada commit.
