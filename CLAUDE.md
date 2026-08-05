# CLAUDE.md — v001 — 05-08-2026

Lo construido y verificado. Nada de lo planeado: eso vive en PENDIENTES.md.

---

## Qué es wPipeline

Un pipeline core para Houdini escrito en Python. Proyecto de aprendizaje y
portafolio, no de estudio: una sola máquina, macOS sobre Apple Silicon, Houdini
Apprentice.

Carlos dirige la funcionalidad y decide. Claude implementa. Cada etapa entrega
un MAPA de solo lectura antes de tocar código, y se cierra corriendo, probando y
commiteando sola.

---

## Rutas del proyecto

| Qué | Dónde | Régimen |
|---|---|---|
| Código | `~/dev/wPipeline` | Disco interno, con git, **fuera de Dropbox** |
| Datos de producción | `/Volumes/W_AirProjects/Dropbox/APPS/wPipeline_Projects` | Dropbox, volumen externo, **sin git** |

**Por qué están separados.** git y Dropbox pelean por los mismos archivos:
Dropbox sincroniza el interior de `.git` mientras git lo está escribiendo, y un
`.git` corrupto no pierde un archivo, pierde el historial completo. Además el
código ya tiene respaldo propio en GitHub, así que no gana nada estando en
Dropbox. Los datos publicados, en cambio, son irreemplazables y no deben estar
al alcance de un `git clean`.

El argumento completo está en INTERVIEW.md, entrada *Code and production data
are separated*.

---

## Repositorio

https://github.com/carloswalraven/wPipeline — público desde el primer commit.
El historial completo es parte del portafolio.

### Configuración de git

`user.name` y `user.email` están definidos con `--local`, solo para este repo:

```
user.name  = Carlos Walraven
user.email = 291433159+carloswalraven@users.noreply.github.com
```

La configuración global de la máquina **no se tocó**. El email es el alias
noreply de GitHub, para no exponer el correo real en un historial público. En la
cuenta están activados *Keep my email addresses private* y *Block command line
pushes that expose my email*, que actúa como red de seguridad: si un commit
saliera firmado con el correo real, GitHub rechaza el push.

Decisión sellada: **no se usa `Co-Authored-By` en los commits.** La atribución
del uso de IA va una sola vez en el README, explicada por Carlos. Ver
PENDIENTES.md, spec *README del repo*.

---

## Etapa 0 — validar el supuesto base

### Qué probó

Un solo supuesto desnudo, del que cuelga todo el proyecto:

> Que Houdini Apprentice, lanzado por un script nuestro, cargue un HDA desde una
> carpeta externa y lo muestre en el tab menu.

Sin versiones, sin proyectos, sin fuente de verdad, sin abstracciones. Si ese
supuesto era falso, toda decisión de diseño construida encima habría sido
inútil.

### Cómo se verificó

**La verificación fue VISUAL, dentro de Houdini Apprentice 21.0.671 con
interfaz.** Que el script corriera en terminal sin error no prueba nada: el tab
menu solo existe en la aplicación gráfica. Carlos hizo la prueba con sus ojos.

Un HDA de juguete (`wtest_sphere.hdanc`, 3.373 bytes) se colocó a mano en
`.../_etapa0_test/publish/hda/`, fuera del repo y en el volumen externo.

### Resultado: PASÓ

- El script detectó `21.0.671` y lanzó Houdini.
- El inventario mostró `wtest_sphere.hdanc` con 3.373 bytes — o sea presente en
  disco, no un archivo *online-only* de Dropbox.
- Los nodos de fábrica seguían disponibles (`Copy to Points` presente). Esto
  confirma que el token `&` expandió correctamente y Houdini no perdió sus HDAs
  propios.
- `WTest Sphere` apareció en el tab menu de SOP.
- El nodo se colocó y generó geometría en el viewport.

Lo único que no se pudo verificar desde terminal antes de la prueba fue
justamente la expansión del `&` en `HOUDINI_OTLSCAN_PATH`: `hconfig` devuelve el
string crudo sin expandirlo. Quedó confirmado por observación dentro de Houdini.

---

## launch_houdini.py

Un solo archivo, biblioteca estándar de Python, sin dependencias. Lo que sigue
describe el código tal como está, no lo que se planea.

### Constantes del módulo

| Constante | Valor |
|---|---|
| `HOUDINI_APPS_DIR` | `/Applications/Houdini` |
| `HDA_DIR` | `/Volumes/W_AirProjects/Dropbox/APPS/wPipeline_Projects/_etapa0_test/publish/hda` |
| `HDA_EXTENSIONS` | `(".hda", ".hdalc", ".hdanc")` |
| `VERSION_RE` | `^Houdini(\d+)\.(\d+)\.(\d+)$` |

`HDA_DIR` está fija en el código a propósito. Externalizarla era parte de lo que
la etapa 0 excluía deliberadamente para no contaminar la prueba. La spec que lo
corrige es *Raíces de producción múltiples y configurables* en PENDIENTES.md.

Las tres extensiones se soportan desde el primer día aunque Apprentice solo
genere `.hdanc`.

### Funciones

**`die(message)`**
Imprime `ERROR: <mensaje>` en stderr y sale con código 1. Es el único punto de
salida por error del script, lo que garantiza que nunca se filtre un traceback
crudo de Python al usuario.

