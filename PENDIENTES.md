# PENDIENTES.md — v003 — 05-08-2026

Decisiones selladas, **no construidas**. Cada entrada tiene un nombre de spec:
las referencias cruzadas entre documentos se hacen por ese nombre, nunca por
número, para que reordenar la lista no rompa nada.

Lo que sí está construido vive en CLAUDE.md.

---

## Siguiente etapa

**Árbol de carpetas y naming**
Sellado. Esta es la forma del proyecto en disco; el gatekeeper la construye, no
el Finder.

```
wPipeline_Projects/
└── DEM/
    ├── project.yml
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
                    │   └── s010_0020_fx_debris_v002.bgeo.sc
                    └── hda/
```

**Código de proyecto de 3 letras.** `DEM`. Prefija todo lo publicado, así un
archivo suelto sigue diciendo de qué show salió.

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
vive en la configuración de la herramienta**, no en cada `project.yml`: los
proyectos eligen de la lista, no inventan códigos.

**Naming.** `work` versiona simple, porque el contexto ya lo da la carpeta:
`dragon_fx_v003.hipnc`. `publish` nombra completo, porque va a viajar fuera de su
carpeta: proyecto + origen + producto + versión —
`DEM_dragon_fx_v001.hdanc`, `s010_0020_fx_debris_v002.bgeo.sc`.

**Publicados inmutables.** Las versiones conviven; se depreca, no se borra.

**Assets publican herramientas, shots publican resultados.** Un asset publica
HDAs; un shot publica caches.

**`project.yml` en la raíz del proyecto, y solo el gatekeeper lo escribe.** Las
carpetas son consecuencia de la fuente de verdad, no al revés.

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

**Dos proyectos como prueba de aceptación**
El segundo proyecto demo **no se crea a mano hoy**: lo crea el gatekeeper cuando
exista, y crearlo *es* su prueba de aceptación. Las pruebas que solo tienen
sentido con más de un show —naming único por prefijo de proyecto, raíces de
producción múltiples, HDAs de dos shows conviviendo en la misma sesión de
Houdini— corren contra los dos. El código de 3 letras del segundo proyecto se
decide ese día, no antes. Razón: un pipeline probado contra un solo proyecto
esconde sus supuestos hardcodeados, porque nunca hay un segundo caso que los
contradiga. Conecta con la idea ya anotada en IDEAS.md de probar múltiples raíces
con varios proyectos.

**Múltiples raíces como prueba de aceptación**
Un tercer proyecto demo, creado por el gatekeeper en una **segunda raíz de
producción** declarada en configuración, junto a los dos de la spec *Dos
proyectos como prueba de aceptación*. Los dos primeros comparten raíz y prueban
que el código de proyecto y el naming no estén hardcodeados; ese par no prueba la
lista de raíces, porque el código que solo usa la primera se ve idéntico al que
la respeta. El tercero es el que ejercita el índice. La segunda raíz vive en el
disco interno, no en un segundo volumen: prueba la lógica de la lista, **no** el
caso de volumen no montado, que ya cubre `volume_root()` de la etapa 0. Al
documentar la prueba hay que decir ese alcance tal cual, sin venderla de más.
Razón: hoy la entrada de INTERVIEW.md *Production roots are externalized
configuration* defiende múltiples raíces sin una prueba que la respalde. Nace de
la idea anotada en IDEAS.md el 05-08-2026.

**Automatización headless (regla de diseño)**
Toda acción del pipeline —publish, export, y el render cuando llegue— debe poder
invocarse por comando, sin humano frente a la pantalla. Es la condición que
permite encadenar dependencias entre pasos y enchufar un job scheduler (Deadline,
Tractor) más adelante sin reescribir nada: la GUI queda como una cáscara que
llama a lo mismo. Nace de la comparación entre Zoic, donde un clic encadenaba las
dependencias hasta el render, y Laika, donde el export entre sim y render se
hacía a mano porque el pipeline todavía estaba en desarrollo.

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
reemplaza el manejo suelto de variables.

---

## Herramienta

**Chequeo de licencia al arrancar**
Verificar que el servidor de licencias responde, leer los días restantes y
avisar con anticipación. **No puede renovar sola**: la activación de Apprentice
requiere la cuenta de SideFX. Se construye junto con el launcher. Modelado en el
aviso de licencias de Zoic y Laika.

---

## Portafolio

**README del repo**
Incluye la declaración, con palabras de Carlos, de cómo se usó IA en el proyecto
y qué decidió él. Decisión sellada: **no se pone `Co-Authored-By` en los
commits**; la atribución va una sola vez en el README, explicada. Es más honesto
y más informativo que repetir una línea automática en cada commit.
