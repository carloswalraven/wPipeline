# PENDIENTES.md — v007 — 07-08-2026

Decisiones selladas, **no construidas**. Cada entrada tiene un nombre de spec:
las referencias cruzadas entre documentos se hacen por ese nombre, nunca por
número, para que reordenar la lista no rompa nada.

Lo que sí está construido vive en CLAUDE.md.

**Salida de la etapa 1a (07-08-2026).** Se fueron de aquí, construidas y
verificadas, las specs *JSON como formato de la fuente de verdad*,
*Configuración de la herramienta en dos capas*, *Descubrimiento de proyectos
por escaneo*, *Campos de project.json*, *Gramática del código de proyecto*,
*Unicidad global del código de proyecto*, *Qué escribe la creación de un
proyecto*, *Lectura tolera vista parcial, escritura exige certeza*, *Paquete
importable y superficie CLI*, *Contrato de errores del paquete* y *Raíces de
producción múltiples y configurables*. Las dos specs de aceptación —*Dos
proyectos como prueba de aceptación* y *Múltiples raíces como prueba de
aceptación*— también salieron: la prueba corrió y pasó. Su descripción vive
ahora en CLAUDE.md, con su alcance honesto.

---

## Siguiente etapa — 1b: secuencias, shots y assets

**Árbol de carpetas y naming**
Sellado. Esta es la forma del proyecto en disco; el gatekeeper la construye, no
el Finder.

De este árbol, la etapa 1a construyó **solo los dos primeros niveles**: la
carpeta del proyecto con su `project.json`, y `assets/` y `seq/` vacías. Todo lo
de adentro es de la 1b y se crea al vuelo cuando llegue el primer asset o shot.

```
wPipeline_Projects/
└── DEM/
    ├── project.json
    ├── assets/
    │   ├── char/
    │   │   └── dragon/
    │   │       ├── work/
    │   │       │   └── fx/
    │   │       │       └── dragon_fx_v003.hipnc
    │   │       └── publish/
    │   │           └── hda/
    │   │               ├── DEM_dragon_fx_v001.hdanc
    │   │               └── DEM_dragon_fx_v002.hdanc
    │   ├── prop/
    │   ├── env/
    │   └── fx/
    └── seq/
        ├── dev/
        │   └── dev_0010/
        │       ├── work/
        │       │   └── fx/
        │       └── publish/
        └── s010/
            └── s010_0020/
                ├── work/
                │   ├── fx/
                │   │   └── s010_0020_fx_v012.hipnc
                │   ├── lgt/
                │   ├── cmp/
                │   └── lay/
                └── publish/
                    ├── geo/
                    │   └── DEM_s010_0020_fx_debris_v002.bgeo.sc
                    └── hda/
```

**`assets/` y `seq/` son hermanos.** La dirección de consumo es una sola: los
shots consumen assets, nunca al revés. Un asset que dependiera de un shot dejaría
de ser reusable.

**Cuatro tipos de asset fijos: `char`, `prop`, `env`, `fx`.** Lista cerrada. Se
escriben legibles a propósito y **no** se abrevian a 3 letras: se leen en el
árbol, no se teclean en cada nombre de archivo. `fx` acá es la repisa de
reusables sin dueño; lo que está amarrado a una entidad vive con la entidad (el
fuego del dragón es del dragón).

**Shots de 10 en 10** (`0010`, `0020`), para poder insertar en medio sin
renumerar. **El nombre del shot incluye su secuencia**: `s010_0020`, no `0020`.
Así el nombre es único en todo el show y un archivo suelto se ubica solo.

**Secuencia reservada `dev`.** La palabra `dev` es un nombre de secuencia
especial que el gatekeeper reserva. Ahí viven los shots de exploración
(`dev_0010`) con toda la maquinaria real —`work`/`publish`, versiones,
departamentos— pero sin cámara ni layout de producción. **Nada se renombra
jamás:** cuando un efecto madura, se publica como asset (`assets/fx/`) o se
rehace limpio en el shot real, y el shot `dev` queda como historia. Razón: el
prefijo `dev_` removible (sabor Laika) obliga a renombrar al graduar, y renombrar
rompe todas las rutas que apuntaban al nombre viejo.

**`work`/`publish` como patrón único**, igual en assets que en shots. Una sola
regla que aprender.

