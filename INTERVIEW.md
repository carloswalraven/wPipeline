# INTERVIEW.md — v001 — 05-08-2026

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
"The pipeline doesn't assume where storage lives. Production roots are
externalized in configuration, it supports multiple roots because in a studio
shows usually live on different volumes, and it validates availability at
startup with fail fast instead of failing halfway through a publish."

**Por qué (ES)**
El código nunca escribe una ruta completa: escribe rutas relativas a una raíz
que le dicen desde fuera. Es lo mismo que `$JOB` en Houdini. Mi disco externo me
obliga a hacerlo bien: alguien que desarrolla todo en `~/Documents` nunca
descubre sus rutas hardcodeadas hasta que otro corre su código.

---

## Fail fast applies to broken, not to empty

**The argument (EN)**
"Fail fast applies to what makes it impossible to continue — an unmounted
volume, a missing DCC — not to what simply hasn't happened yet. An empty publish
folder is a warning, not an error. Pipelines that confuse 'empty' with 'broken'
end up blocking the artists they're supposed to help."

**Por qué (ES)**
Si el script fallara por carpeta vacía, bloquearía justo el paso que necesitás
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
