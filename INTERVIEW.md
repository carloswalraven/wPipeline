# INTERVIEW.md — v005 — 07-08-2026

Argumentos de defensa. Cada entrada: el título de la decisión, el argumento en
inglés listo para decir en voz alta, y la razón en español con su analogía.

---

## Validate the assumption before building

**The argument (EN)**
"Before building anything, I validated the assumption the whole project rests
on: that a launcher-defined environment can make published HDAs available in
Houdini without manual installation. I tested it with a throwaway asset and no
pipeline code — if that assumption had failed, every design decision above it
would have been worthless."

**Por qué (ES)**
La etapa 0 no construyó pipeline: probó el supuesto desnudo. La mayoría empieza
construyendo y descubre el supuesto roto en la semana tres.

---

## Production roots are externalized configuration

**The argument (EN)**
"The pipeline is designed not to assume where storage lives: production roots are
externalized into configuration, and the design carries a list of roots rather
than a single one, because in a studio shows usually live on different volumes.
Stage zero left the root hardcoded on purpose — externalizing it there would have
contaminated the one assumption I was testing. The gatekeeper is what
externalizes it, and the config file was never the proof: the proof was creating
a project in a second root and having every path still resolve, which is exactly
what the acceptance test did. Availability is validated up front too, so an
unmounted volume stops you before a publish is halfway through."

**Por qué (ES)**
El código nunca escribe una ruta completa: escribe rutas relativas a una raíz que
le dicen desde fuera. Es lo mismo que `$JOB` en Houdini. Mi disco externo me
obliga a hacerlo bien: alguien que desarrolla todo en `~/Documents` nunca descubre
sus rutas hardcodeadas hasta que otro corre su código. La deuda que este argumento
tenía —defender múltiples raíces sin una prueba que lo respaldara— la cerró la
prueba de aceptación: la herramienta creó un proyecto en una segunda raíz
declarada en configuración. Con su alcance dicho tal cual: probó la lógica de la
lista, no el caso de volumen no montado.

---

## Fail fast applies to broken, not to empty

**The argument (EN)**
"Fail fast applies to what makes it impossible to continue — an unmounted
volume, a missing DCC — not to what simply hasn't happened yet. An empty publish
folder is a warning, not an error. Pipelines that confuse 'empty' with 'broken'
end up blocking the artists they're supposed to help."

**Por qué (ES)**
Si el script fallara por carpeta vacía, bloquearía justo el paso que necesitas
para llenarla.

---

## Houdini version is a property of the project

**The argument (EN)**
"Houdini version is a property of the project, not of the workstation. The
pipeline pins each project to a specific DCC version, because sims and HDAs are
not guaranteed to reproduce across versions, and a show has to stay reproducible
for months after it wraps. Falling back to the newest installed version is the
default for projects that haven't declared one — not the rule."

**Por qué (ES)**
En los estudios se cierra la versión a mitad de producción y las excepciones se
aprueban y registran. Mismo espíritu que nunca borrar, solo deprecar.

---

## Code and production data are separated

**The argument (EN)**
"Code and production data live in different places on purpose. Code is versioned
in git and can be deleted and recloned; published data is immutable and
irreplaceable. Keeping them in the same tree is how you lose publishes to a git
clean."

**Por qué (ES)**
Además, Dropbox y git pelean por los mismos archivos y un `.git` corrupto pierde
el historial entero. GitHub ya es el respaldo del código.

---

## The gatekeeper is the only writer

**The argument (EN)**
"The project file is never edited by hand. The tool is the only writer — it
creates projects, sequences, shots and assets, and the folders on disk are a
consequence of the source of truth, not the other way around. That's the whole
reason a production tracker like Flow or Kitsu can be plugged in later: the
pipeline already asks a source of truth what exists instead of reading the
filesystem. Swapping what answers that question doesn't touch the code that
consumes it."

**Por qué (ES)**
Si las carpetas son la verdad, cualquiera con Finder puede crear un shot inválido
y el pipeline se entera cuando ya es tarde. Con la fuente de verdad al frente,
la carpeta mal hecha simplemente no existe para la herramienta. Y el día que la
verdad venga de una base de datos en vez de un archivo, se cambia quién contesta,
no quién pregunta.

---

## CLI-first

**The argument (EN)**
"Everything is built command-line first. The validation layer doesn't know
whether a name came from a terminal or from a text field in a GUI — the
interface is a shell that gets added later, on top of logic that already works.
I do it in that order for two reasons: it forces the rules to live in one place
instead of being scattered across UI callbacks, and anything you can do with a
command can be automated. A button can only ever be pressed by a person."