**Departamentos con código de 3 letras**: `lgt`, `cmp`, `lay`… `fx` se queda en
dos letras como excepción, por ser el nombre estándar. Es una **lista cerrada que
vive en la configuración de la herramienta**, no en cada `project.json`: los
proyectos eligen de la lista, no inventan códigos.

**Naming.** `work` versiona simple, porque el contexto ya lo da la carpeta:
`dragon_fx_v003.hipnc`. `publish` nombra completo, porque va a viajar fuera de su
carpeta: proyecto + origen + producto + versión —
`DEM_dragon_fx_v001.hdanc`, `DEM_s010_0020_fx_debris_v002.bgeo.sc`. El prefijo de
proyecto aplica a **todo** lo publicado, sin excepción, incluidos los caches de
shot: el ejemplo anterior del cache no lo llevaba y contradecía la regla enunciada
dos párrafos antes.

**Publicados inmutables.** Las versiones conviven; se depreca, no se borra.

**Assets publican herramientas, shots publican resultados.** Un asset publica
HDAs; un shot publica caches.

**`project.json` en la raíz del proyecto, y solo el gatekeeper lo escribe.** Las
carpetas son consecuencia de la fuente de verdad, no al revés.

**Gramática de secuencias, shots y assets**
Sin sellar todavía. Se decide en el chat de planeación **antes** de construir la
1b, igual que se hizo con la gramática del código de proyecto. Lo que ya está
decidido y la restringe: shots de 10 en 10, el nombre del shot incluye su
secuencia, `dev` es secuencia reservada, y los cuatro tipos de asset son lista
cerrada.

El precedente de la 1a vale la pena repetirlo: la gramática vive en la política
versionada y las funciones de validación la reciben como argumento, nunca como
constantes. Eso es lo que hace que la lista cerrada sea configuración y no la
opinión de un estudio horneada en el código.

**El prefijo de proyecto aplica a todo lo publicado**
Sin excepciones: HDAs de asset y caches de shot por igual. La razón de existir del
prefijo es que un archivo publicado viaja fuera de su carpeta —a un escritorio, a
un email, a un directorio de entregas— y ahí el nombre es todo el contexto que
queda. Un cache viaja tanto o más que un HDA: es lo que lighting recoge y arrastra
a otra escena. Que el nombre del shot incluya su secuencia lo hace único dentro
del show; el prefijo lo hace único entre shows.

Descartado quitar el prefijo también de los assets. Descartada de plano la tercera
vía —prefijo en assets y no en shots—: una regla con excepción sin razón que la
explique es la más cara de todas. Corrige el ejemplo que contradecía la regla en
*Árbol de carpetas y naming*.

Nada de esto está construido: la etapa 1a no publica nada todavía.

**Consumo de la política que ya está escrita**
`wpipeline/policy/pipeline.json` ya declara `departments`, `asset_types` y
`version_padding`, y **ningún código las lee todavía**. La 1a solo consume
`project_code`.

Las tres llaves se escribieron desde el principio porque el vocabulario cerrado
es decisión sellada y tenerlo en un archivo de datos es lo que lo hace
configuración. La 1b es la que las consume: `asset_types` al crear un asset,
`departments` al crear una carpeta de trabajo, `version_padding` al nombrar una
versión. Anotado acá para que la deuda esté declarada y no se descubra leyendo
el archivo.

**Migración de launch_houdini.py y deuda de duplicación**
`launch_houdini.py` sigue en la raíz del repo, intacto, con su propio `die()`.
Hoy conviven dos copias de la lógica de detección de versión de Houdini: las
suyas y las de `wpipeline/houdini.py`, que hacen lo mismo y fallan distinto
—`die()` allá, `raise` acá—, según la spec ya construida *Contrato de errores
del paquete*.

La 1b migra el launcher al paquete. Ese día se borran las funciones del script
viejo y quedan las del paquete como únicas. No se hizo en la 1a a propósito:
mezclar una refactorización con una etapa nueva hace que, si algo se rompe, no
se sepa cuál de las dos lo rompió.

---

## Arquitectura sellada

**Version pinning de Houdini por proyecto**
La versión de Houdini es un atributo del proyecto en la fuente de verdad, no una
preferencia de la máquina. Razón: las sims y los HDAs no se garantizan
reproducibles entre versiones, y un show tiene que seguir siendo reproducible
meses después de cerrado.

**Construido:** el campo `houdini_version` se clava al crear el proyecto, con la
versión detectada en ese momento, y se escribe `null` con aviso cuando no hay
Houdini instalado.

