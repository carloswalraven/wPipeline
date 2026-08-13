# PLAN_1b.md — BORRADOR — 12-08-2026
Plan de implementación de la etapa 1b, generado tras el MAPA
confirmado (PENDIENTES.md v009, spec *Decisiones del MAPA de la
1b*). NO APROBADO: pendiente de revisión en el chat de planeación.
Las propuestas marcadas como no selladas requieren decisión de
Carlos antes de construir. Este archivo es transitorio: se borra
al cierre de la etapa 1b, cuando lo construido pase a CLAUDE.md.

---

Cuatro bloques: A (gramática pura, mini-etapa autocontenida), B (chequeo de
`schema_version`), C (entidades), D (launcher, aparte y al final). Cada paso
deja la suite completa en verde y es un commit propio; el repo nunca queda
roto entre commits. Salvo donde se marca lo contrario, **ningún paso requiere
Houdini**: es lógica pura de pipeline, verificable en terminal con
`python3 -m unittest discover`.

Cada paso declara tres cosas: (a) qué archivos toca, (b) qué pruebas
automáticas lo cubren, (c) si requiere verificación con los ojos de Carlos, y
qué exactamente.

---

## BLOQUE A — Gramática pura y política

### Paso 1. Bloques de gramática por entidad en la política.

Implementa: *Decisiones del MAPA de la 1b* (punto de la política por bloques)
y *Gramática de secuencias, shots y assets*.

- a. Toca: `wpipeline/policy/pipeline.json` (bloques nuevos `sequence`,
  `shot`, `asset_name`, espejo de `project_code`); `tests/test_policy_file.py`.
- Contenido propuesto: `sequence` (`prefix: "s"`, `digits: 3`,
  `reserved: ["dev"]`), `shot` (`digits: 4`), `asset_name` (`min_length: 2`,
  `max_length: 32`, alfabeto `a-z0-9_` explícito,
  `reserved: ["work", "publish", "dev", "char", "prop", "env", "fx"]`). El
  detalle que la spec dejó al plan: los reservados **repiten literal** los
  cuatro tipos en vez de referenciar `asset_types` — la política se lee como
  datos planos y una referencia interna exigiría un resolver que no existe;
  una prueba cruza que ambas listas coincidan para que no diverjan en
  silencio.
- El `schema_version` de la política se queda en 1: viaja con el paquete,
  siempre en sincronía con el código que la lee; agregar llaves no rompe a
  ningún lector actual.
- b. Pruebas: contenido de los bloques nuevos en `test_policy_file.py`, más la
  prueba cruzada de reservados vs `asset_types`.
- c. Ojos: no. Sin Houdini.

### Paso 2. Gramática de secuencias y shots en naming.py.

Implementa: *Gramática de secuencias, shots y assets*.

- a. Toca: `wpipeline/naming.py` (`validate_sequence_name(name, grammar)`,
  `validate_shot_number(number, grammar)`,
  `shot_full_name(sequence_name, shot_number)` → `"s010_0020"` /
  `"dev_0010"`); `tests/test_naming.py`.
- `validate_sequence_name` acepta el patrón `s` + 3 dígitos **o** la reservada
  `dev` (que en secuencias es la única forma libre permitida, no una
  prohibición). Nota deliberada: la forma valida dígitos, **no** multiplicidad
  de 10 — insertar `s015` en medio es exactamente el hueco que numerar de 10
  en 10 existe para permitir; el 10 en 10 es convención de numeración, no
  regla de validación. Igual para shots.
- b. Pruebas: sintéticas positivas y negativas (`s010`, `dev`, `S010`, `s01`,
  `s0100`, `10`, `0020` suelto, shot de 3 dígitos…), como `parse_version` en
  la etapa 0.
- c. Ojos: no.

### Paso 3. Gramática de assets en naming.py.

Implementa: *Gramática de secuencias, shots y assets* y los reservados de
*Decisiones del MAPA de la 1b*.

- a. Toca: `wpipeline/naming.py` (`validate_asset_name(name, grammar)`:
  alfabeto, empieza con letra, sin `_` al inicio ni al final ni doble, largo
  2–32, reservados desde el bloque); `tests/test_naming.py`.
- b. Pruebas: `fx` rechazado por reservado, `dragon`, `debris_pack`, `_x`,
  `x_`, `a__b`, `Dragón`, nombre de 33 caracteres, `a`…
- c. Ojos: no.

### Paso 4. Departamentos y token de versión.

Implementa: *Consumo de la política que ya está escrita* (su mitad pura).