**`parse_version(name)`**
`"Houdini21.0.671"` → `(21, 0, 671)`. Devuelve `None` si el nombre no matchea el
patrón. Es una función pura, sin acceso a disco, lo que permitió probar el
ordenamiento contra una lista sintética de nombres inventados. Descarta
correctamente `Current`, `Icon`, `Houdini21.0` y `.DS_Store`.

**`find_newest_houdini()`**
Recorre `/Applications/Houdini`, parsea cada entrada, descarta lo que devuelve
`None`, ordena por **tupla numérica** y devuelve la mayor como `(versión,
carpeta)`. La comparación numérica importa: como texto, `21.0.671` le ganaría a
`21.0.1000`. Muere con mensaje claro si el directorio no existe o si no hay
ninguna versión reconocible.

**`find_apprentice(version_dir)`**
Busca `Houdini Apprentice *.app` con glob — el nombre del bundle incluye la
versión y no se hardcodea — y devuelve
`<bundle>/Contents/MacOS/happrentice`. Verifica que exista y que tenga permiso
de ejecución antes de devolverlo.

Ese binario es el Mach-O arm64 real. Se eligió por encima de dos alternativas:
`open -a` no pasa el entorno de forma confiable y reusa una instancia ya abierta
con el entorno viejo; `Resources/bin/happrentice` es un wrapper bash que manda
la app al fondo salvo que reciba `-foreground`, y agrega una capa de shell
innecesaria. El wrapper de SideFX apunta a este mismo binario.

**`volume_root(path)`**
Para una ruta bajo `/Volumes/X/...` devuelve `/Volumes/X`; `None` si no está en
un volumen montado. Existe para poder distinguir "el disco externo no está
conectado" de "la carpeta no existe", que son dos problemas con dos soluciones
distintas.

**`check_hda_dir()`**
Valida en orden: volumen montado → la ruta existe → es un directorio. Cualquiera
que falle llama a `die()`. Devuelve la lista ordenada de archivos cuya extensión
(en minúsculas) está en `HDA_EXTENSIONS`.

**Una carpeta vacía no es un error.** Devuelve una lista vacía y el script sigue.
Fail fast aplica a lo que hace imposible continuar, no a lo que simplemente
todavía no pasó. Ver INTERVIEW.md, entrada *Fail fast applies to broken, not to
empty*.

**`main()`**
Orquesta todo: detecta versión, resuelve binario, valida la carpeta, compone
`HOUDINI_OTLSCAN_PATH`, imprime, y lanza.

### HOUDINI_OTLSCAN_PATH

El valor que queda definido es:

```
/Volumes/W_AirProjects/Dropbox/APPS/wPipeline_Projects/_etapa0_test/publish/hda:&
```

Nuestra carpeta primero, `:` como separador (el de macOS), y `&` al final. El
`&` es el token que le dice a Houdini "y además insertá acá tu valor por
defecto". Sin él, la sesión arranca sin los 27 HDAs de fábrica.

El separador se confirmó leyendo el `HOUDINI_PATH` que el propio Houdini se
autogenera en esta máquina, que usa `:` entre rutas y termina en `&`.

La variable vive **solo en el entorno del proceso hijo**. No escribe en
`houdini.env`, ni en las preferencias, ni en `/Applications`. Un error acá no
puede dañar la instalación de Houdini: en el peor caso esa sesión arranca sin
HDAs de fábrica, y se corrige cerrando la ventana.

### Inventario previo al lanzamiento

Antes de lanzar imprime cada HDA encontrado con su **tamaño en bytes**, y marca
explícitamente los de 0 bytes. La carpeta de publish vive en Dropbox, donde un
archivo *online-only* aparece en el listado pero no tiene contenido local:
Houdini no lo puede leer. Verlo antes ahorra buscar un nodo que nunca iba a
cargar.

### Cómo lanza

```python
env = os.environ.copy()
env["HOUDINI_OTLSCAN_PATH"] = otlscan_path
os.execve(str(binary), [str(binary)], env)
```

`os.execve` reemplaza el proceso de Python por Houdini: cero procesos
intermedios, y el stderr de Houdini cae en la terminal, que para depurar esta
etapa es una ventaja. La contrapartida es que cerrar la terminal cierra Houdini.
Se parte de `os.environ.copy()` y no de un entorno vacío, porque Houdini necesita
`HOME`, `PATH` y compañía para arrancar.

### Cómo se corre

```
python3 ~/dev/wPipeline/launch_houdini.py
```

---

## Entorno verificado

| Componente | Estado |
|---|---|
| Houdini | `21.0.671`, **única versión instalada** en `/Applications/Houdini` |
| Bundle usado | `Houdini Apprentice 21.0.671.app` — Mach-O arm64 |
| Python | `3.12.3` en `/Library/Frameworks/Python.framework/Versions/3.12` |
| Homebrew | `6.0.15` en `/opt/homebrew` |
| GitHub CLI | `gh 2.97.0`, autenticado, protocolo HTTPS |
| `~/.zprofile` | Homebrew agregado con `eval "$(/opt/homebrew/bin/brew shellenv)"` |

Dos cosas que conviene tener presentes:

- Como hay **una sola versión de Houdini instalada**, la lógica de elegir la más
  reciente nunca se ejercita en esta máquina. Se verificó por otra vía: probando
  `parse_version` contra una lista sintética de nombres.
- `brew shellenv` pone `/opt/homebrew/bin` adelante de todo en el `PATH`. Hoy no
  hay conflicto porque Homebrew no tiene ningún `python3` instalado, pero un
  futuro `brew install python` cambiaría el intérprete por defecto en silencio.
