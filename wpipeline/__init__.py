"""wPipeline - a core pipeline for Houdini.

Stage 1a: tool configuration and project creation.

This package is a library first and a command line tool second. It is meant to
be importable from any interpreter, including the Python embedded in Houdini,
so it raises exceptions instead of exiting. Only the CLI layer prints and picks
an exit code. See PENDIENTES.md, spec "Contrato de errores del paquete".
"""