**Por qué (ES)**
Es el rig antes del picker. Si los controles están bien hechos, el picker es una
cáscara y se puede rehacer cuando quieras; si la lógica vive dentro del picker,
no tienes rig, tienes una interfaz con opiniones.

---

## Department codes are a closed vocabulary

**The argument (EN)**
"Department codes are three letters, defined once in configuration, and closed.
Projects pick from the list — they don't invent codes. At Laika the FX
department code was `efx`, not `fx`. That's the point: every studio seasons its
own vocabulary, and the moment you hardcode one studio's flavor into the tool,
the tool only works at that studio. So the list lives in configuration, and the
validator refuses anything that isn't in it."

**Por qué (ES)**
Un vocabulario abierto se convierte en `lighting`, `light`, `lgt` y `LGT` en el
mismo show, y a partir de ahí ninguna búsqueda encuentra todo. Cerrar la lista es
lo que hace que el nombre sea un dato y no una opinión.

---

## Asset types are read, department codes are typed

**The argument (EN)**
"Asset types stay readable — `char`, `prop`, `env`, `fx` — and department codes
get abbreviated to three letters. That's not inconsistency, it's usage. Asset
types are read in the folder tree a handful of times; department codes get typed
into thousands of filenames. You optimize the thing you read for clarity and the
thing you write for brevity."

**Por qué (ES)**
La regla no es "todo abreviado" ni "todo legible": es que cada nombre paga el
costo del lugar donde vive. Abreviar lo que se lee poco es perder claridad
gratis; alargar lo que se teclea mil veces es cobrar un impuesto mil veces.

---

## Assets publish tools, shots publish results

**The argument (EN)**
"Assets and shots publish different kinds of things, and keeping that distinction
sharp is what keeps the library reusable. An asset publishes a tool — the dragon
publishes the HDA that makes its fire. A shot publishes a result — the fire
already simulated for that specific shot, as a cache. Consumption only flows one
way: shots consume assets, never the reverse. An asset that depended on a shot
would stop being an asset."

**Por qué (ES)**
Si un shot publica una herramienta, esa herramienta nace amarrada a una cámara y
a un timing, y el siguiente shot la hereda con basura adentro. La repisa de
reusables (`assets/fx/`) es para lo que no tiene dueño; lo que está amarrado a
una entidad vive con la entidad.

---

## Dev is a reserved sequence, nothing ever renames

**The argument (EN)**
"There's a reserved sequence called `dev` where exploration happens, with all the
real machinery — work and publish, versions, departments — but no production
camera or layout. What makes it work is the rule around it: nothing ever gets
renamed. At Laika, dev work lived behind a removable `dev_` prefix, so graduating
a shot meant renaming it — and renaming breaks every path that pointed at the old
name. Here, when something matures it either gets published as an asset or gets
rebuilt clean in the real shot, and the dev shot stays as history."

**Por qué (ES)**
Renombrar se siente barato el día que lo haces y se cobra caro después: los
`.hip` que apuntaban ahí, los caches ya publicados, las notas que citan el
nombre. Es más barato duplicar trabajo una vez que romper rutas para siempre.

---

## Multi-project is an acceptance test, not an afterthought

**The argument (EN)**
"The gatekeeper's acceptance test was creating two projects, not one. A pipeline
tested against a single show hides its hardcoded assumptions, because nothing
ever contradicts them — the one project code, the one root, the one naming
prefix all look like they work. Testing multiple production roots took a third
project in a second root, because when two projects share a root, code that only
ever uses the first one looks identical to code that respects the list. And I
didn't create any of them by hand — the tool created all three. That's the test.
The HDA half of it, two shows coexisting in one Houdini session, comes with the
publish stage."

**Por qué (ES)**
Un solo proyecto no prueba nada: prueba que el código funciona para ese
proyecto. El segundo es el que descubre las rutas fijas y el naming hardcodeado;
la lista de raíces la descubre recién el tercero, en otra raíz, y por eso al
documentar la prueba las dos mitades se cuentan por separado, cada una con su
alcance. Y crearlos a mano habría sido hacerle trampa al examen.

---

## The core is format-agnostic; USD is a publish product

**The argument (EN)**
"The core stays format-agnostic. USD isn't the architecture — it's a publish
product, one more thing that can come out of a publish, alongside HDAs and
caches. When that phase arrives it opens with its own stage zero: a minimal test
of what the Apprentice license actually allows and restricts with USD in Houdini,
before anything gets designed on top of it. I'd rather find the license wall in
an afternoon than three weeks into a design that assumed it wasn't there."

**Por qué (ES)**
Es la misma disciplina de la etapa 0: validar el supuesto desnudo antes de
construir encima. Un core que se casa con un formato tiene que reescribirse
cuando llega el siguiente; uno agnóstico solo agrega un tipo de producto más.