- a. Toca: `wpipeline/naming.py` (`validate_department(code, departments)`;
  `version_token(number, padding)` → `"v003"` — nombre distinto de
  `houdini.format_version` a propósito); `tests/test_naming.py`.
- `validate_department` tendrá su consumidor real en el paso 10;
  `version_token` queda listo y probado, pero **su llamada de producción llega
  con publish** (fase futura) — esto se declara honesto en la cobertura final.
- b. Pruebas: sintéticas contra listas inyectadas y paddings varios.
- c. Ojos: no.

---

## BLOQUE B — schema_version deja de ser decorativo

### Paso 5. Chequeo estricto mínimo al leer.

Implementa: *Decisiones del MAPA de la 1b* (chequeo estricto de
`schema_version`).

- a. Toca: `wpipeline/truth/record.py` (`from_file_data` compara
  `data["schema_version"]` contra `SCHEMA_VERSION`; distinto o no-entero →
  `CorruptProjectFileError` con mensaje "this file is newer than the tool");
  `wpipeline/config.py` (`load_policy` verifica su `schema_version` →
  `PolicyError` si no es el conocido); `tests/test_record.py`,
  `tests/test_config.py`.
- Efecto coherente con la regla sellada *Lectura tolera vista parcial,
  escritura exige certeza*: un `project.json` con schema desconocido cae en
  `damaged_files` — advertencia al listar, bloqueo al crear. Los marcadores
  del bloque C **nacen** con este chequeo puesto, que es la razón de que este
  paso vaya antes.
- b. Pruebas: schema 2, schema `"1"` (string), schema ausente (caso ya
  cubierto), política con schema errado.
- c. Ojos: no.

---

## BLOQUE C — secuencias, shots y assets

### Paso 6. Despacho por tabla en cli.py.

No implementa spec nueva: preparación mecánica para pasar de 2 a 8+
subcomandos sin que el `if/else` crezca.

- a. Toca: `wpipeline/cli.py` (el `if args.command ==` se vuelve un dict de
  handlers; superficie idéntica).
- b. Pruebas: las existentes de `tests/test_cli.py` cubren el refactor — cero
  pruebas nuevas es la evidencia de que no cambió la superficie.
- c. Ojos: no.

### Paso 7. Records de marcadores.

Implementa: *Decisiones del MAPA de la 1b* (registro por archivo marcador
propio por entidad). `project.json` no se toca; su schema queda en 1.

- a. Toca: `wpipeline/truth/record.py` (`SequenceRecord`, `ShotRecord`,
  `AssetRecord`, cada uno con su `SCHEMA_VERSION` propio = 1, su tupla de
  campos sellados, `from_file_data` con el chequeo del paso 5 y
  `to_file_data` armado a mano); `tests/test_record.py`.
- Campos propuestos — `sequence.json`: `schema_version`, `name`, `created`.
  `shot.json`: `schema_version`, `name`, `sequence`, `created`. `asset.json`:
  `schema_version`, `name`, `type`, `created`. `sequence` y `type` se
  declaran aunque sean derivables de la ruta, por el precedente de `root` en
  la 1a: campo declarado + chequeo declaración-vs-ubicación
  (`root_matches_location`), que se reporta y nunca se repara.
- b. Pruebas: una que cuenta llaves escritas por cada record (el mismo candado
  de `to_file_data` de la 1a), más los casos de campos faltantes y schema
  errado.
- c. Ojos: no.

### Paso 8. Lectura de sub-entidades por proyecto.

Implementa: *Decisiones del MAPA de la 1b* (marcadores + operaciones
explícitas, lado de lectura) y *Árbol de carpetas y naming*.

- a. Toca: `wpipeline/truth/base.py` (crecen `list_sequences(code)`,
  `get_sequence(code, name)`, `list_shots(code, sequence)`,
  `get_shot(code, sequence, shot)`, `list_assets(code, asset_type=None)`,
  `get_asset(code, name)` — con los tres `create_` del resto del bloque
  quedan las ~9 operaciones selladas); `wpipeline/truth/filesystem.py`
  (escaneo **por proyecto, bajo demanda**: `seq/*/sequence.json`,
  `seq/<seq>/*/shot.json`, `assets/<tipo>/*/asset.json`; carpeta sin marcador
  es invisible — la regla de la 1a repetida en cada nivel);
  `tests/test_filesystem.py`.
- El escaneo jamás recorre raíces completas hacia adentro: baja solo dentro
  del proyecto pedido. La razón Dropbox del "un nivel por raíz" se respeta
  acotando la profundidad al ámbito consultado.
