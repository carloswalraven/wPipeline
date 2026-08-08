# PENDIENTES.md — v006 — 07-08-2026

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
  Vive en `wpipeline/policy/pipeline.json`, resuelto con rutas relativas al
  paquete y no al directorio desde el que se invoque.
- **Configuración de máquina** —la lista de raíces de producción—: local, **fuera
  de git**. Una ruta de Dropbox en un repo público es hardcodear mudado de lugar.
  Vive en `~/.config/wpipeline/machine.json`, como un diccionario de nombre
  lógico → ruta: la llave *es* el nombre con el que `project.json` apunta a su
  raíz, y un diccionario garantiza que ese nombre sea único sin validarlo aparte.

**Formato de las dos capas: JSON.** Un solo formato en todo el proyecto —project
file, política y configuración de máquina— y cero dependencias: ningún intérprete
de esta máquina lee YAML. Esto cierra el hueco que dejaba abierto la spec *JSON
como formato de la fuente de verdad*, cuyo alcance era solo el project file.

Orden de descubrimiento, **sin merge**: gana completa la primera capa que existe,
y la carga reporta de qué capa vino. Mezclar tres capas es de donde salen los bugs
de "¿de dónde salió este valor?", y el costo de contestar esa pregunta supera la
comodidad de heredar la mitad de un archivo.

`WPIPELINE_CONFIG` apunta a un **archivo** y reemplaza **solo la capa de máquina**.
La política siempre viene del repo: es parte de lo que la herramienta *es*, no de
dónde está parada, y dejar que una variable de entorno la sustituya convertiría el
vocabulario cerrado de departamentos en uno abierto por la puerta de atrás.

**Los defaults versionados no traen raíces.** Una ruta local en un repo público es
hardcodear mudado de lugar, así que el default de la capa de máquina es la **lista
vacía**. Los defaults del repo aportan política, nunca almacenamiento.

**Cero raíces declaradas es error, con mensaje instructivo completo**: la ruta
exacta del archivo a crear y un contenido de ejemplo copiable de la pantalla. Es
lo primero que le pasa a cualquiera que clone el repo en una máquina limpia, y una
herramienta que dice "no hay raíces" sin decir cómo se declaran obliga a adivinar
o a leer el código.

En `.gitignore` va una línea preventiva para `machine.json`, por si algún día
queda una copia local en la raíz del repo. No hace falta hoy —el archivo vive en
`~/.config`— pero el costo es cero y lo que previene es filtrar una ruta local a
un repo público. Misma lógica que el *Block command line pushes that expose my
email* que ya está activo en GitHub: una red para el error que no piensas cometer.

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

**El escaneo es de un solo nivel por raíz.** Los proyectos son hijos directos de
la raíz, así que se miran las carpetas de primer nivel y se busca `project.json`
adentro de cada una; nada recursivo. La raíz principal vive en Dropbox, donde un
barrido recursivo es lento y además puede tocar archivos *online-only* y forzar su
descarga —el mismo problema que ya obliga a imprimir el tamaño en bytes en el
inventario de la etapa 0.

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

**Lectura tolera vista parcial, escritura exige certeza**
Con raíces múltiples aparece un estado que con una sola no existía: ver *algunas*
de las raíces. Las dos operaciones lo tratan distinto a propósito.

Si una raíz declarada no está montada:

- **Listar proyectos funciona**, con advertencia explícita de cuál raíz falta y la
  lista marcada como parcial. Una respuesta incompleta y rotulada como incompleta
  sigue siendo útil; negarse a contestar no ayuda a nadie.
- **`create-project` falla.** La unicidad global del código no se puede garantizar
  sin ver todas las raíces, y crear con esa duda puede fabricar una colisión que
  no se descubre hasta que ya hay archivos publicados con el prefijo duplicado —o
  sea cuando arreglarlo significa renombrar publicados inmutables.

Mismo trato para un `project.json` ilegible —JSON inválido, o le falta alguno de
los seis campos—: el escaneo lo reporta como advertencia con la ruta exacta y
sigue; `create-project` falla mientras exista uno roto en cualquier raíz, porque
ese archivo podría ser justamente el que declara el código que estás pidiendo.

**Nunca se repara automáticamente**, y la diferencia con el caso de la spec *Qué
escribe la creación de un proyecto* es de origen: una carpeta sin project file
**nunca fue** un proyecto, y un project file roto **fue** un proyecto y algo lo
dañó. Silenciarlo escondería daño real y de paso burlaría la unicidad. El
gatekeeper reporta, no adivina.

Es la misma frontera que separa *fail fast* de *no falles por vacío*, trazada
sobre otra pregunta: leer tolera vista parcial, escribir exige certeza.

