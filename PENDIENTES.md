# PENDIENTES.md — v005 — 06-08-2026

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

---

## Etapa 1a — configuración y creación de proyectos

La etapa 1 se partió en dos. **1a** es configuración de la herramienta y creación
de proyectos; **1b** es secuencia, shot y asset dentro de un proyecto que ya
existe. Razón: 1a se prueba sola —crear los tres proyectos demo en dos raíces *es*
su prueba de aceptación— y cabe en una etapa chica.

**JSON como formato de la fuente de verdad**
El project file es `project.json`, no `project.yml`. Ningún intérprete de esta
máquina lee YAML —ni el Python del sistema 3.12.3 ni el embebido de Houdini
3.11.7—; los dos leen `json` de biblioteca estándar. Verificado con salida cruda
en el MAPA de s006. Razón de fondo, más allá de la dependencia: YAML existe para
que un humano edite el archivo a mano, y la spec *Árbol de carpetas y naming*
prohíbe justamente eso —solo el gatekeeper escribe—. Sería pagar una dependencia
en dos intérpretes por una comodidad que el diseño no permite usar. Alcance:
decide el project file, **no** el formato de la configuración de la herramienta,
que se sella en *Configuración de la herramienta en dos capas*.

**Configuración de la herramienta en dos capas**
Lo que hoy se llamaba "configuración de la herramienta" son dos cosas con reglas
opuestas y viven separadas:

- **Política del pipeline** —lista cerrada de departamentos, gramática de
  nombres, padding de versiones—: igual en cualquier máquina, versionada en el
  repo. Es parte de lo que la herramienta es, y de lo que un entrevistador abre.
- **Configuración de máquina** —la lista de raíces de producción—: local, **fuera
  de git**. Una ruta de Dropbox en un repo público es hardcodear mudado de lugar.

Orden de descubrimiento: variable de entorno si está definida → archivo local del
usuario → defaults versionados del repo. La variable de entorno permite apuntar la
herramienta a otra configuración sin tocar archivos.

Razón: con un archivo único hay que elegir entre publicar la ruta local o dejar la
política fuera del portafolio, y ninguna sirve.

**Descubrimiento de proyectos por escaneo**
"Qué proyectos existen" se contesta escaneando las raíces declaradas en busca de
`project.json`. No hay registro central. Esto **no** contradice la entrada de
INTERVIEW.md *The gatekeeper is the only writer*: son dos preguntas de nivel
distinto. Qué **contiene** un proyecto lo contesta siempre `project.json` y jamás
el filesystem; **dónde** están los project files es la pregunta de arranque, y si
su respuesta viniera de la fuente de verdad sería huevo y gallina.

El escaneo se implementa como **operación de la capa de abstracción** sellada en
*Fuente de verdad abstraída*, no como código suelto: el día que conteste Flow o
Kitsu, ningún consumidor cambia. Es la primera operación concreta de esa capa.

Descartado el registro central porque crea una segunda verdad que se desincroniza
en silencio, y un registro que puede mentir es peor que un escaneo lento.

Carpetas sin `project.json` se ignoran sin ruido —esto cubre `_etapa0_test`, que
vive en la raíz de producción y no es un proyecto.

**Campos de project.json**
Seis campos, sin contenedores vacíos:

```
schema_version   entero, hoy 1
code             código de proyecto de 3 letras
name             nombre legible
root             nombre lógico de la raíz
houdini_version  versión clavada al crear
created          timestamp ISO en UTC
```

`root` guarda el **nombre lógico** de la raíz (`main`, `internal`), nunca su ruta:
la configuración declara las raíces con nombre y el proyecto dice en cuál vive.
Guardar la ruta absoluta rompería un archivo inmutable el día que el volumen
cambie de nombre o se monte en otra máquina. Además es verificable: la herramienta
encontró el archivo escaneando cierta raíz y puede confirmar que el campo
coincide.

`houdini_version` se clava al crear, con la detectada en ese momento; el fallback
a "la más reciente instalada" queda solo para archivos que no la declaren, según
*Version pinning de Houdini por proyecto*.