- El resultado es un `ScanResult` de ámbito (mismas cuatro listas, acotadas al
  proyecto), y `has_damage` de ámbito es lo que consultará la escritura del
  paso 9 en adelante — *la certeza al escribir se exige sobre el ámbito de la
  unicidad*, según *Decisiones del MAPA de la 1b*.
- b. Pruebas: árboles sintéticos en raíces temporales — marcador dañado,
  carpeta sin marcador ignorada sin ruido, `type` declarado distinto de la
  carpeta (advierte sin bloquear), proyecto inexistente.
- c. Ojos: no.

### Paso 9. create_sequence de punta a punta.

Implementa: *Decisiones del MAPA de la 1b* (operaciones explícitas, certeza
por ámbito, marcador al final) y la secuencia reservada `dev` de *Árbol de
carpetas y naming*.

- a. Toca: `wpipeline/errors.py` (excepciones hermanas por entidad, colgando
  de `SourceOfTruthError` — reportables gratis por el catch único);
  `wpipeline/truth/base.py` y `wpipeline/truth/filesystem.py`
  (`create_sequence(code, sequence_name)`: certeza sobre el proyecto
  contenedor — raíz montada, registro legible, marcadores de `seq/` sin
  daño; otras raíces no bloquean — colisión y carpeta huérfana rechazadas,
  carpeta + `sequence.json` **al final** como marcador de compleción);
  `wpipeline/commands/create_sequence.py` (nuevo: gramática → proyecto →
  escritura); `wpipeline/cli.py` (`create-sequence DEM s010 [--json]`,
  `list-sequences DEM [--json]`); `tests/test_create_sequence.py` (nuevo),
  `tests/test_cli.py`.
- `create-sequence DEM dev` es válido: así nace la secuencia reservada.
- b. Pruebas: unitarias del comando con `truth` inyectada + CLI por subproceso
  (exit codes, `--json` con stderr vacío) — el patrón de la 1a.
- c. Ojos: no en este paso (la mirada al árbol real va en el paso 12).

### Paso 10. create_shot.

Implementa: lo mismo que el paso 9, más el consumo de `departments` de
*Consumo de la política que ya está escrita*.

- a. Toca: `wpipeline/truth/base.py` y `wpipeline/truth/filesystem.py`
  (`create_shot(code, sequence_name, shot_number)`: exige la secuencia
  **existente con marcador**; crea `s010_0020/` con `work/` y `publish/`
  vacíos + `shot.json` al final); `wpipeline/commands/create_shot.py`
  (nuevo); `wpipeline/cli.py`
  (`create-shot DEM s010 0020 [--department fx]... [--json]`,
  `list-shots DEM s010 [--json]`); pruebas nuevas y `tests/test_cli.py`.
- `--department`, repetible, valida contra la lista de la política y crea
  `work/<dept>/` — el consumo real de la llave. `work/` vacío sigue siendo
  legal: fail fast aplica a lo roto, no a lo vacío.
- **PROPUESTA NO SELLADA — requiere decisión de Carlos:** la secuencia **no**
  se crea al vuelo desde `create_shot`. Lo que se crea al vuelo son carpetas
  de vocabulario (tipos de asset, `work/publish`, departamentos); las
  entidades con registro se crean explícito, porque un marcador escrito como
  efecto secundario diluye "solo el gatekeeper escribe el registro". El error
  nombra `create-sequence`. Se confirma o se voltea al aprobar este plan.
- b. Pruebas: shot sin secuencia previa rechazado, colisión, número inválido,
  departamento fuera de lista, `--json` parseable.
- c. Ojos: no.

### Paso 11. create_asset.

Implementa: lo mismo, más el consumo de `asset_types` de *Consumo de la
política que ya está escrita*.

- a. Toca: `wpipeline/truth/base.py` y `wpipeline/truth/filesystem.py`
  (`create_asset(code, asset_type, asset_name)`: valida tipo contra
  `asset_types`, crea `assets/<tipo>/` al vuelo si falta —carpeta de
  vocabulario, sin marcador—, luego `<asset>/` con `work/`, `publish/` y
  `asset.json` al final); `wpipeline/commands/create_asset.py` (nuevo);
  `wpipeline/cli.py`
  (`create-asset DEM char dragon [--department fx]... [--json]`,
  `list-assets DEM [--type char] [--json]`); pruebas nuevas y
  `tests/test_cli.py`.