**Paquete importable y superficie CLI**
El código nuevo vive en un paquete `wpipeline/` en la raíz del repo. Dos razones:
una CLI de subcomandos con validación centralizada no cabe en un script suelto sin
convertirse en un archivo que hace de todo, y las funciones del paquete necesitan
contrato de excepciones y no `die()`, según la spec *Contrato de errores del
paquete*. Las herramientas que corran dentro de Houdini importan, no ejecutan.

**Corrección.** La versión anterior de esta spec daba otra razón: que
`launch_houdini.py` "no se puede importar sin ejecutarse porque termina en
`os.execve`". Es falsa, y el MAPA de s007 lo verificó importando el módulo: el
`os.execve` vive dentro de `main()` y el archivo tiene guarda `__main__`, así que
el import es limpio y no lanza Houdini. La decisión de tener paquete se sostiene
por las dos razones de arriba; el argumento viejo no se puede usar ni acá ni en
una entrevista.

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

**`--root <nombre_lógico>` en `create-project`.** Opcional cuando hay exactamente
una raíz declarada —no hay ambigüedad posible, y obligar a nombrar la única raíz
que existe es ceremonia— y **obligatorio con dos o más**, con error claro que
liste los nombres disponibles si falta. Lo que se prohíbe es la ambigüedad, no la
comodidad: un default silencioso "la primera de la lista" es justo el supuesto
escondido que la spec *Múltiples raíces como prueba de aceptación* existe para
descubrir.

**`houdini_version` al crear.** Detección automática si hay Houdini instalado. Si
no lo hay, el campo se escribe como `null` y la salida avisa que el proyecto quedó
sin versión clavada; a partir de ahí aplica el fallback ya sellado en *Version
pinning de Houdini por proyecto*. Razón: atar la creación de un proyecto a tener el
DCC instalado rompería *Automatización headless*, porque un scheduler puede
perfectamente crear proyectos en una máquina que no tiene Houdini.

**Contrato de errores del paquete**
El paquete `wpipeline/` **lanza excepciones**. Jamás llama `sys.exit()` ni imprime
a stderr. La capa CLI atrapa, imprime el mensaje legible y decide el código de
salida.

Razón: una biblioteca que corre dentro de Houdini no puede matar la sesión del
artista con un `SystemExit`. `die()` es correcto en `launch_houdini.py` —un script
de terminal, donde salir *es* el comportamiento deseado— e incorrecto en un paquete
importable. No es que una versión esté mejor escrita que la otra: son dos contratos
distintos para dos lugares distintos.

Consecuencia inmediata: la lógica de detección de versión de Houdini se
reimplementa en `wpipeline/` con `raise`. `parse_version` se copia idéntica, por
ser pura y estar ya probada contra la lista sintética de la etapa 0;
`find_newest_houdini` se reescribe con excepciones, porque su única diferencia real
es cómo falla.

**Deuda anotada:** quedan dos copias de esa lógica hasta que la etapa 1b migre
`launch_houdini.py`. Ese día se borran las del script viejo y las del paquete
quedan como únicas.

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
Un archivo local JSON —el formato quedó sellado en *Configuración de la herramienta
en dos capas*— detrás de una capa de abstracción, para poder enchufar Flow o Kitsu
en fase 2 sin reescribir el pipeline que la consume.

**La capa nace en la etapa 1a**, con tres operaciones exactas y ni una más:

```
list_projects()       -> el escaneo de las raíces
get_project(code)     -> un proyecto por su código
create_project(...)   -> el gatekeeper escribiendo
```

`get_project` existe en la interfaz aunque la implementación por filesystem lo
derive de `list_projects`: contra Flow o Kitsu es una consulta indexada y contra un
escaneo es un barrido, y el punto de la interfaz es dejar que el backend elija.
Ponerlo después significaría cambiar la interfaz cuando llegue el backend que lo
necesita, que es exactamente lo que la capa existe para evitar.

`ProjectRecord` carga los seis campos sellados en *Campos de project.json* más dos
derivados que **no se persisten**: el nombre lógico de la raíz donde el escaneo lo
encontró, y el `path`, calculado como raíz de la configuración + `code`. Que el
`path` nunca se escriba es la garantía **mecánica** —no la promesa— de que no puede
quedar obsoleto: lo que no está guardado no se desactualiza.

Nada de secuencias, shots ni assets: eso es la etapa 1b, y `schema_version` existe
para que ese crecimiento sea declarado y no silencioso.

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

**La segunda raíz es `~/wPipeline_Projects_internal`, con nombre lógico
`internal`.** Fuera de `~/dev/wPipeline`, porque un `git clean` jamás puede
alcanzar datos de producción —es el argumento entero de la entrada de INTERVIEW.md
*Code and production data are separated*—, y fuera de `~/Documents`, porque iCloud
puede sincronizarla y repetiría el conflicto Dropbox/git en otra nube.

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