Sin contenedores vacíos de secuencias ni assets: los agrega la etapa 1b, y
`schema_version` existe para que ese cambio sea declarado y no silencioso.

**Gramática del código de proyecto**
`code`: exactamente 3 caracteres, solo `A`–`Z` mayúsculas. Sin dígitos, sin
acentos. `DEV` es palabra reservada.

`name`: texto libre no vacío, cualquier idioma y acentos; no toca el disco, porque
la carpeta se llama por el `code`.

Sin dígitos a propósito: 17.576 combinaciones alcanzan para una carrera entera, y
admitir dígitos abre `S01`, que se lee como secuencia. Cerrar el alfabeto hace que
el código sea inconfundible dentro de cualquier nombre de archivo.

`DEV` reservado porque `dev` ya es secuencia reservada y daría rutas como
`DEV/seq/dev/`: legal para la máquina, trampa para el humano.

La gramática de secuencias, shots y assets se sella en la etapa 1b.

**Unicidad global del código de proyecto**
El código es único en **todas** las raíces, no dentro de cada una. Razón: el
prefijo viaja pegado a cada archivo publicado y esos archivos terminan cargados
juntos en la misma sesión de Houdini; si la unicidad fuera por raíz, dos shows en
volúmenes distintos podrían llamarse igual y colisionar el día que alguien abre
los dos. La raíz es un detalle de almacenamiento, el namespace es global. Lo
verifica el escaneo de *Descubrimiento de proyectos por escaneo*.

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

**Qué escribe la creación de un proyecto**
En disco: la carpeta del proyecto, `project.json`, y las dos carpetas de primer
nivel `assets/` y `seq/`. Nada más. Sin los cuatro tipos de asset, sin la
secuencia `dev`: los crea la etapa 1b al vuelo cuando llegue el primer asset o
shot. `assets/` y `seq/` sí van porque son la forma del proyecto.

Si el código ya existe en cualquier raíz: error, no se toca nada, y el mensaje dice
en qué raíz se encontró.

Si existe la carpeta pero falta `project.json`: error, no se repara. Reparar
significaría escribir un project file dentro de una carpeta cuyo contenido la
herramienta no creó ni entiende, adoptando basura como si fuera un show. El
gatekeeper no adopta lo que no escribió. Costo aceptado: un proyecto a medio crear
se borra a mano.

**Paquete importable y superficie CLI**
El código nuevo vive en un paquete `wpipeline/` en la raíz del repo. Razón: las
herramientas que corran dentro de Houdini importan, no ejecutan, y hoy
`launch_houdini.py` no se puede importar sin ejecutarse porque termina en
`os.execve`.

`launch_houdini.py` **no se mueve** en esta etapa: es de la etapa 0, funciona, y
migrarlo hoy mezclaría una refactorización con una etapa nueva. Migra en 1b o
cuando estorbe.

Houdini encuentra el paquete vía `PYTHONPATH` declarado en el package de
*Integración Houdini vía packages* —el mismo mecanismo que ya sirve HDAs,
sirviendo código—. El gatekeeper todavía no escribe packages: eso llega cuando
haya HDAs de dos proyectos que cargar.

CLI de un solo comando con subcomandos, no un script por acción, para que la
validación viva en un lugar: `wpipeline create-project DEM --name "Demo Project"`.
Salida en texto legible por defecto, bandera `--json` para salida estructurada, y
código de salida 0/1 siempre confiable. Razón: *Automatización headless* exige
invocación sin humano delante, y un comando que solo imprime prosa obliga a quien
lo llame a parsear texto.

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
sentido con más de un show —naming único por prefijo de proyecto, y HDAs de dos
shows conviviendo en la misma sesión de Houdini— corren contra los dos. El código
de 3 letras del segundo proyecto se decide ese día, no antes. Razón: un pipeline
probado contra un solo proyecto esconde sus supuestos hardcodeados, porque nunca
hay un segundo caso que los contradiga. La prueba de raíces múltiples vive
aparte, en la spec *Múltiples raíces como prueba de aceptación*.

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