- **PROPUESTA NO SELLADA — requiere decisión de Carlos:** unicidad de asset
  **por proyecto, entre todos los tipos**, no por tipo. Razón: el nombre
  publicado (`DEM_dragon_fx_v001`) no carga el tipo, así que `char/dragon` y
  `prop/dragon` colisionarían en publish. El MAPA no lo detectó; se confirma
  al aprobar.
- b. Pruebas: tipo inválido, nombre reservado (`fx` como asset), colisión en
  el mismo tipo y en tipo distinto, carpeta de tipo creada al vuelo una sola
  vez.
- c. Ojos: no.

### Paso 12. Prueba de aceptación de entidades contra las raíces reales.

Cierra el bloque C, espejo de la aceptación de la 1a: las entidades las crea
**la herramienta**, nunca la mano.

- a. Toca: ningún archivo del repo — solo las raíces de producción, vía CLI
  (`DEM`: `s010` + `s010_0020` con departamentos, `dev` + `dev_0010`,
  `char/dragon`; `NEB` en `internal` para ejercitar el ámbito con dos raíces;
  negativas: colisión de shot, asset reservado, shot sin secuencia, y la
  filosa — crear en `NEB` con `main` desmontado **debe pasar**, que es
  exactamente lo que la certeza por ámbito cambió respecto a la 1a).
- b. Pruebas: la suite completa en verde antes y después; la aceptación es
  adicional, no sustituta.
- c. Ojos: **SÍ — Carlos, con Finder, en las dos raíces**: el árbol
  resultante contra el diagrama sellado en *Árbol de carpetas y naming*,
  marcadores presentes, `_etapa0_test` intacta. **No requiere Houdini**: es
  forma en disco.

---

## BLOQUE D — migración del launcher (aparte, al final)

Nunca mezclado con el bloque C: si algo se rompe, se sabe cuál de las dos
cosas lo rompió.

### Paso 13. find_apprentice migra al paquete.

Implementa: *Decisiones del MAPA de la 1b* (Apprentice amarrado y declarado)
y abre *Migración de launch_houdini.py y deuda de duplicación*.

- a. Toca: `wpipeline/houdini.py` (`find_apprentice(version_dir)` con
  `raise HoudiniNotFoundError`; la edición como constante nombrada
  —`APPRENTICE_BUNDLE_GLOB = "Houdini Apprentice *.app"`— con docstring de
  limitación consciente); `tests/test_houdini.py`. `launch_houdini.py` sigue
  intacto en este paso.
- b. Pruebas: bundles sintéticos — sin bundle, binario ausente, binario sin
  permiso de ejecución, binario válido.
- c. Ojos: no.

### Paso 14. El resolver de lanzamiento, sin ejecutar nada.

Implementa: *Version pinning de Houdini por proyecto* (la parte pendiente: el
primer lector de `houdini_version`) y *Decisiones del MAPA de la 1b* (el
paquete resuelve, la CLI ejecuta).

- a. Toca: `wpipeline/commands/launch.py` (nuevo:
  `resolve_launch(code, ...)` → binario + entorno, **sin** `execve`; respeta
  la versión clavada del proyecto, cae a "la más reciente instalada" **solo**
  con `null`; versión clavada no instalada → error claro que nombra la
  versión y dónde está clavada, porque el pin existe para reproducibilidad,
  no para adivinar; compone `HOUDINI_OTLSCAN_PATH` con `:` y `&`, e
  inventaría HDAs con tamaños y marca de 0 bytes para que la CLI lo imprima);
  `tests/test_launch.py` (nuevo).
- **PROPUESTA NO SELLADA — requiere decisión de Carlos:** al OTLSCAN entran
  los `publish/hda` existentes del proyecto — `assets/*/*/publish/hda` y
  `seq/*/*/publish/hda`. Se confirma al aprobar.
- b. Pruebas: carpetas sintéticas — pin respetado, `null` con fallback, pin
  no instalado, proyecto inexistente, composición del path.
- c. Ojos: no todavía.

### Paso 15. Subcomando launch y borrado de launch_houdini.py.

Implementa: *Migración de launch_houdini.py y deuda de duplicación*,
completa.

- a. Toca: `wpipeline/cli.py` (`launch DEM`: imprime inventario y hace
  `os.execve` — la única capa con permiso de terminar procesos); **borra
  `launch_houdini.py` completo**, incluida su copia de `volume_root`,
  quedando las funciones del paquete como únicas; `tests/test_cli.py`.
- b. Pruebas: por subproceso con árbol sintético y un binario falso (script
  que imprime su entorno y sale), verificando que `HOUDINI_OTLSCAN_PATH`
  llega al proceso hijo y que el reemplazo ocurre.
