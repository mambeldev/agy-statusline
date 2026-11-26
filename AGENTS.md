# AI Installation Instructions (`agy-statusline`)

Este documento está diseñado para **agentes de IA** (como Antigravity CLI `agy`, Claude Code, Cursor, etc.). Cuando el usuario te pida instalar, configurar, verificar o desinstalar este proyecto, sigue estos pasos.

---

## Objetivo

Instalar `statusline.py` y registrarlo en `~/.gemini/antigravity-cli/settings.json` sin perder ninguna otra configuración existente del usuario, usando el auto-instalador integrado en el propio script (compatible con Python 3.7+, incluido el `/usr/bin/python3` 3.9 nativo de macOS, sin dependencias externas).

---

## Instalación en 1 paso

Ejecuta el auto-instalador integrado:

```bash
python3 ./statusline.py --install
```

*(Opcional)* Si el usuario pide explícitamente usar el script desde la carpeta actual sin copiarlo a `~/.gemini/antigravity-cli/statusline.py`, usa:

```bash
python3 ./statusline.py --install-here
```

> **Nota sobre Sandbox:** El comando `--install` escribe en `~/.gemini/antigravity-cli/`. Si el sandbox bloquea la escritura en `~/.gemini/antigravity-cli/` (`PermissionError`), vuelve a ejecutar `python3 ./statusline.py --install` con `BypassSandbox: true`, o indícale al usuario que ejecute dentro de `agy`:
> ```text
> /statusline ~/.gemini/antigravity-cli/statusline.py
> ```

---

## Verificación (opcional)

El comando `--install` ya muestra una vista previa automáticamente, pero si deseas probar el renderizado en cualquier momento sin alterar el caché mensual:

```bash
python3 ./statusline.py --test
```

---

## Desinstalación (si el usuario lo solicita)

Si el usuario te pide desinstalar `agy-statusline`, ejecuta:

```bash
python3 ./statusline.py --uninstall
```