**Pendiente:** nadie **lee** ese campo todavía. Falta que abrir un proyecto
respete su versión clavada, y que el fallback a "la más reciente instalada"
aplique solo a los proyectos que declaran `null`. Eso llega cuando el launcher
sea consciente de proyectos, o sea junto con la migración de la spec *Migración
de launch_houdini.py y deuda de duplicación*.

**Fuente de verdad abstraída**
Un archivo local JSON detrás de una capa de abstracción, para poder enchufar Flow
o Kitsu en fase 2 sin reescribir el pipeline que la consume.

**Construido:** la capa existe, con la interfaz de tres operaciones
—`list_projects`, `get_project`, `create_project`— y una implementación por
escaneo del filesystem. Ningún consumidor habla con el disco directamente.

**Pendiente:** el segundo backend. La capa vale exactamente lo que valga el día
que exista una implementación que no sea el filesystem, y hasta entonces es una
promesa razonada, no una demostración. Es fase 2 y no tiene fecha.

Cuando llegue, la interfaz crece con secuencias, shots y assets: la 1b agrega
operaciones y `schema_version` existe para que ese crecimiento sea declarado.

**Automatización headless (regla de diseño)**
Toda acción del pipeline —publish, export, y el render cuando llegue— debe poder
invocarse por comando, sin humano frente a la pantalla. Es la condición que
permite encadenar dependencias entre pasos y enchufar un job scheduler (Deadline,
Tractor) más adelante sin reescribir nada: la GUI queda como una cáscara que
llama a lo mismo. Nace de la comparación entre Zoic, donde un clic encadenaba las
dependencias hasta el render, y Laika, donde el export entre sim y render se
hacía a mano porque el pipeline todavía estaba en desarrollo.

La etapa 1a la respeta ya: `--json` y códigos de salida confiables, y la creación
de proyectos no exige Houdini instalado. Sigue acá porque es una regla que aplica
a cada acción futura, no un pendiente que se cierra.

**USD como fase futura**
El core se mantiene agnóstico de formato. USD no es la arquitectura: entra como
un producto más de publish (`publish/usd/`) en una fase futura. Y esa fase abre
con su propia etapa 0 —una prueba mínima que valide qué permite y qué restringe
la licencia Apprentice con USD en Houdini— antes de diseñar nada encima.

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
reemplaza el manejo suelto de variables. Es también como Houdini va a encontrar
el paquete `wpipeline/`: un `PYTHONPATH` declarado ahí, el mismo mecanismo que
ya sirve HDAs, sirviendo código. El gatekeeper todavía no escribe packages: eso
llega cuando haya HDAs de dos proyectos que cargar.

---

## Herramienta

**Chequeo de licencia al arrancar**
Verificar que el servidor de licencias responde, leer los días restantes y
avisar con anticipación. **No puede renovar sola**: la activación de Apprentice
requiere la cuenta de SideFX. Se construye junto con el launcher. Modelado en el
aviso de licencias de Zoic y Laika.

**Dos fallas, dos mensajes.** El chequeo las distingue en vez de reportar "problema
de licencia" y mandar a buscar:

- **hserver caído** — no responde en `localhost:1715`. El mensaje incluye el
  procedimiento de arranque manual: Licenses > License Administrator > Services >
  Sesinetd Start, después Hserver Start. No pide contraseña de administrador.
- **Licencia vencida** — el servidor contesta y lo que se acabó es la licencia.
  Esta sí requiere la cuenta de SideFX.

Razón: hserver no es un servicio del sistema —no lo levanta init.d ni systemd, lo
dice el propio panel de SideFX—, así que muere en cada reinicio o apagado y no
vuelve solo. Pasó tres veces en cuatro días y el diagnóstico correcto nunca fue
licencia vencida. Un solo mensaje genérico manda a revisar la cuenta cuando lo que
hacía falta eran dos clics. Sellada desde IDEAS.md, entrada del 06-08-2026.

---

## Portafolio

**README del repo**
Incluye la declaración, con palabras de Carlos, de cómo se usó IA en el proyecto
y qué decidió él. Decisión sellada: **no se pone `Co-Authored-By` en los
commits**; la atribución va una sola vez en el README, explicada. Es más honesto
y más informativo que repetir una línea automática en cada commit.

Debe declarar también que los documentos de trabajo del repo están en español y
el código en inglés, para que quien lo abra sepa que la mezcla es deliberada.