- c. Ojos: **SÍ — la verificación con Houdini de la etapa, la única**:
  `python3 -m wpipeline launch DEM` abre Houdini Apprentice 21.0.671, el HDA
  de prueba aparece en el tab menu, los nodos de fábrica siguen (`&`
  expandido), el nodo genera geometría. Nota honesta: como nada publica
  todavía, la verificación usa un HDA de juguete colocado a mano en un
  `publish/hda` de `DEM` — el mismo truco declarado de la etapa 0.

### Paso 16. Chequeo de licencia al arrancar.

Implementa: *Chequeo de licencia al arrancar* — va en este bloque porque esa
spec sella que se construye junto con el launcher.

- a. Toca: módulo nuevo en el paquete (resuelve y lanza excepciones;
  propuesta: `wpipeline/license.py`), `wpipeline/cli.py` (imprime antes del
  exec). Dos fallas, dos mensajes: hserver caído en `localhost:1715` →
  procedimiento manual de arranque; licencia vencida → cuenta de SideFX.
- Sub-paso previo de solo lectura: investigar en terminal el mecanismo real
  de consulta a hserver antes de escribir código — es el punto menos conocido
  del plan.
- b. Pruebas: "hserver caído" se simula con un puerto cerrado; "licencia
  vencida" **no se puede simular** con la licencia vigente — el parser se
  prueba contra salidas sintéticas y esa cobertura parcial queda declarada.
- c. Ojos: **SÍ, parcial**: tras un reinicio (hserver muerto), correr
  `launch` y ver el mensaje con el procedimiento — el caso que pasó tres
  veces en cuatro días.

---

## COBERTURA DE SPECS DE PENDIENTES v009

**Completas al cerrar la 1b:**

- *Decisiones del MAPA de la 1b* — los siete puntos, repartidos en los pasos
  1, 5, 7–11, 13–15.
- *Gramática de secuencias, shots y assets* — pasos 1–3.
- *Migración de launch_houdini.py y deuda de duplicación* — pasos 13–15,
  `volume_root` incluida.
- *Version pinning de Houdini por proyecto* — el paso 14 entrega el lector
  que faltaba.
- *Chequeo de licencia al arrancar* — paso 16 (el caso "licencia vencida"
  queda con cobertura de prueba parcial, declarada).

**Parciales, con qué queda fuera y por qué:**

- *Árbol de carpetas y naming* — la 1b construye entidades, `work/publish` y
  departamentos; el **naming de publish** (`DEM_dragon_fx_v001.hdanc`) no se
  construye porque nada publica todavía: es de la etapa de publish. Los
  archivos de work (`dragon_fx_v003.hipnc`) los nombra quien guarda desde
  Houdini — también futuro.
- *Consumo de la política que ya está escrita* — `asset_types` y
  `departments` quedan consumidas en serio (pasos 10–11); `version_padding`
  queda con su función pura lista y probada (paso 4) pero **sin llamada de
  producción** hasta publish. La deuda se achica y se declara, no se cierra.
- *El prefijo de proyecto aplica a todo lo publicado* — fuera completa: no
  hay publish en la 1b. Sigue sellada, esperando su etapa.

**Fuera de la 1b, sin cambio de estatus:** *Fuente de verdad abstraída* (el
segundo backend sigue siendo fase 2; la interfaz crece aquí exactamente como
esa spec anticipa), *Automatización headless* (regla permanente — cada
comando nuevo la respeta con `--json` y exit codes), *USD como fase futura*,
*Sistema de estados*, *Publish de HDAs*, *Detección de licencia para
extensión*, *Integración Houdini vía packages*, *README del repo*.

---

## LAS TRES PROPUESTAS NO SELLADAS — pendientes de decisión de Carlos

Marcadas también en su paso. Ninguna se construye sin decisión previa:

1. **Paso 10** — la secuencia **no** se crea al vuelo desde `create_shot`:
   las entidades con registro se crean explícito; al vuelo solo las carpetas
   de vocabulario.
2. **Paso 11** — unicidad de asset **por proyecto entre todos los tipos**,
   porque el nombre publicado no carga el tipo.
3. **Paso 14** — el contenido del `HOUDINI_OTLSCAN_PATH` son los
   `publish/hda` existentes del proyecto (`assets/*/*/publish/hda` y
   `seq/*/*/publish/hda`).

La actualización de documentos (CLAUDE.md, PENDIENTES, GLOSARIO, INTERVIEW)
no es paso del plan: va al cierre de etapa, después de las pruebas, como
siempre.