---

## Every pipeline action is headless-invocable

**The argument (EN)**
"Every pipeline action — publish, export, and render when it gets there — has to
be invocable from a command, with no human in front of the screen. That's the
property that lets you chain dependencies between steps, and it's what makes
plugging in a job scheduler like Deadline or Tractor later a matter of wiring,
not rewriting. If the only way to run a publish is to click a button, the farm
can never run it."

**Por qué (ES)**
Automatizable y headless son la misma propiedad vista dos veces. Un botón solo lo
aprieta una persona; un comando lo aprieta cualquier cosa, incluido otro comando
que acaba de terminar.

---

## A pipeline pain I lived

**The argument (EN)**
"At Zoic, one click would chain the whole thing: I'd fire off a set of simulation
wedges and the dependencies carried it through to the render — I came back to
results. At Laika, the export between simulation and render was manual, because
the USD pipeline was still in development. So the FX artists sat there moving
data between steps by hand — doing machine work. Same discipline, same caliber of
people, completely different cost per iteration. That's what convinced me that
the automation *between* steps matters more than the format of the data moving
through them. A beautiful data format with a human in the middle is still a
human in the middle."

**Por qué (ES)**
Es la experiencia de la que sale la regla de headless. No es una preferencia
teórica: es haber perdido horas de artista haciendo de cable entre dos programas.

---

## Libraries raise, command lines translate

**The argument (EN)**
"The package never exits and never prints. It raises, and the command line layer
is the only thing that catches, prints a readable message and picks an exit code.
That's not a style preference — it's what makes the same code safe to import
inside Houdini. A library that calls `sys.exit()` takes the artist's session down
with it. My stage zero launcher does exit on error, and that's correct there,
because it's a terminal script and exiting is the whole point. Same logic, two
different contracts, because they live in two different places."

**Por qué (ES)**
Es la diferencia entre un fusible y cortar la luz de la casa. La función que
detecta un problema casi nunca es la que sabe qué tan grave es: eso lo sabe quien
la llamó. Si la de abajo decide morir, le quita esa decisión a todos los de
arriba, incluido un panel de Houdini que solo quería pintar un mensaje en rojo.

---

## Reads tolerate a partial view, writes demand certainty

**The argument (EN)**
"With multiple production roots you get a state that doesn't exist with one: you
can see some of them. Listing projects still works when a volume is missing — it
warns which root it couldn't read and labels the list as partial, because an
incomplete answer that says it's incomplete is still useful. Creating a project
refuses outright. Project codes are unique across every root, and I can't claim
uniqueness over roots I never read. The cost of being wrong isn't symmetric: a
partial list wastes a second of your time, a duplicate code is discovered when
there are already published files carrying the same prefix, and by then fixing it
means renaming immutable publishes."

**Por qué (ES)**
Es el banco: consultar el saldo con un servidor caído te puede dar un número viejo
y avisarte que está viejo, y sirve. Hacer una transferencia con ese mismo servidor
caído no se hace, porque el error no se descubre hasta que el dinero ya se movió.
Leer y escribir no merecen el mismo nivel de certeza, y tratarlos igual es o
bloquear de más o romper de más.

---

## The negative test is the one that proves it

**The argument (EN)**
"The sharpest test in the acceptance run wasn't creating the three projects — it
was one that had to fail. I asked the tool to create a project code that already
existed, but in a *different* root than the one I was targeting, and it refused
and told me which root already had it. A pipeline with per-root uniqueness would
have happily accepted that command. The successful runs prove the code path
works; that refusal is what proves the namespace is actually global and the root
is just storage."

**Por qué (ES)**
Las pruebas que pasan te dicen que el camino feliz funciona. Las que tienen que
fallar te dicen que la regla existe de verdad. Es la diferencia entre confirmar
que la puerta abre y confirmar que la cerradura cierra: nadie compra una cerradura
probando solo lo primero.

---

## One format everywhere, zero dependencies

**The argument (EN)**
"Everything is JSON: the project file, the versioned pipeline policy, and the
machine configuration. I looked at YAML because it's nicer to hand-edit, and
rejected it for two reasons. First, neither interpreter on this machine reads it
— not the system Python and not the one embedded in Houdini — so it would have
cost a dependency in two places. Second, and this is the one that settled it, the
whole design says only the tool writes these files. I'd have been paying a
dependency for a convenience the design doesn't allow anyone to use."

**Por qué (ES)**
Un formato de más es una respuesta de más que dar, y una razón de más que
sostener. Cero dependencias no es purismo: es que el proyecto entero corre en
cualquier Python 3.11 o más nuevo sin instalar nada, incluido el que viene adentro
de Houdini, que es justo donde no quieres andar instalando cosas.
