# IDEAS.md

Bandeja viva. Sin versión: se agrega y se saca sin sellar nada.

---

~~05-08-2026 — Probar múltiples raíces con tres proyectos en carpetas distintas,
al llegar a la etapa de creación de proyectos.~~ — SELLADA a PENDIENTES.md (spec
*Múltiples raíces como prueba de aceptación*), 05-08-2026.

~~06-08-2026 — El chequeo de licencia al arrancar debe distinguir dos fallas
distintas: hserver caído (no responde en `localhost:1715`) y licencia vencida.
Hoy Houdini no abrió y el diagnóstico correcto era el primero, no el segundo; la
spec *Chequeo de licencia al arrancar* solo contempla el segundo. hserver no es
un servicio del sistema —no lo levanta init.d ni systemd, lo dice el propio panel
de SideFX—, así que muere en cada reinicio o apagado y no vuelve solo. Pasó dos
veces en tres días. Se arregla en el Houdini License Administrator: Licenses >
License Administrator > Services > Sesinetd Start, después Hserver Start. Sin
contraseña de administrador.~~ — SELLADA a PENDIENTES.md (ampliación de la spec
*Chequeo de licencia al arrancar*), 07-08-2026.

07-08-2026 — Subcomando `wpipeline config --init` que genere el archivo de
máquina interactivamente, si el error instructivo de cero raíces resulta molesto
en la práctica. Hoy ese error ya imprime la ruta y un ejemplo copiable, así que
puede alcanzar; se decide con el uso, no antes.

07-08-2026 — Bandera `--houdini-version X.Y.Z` en `create-project` para forzar
una versión concreta sin detección, si algún día hace falta. Hoy el caso sin
Houdini instalado escribe `null` y avisa, que cubre el motivo por el que la
bandera existiría.
