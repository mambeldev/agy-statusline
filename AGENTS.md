# AI Installation Instructions (`agy-statusline`)

Este documento está diseñado para **agentes de IA** (como Antigravity CLI `agy`, Claude Code, Cursor, etc.). Cuando el usuario te pida instalar, configurar, verificar o desinstalar este proyecto, sigue exactamente estos pasos.

---

## Objetivo

Instalar el script `statusline.py` en `~/.gemini/antigravity-cli/statusline.py` y registrarlo en `~/.gemini/antigravity-cli/settings.json` sin perder ninguna otra configuración existente del usuario.

---

## Paso 1: Verificar requisitos previos

1. Comprueba que `python3` esté disponible y sea versión **3.10 o superior** (el script utiliza anotaciones de tipo `float | None`):
   ```bash
   python3 -c 'import sys; assert sys.version_info >= (3, 10), f"Python 3.10+ required, found {sys.version}"; print("OK:", sys.version)'
   ```
2. Confirma que el archivo `statusline.py` existe en el directorio actual del repositorio.

---

## Paso 2: Copiar el script y asignar permisos

Copia `statusline.py` a `~/.gemini/antigravity-cli/statusline.py` y hazlo ejecutable:

```bash
mkdir -p ~/.gemini/antigravity-cli/cache
cp ./statusline.py ~/.gemini/antigravity-cli/statusline.py
chmod +x ~/.gemini/antigravity-cli/statusline.py
```

> **Nota sobre Sandbox:** Si te encuentras ejecutando comandos dentro de un sandbox que bloquea la escritura en `~/.gemini/antigravity-cli/`, solicita ejecución fuera del sandbox (`BypassSandbox: true`) únicamente para el paso de copia y actualización de `settings.json`, o indícale al usuario el comando exacto si la política del sistema bloquea esa ruta.

---

## Paso 3: Configurar `~/.gemini/antigravity-cli/settings.json`

**IMPORTANTE:** Nunca sobrescribas `~/.gemini/antigravity-cli/settings.json` por completo si ya existe. Debes fusionar (*merge*) la clave `"statusLine"` conservando el resto de claves del archivo.

Ejecuta este script de Python para actualizar `settings.json` de forma segura e idempotente:

```bash
python3 -c '
import json, os

settings_path = os.path.expanduser("~/.gemini/antigravity-cli/settings.json")
os.makedirs(os.path.dirname(settings_path), exist_ok=True)

data = {}
if os.path.exists(settings_path):
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            data = json.loads(content)

data["statusLine"] = {
    "type": "command",
    "command": "~/.gemini/antigravity-cli/statusline.py",
    "enabled": True,
    "padding": 0,
    "stack_with_default": False
}

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print("settings.json updated successfully.")
'
```

### Alternativa si `~/.gemini/antigravity-cli/settings.json` está protegido por el entorno del agente

Si el entorno del agente bloquea por seguridad el acceso de lectura/escritura a `~/.gemini/antigravity-cli/settings.json`, copia o mantén `statusline.py` en una ruta accesible (o pide al usuario que ejecute el `cp`) e indícale que ejecute este comando slash directamente dentro de `agy`:

```text
/statusline ~/.gemini/antigravity-cli/statusline.py
```

---

## Paso 4: Verificar la instalación

Ejecuta una prueba enviando un JSON simulado por `stdin` al script instalado para confirmar que devuelve la barra formateada con códigos ANSI y código de salida `0`:

```bash
echo '{"terminal_width":100,"agent_state":"active","cwd":"/tmp/demo","vcs":{"branch":"main"},"model":{"display_name":"Gemini"},"quota":{"gemini-5h":{"remaining_fraction":0.8},"gemini-weekly":{"remaining_fraction":0.5,"reset_time":"2099-01-01T00:00:00Z"}}}' | ~/.gemini/antigravity-cli/statusline.py && echo ""
```

Si la salida muestra `● active demo (main)` a la izquierda y `[Day: 20.0% | Week: 50.0% | Month: ...%]  [Gemini]` a la derecha, la instalación ha sido exitosa.

---

## Instrucciones de desinstalación (si el usuario lo solicita)

Si el usuario te pide desinstalar `agy-statusline`:

1. Elimina la clave `"statusLine"` de `~/.gemini/antigravity-cli/settings.json` conservando el resto del archivo (o dile al usuario que ejecute `/statusline reset` en `agy`).
2. Elimina el script instalado y, opcionalmente, el caché mensual:
   ```bash
   rm -f ~/.gemini/antigravity-cli/statusline.py
   rm -f ~/.gemini/antigravity-cli/cache/token_tracker.json
   ```
