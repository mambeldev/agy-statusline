# agy-statusline

Barra de estado personalizada (*custom statusline*) para **Antigravity CLI (`agy`)** que muestra en tiempo real el consumo de cuota de tokens (**Día**, **Semana** y **Mes**), el estado del agente, el directorio actual, la rama de Git y el modelo activo.

---

## Vista previa

```text
 ● active agy-statusline (main)                    [Day: 14.5% | Week: 42.0% | Month: 31.2%]  [Gemini 2.5 Pro] 
```

### Diseño adaptativo (Responsive)

El script mide automáticamente el ancho de tu terminal y adapta la vista para evitar cortes de línea:

| Ancho de terminal | Formato mostrado |
| :--- | :--- |
| **>= 95 columnas** | `● active carpeta (rama)          [Day: 14.5% | Week: 42.0% | Month: 31.2%]  [Modelo]` |
| **< 95 columnas** | `● active carpeta (rama)          [D: 14.5% | W: 42.0% | M: 31.2%]  [Modelo]` |
| **Compacto** | `● active                         [D: 14.5% | W: 42.0% | M: 31.2%]  [Modelo]` |
| **Mínimo** | `● active                         [14.5%|42.0%|31.2%] [Modelo]` |

### Código de colores por consumo

* 🟢 **Verde** (`< 50%`): Consumo bajo / normal.
* 🟡 **Amarillo** (`50% - 79.9%`): Consumo moderado.
* 🔴 **Rojo** (`80% - 94.9%`): Consumo alto.
* 🚨 **Rojo en negrita** (`>= 95%`): Cuota próxima a agotarse.

---

## Requisitos

* **Antigravity CLI (`agy`)** instalado.
* **Python 3.10+** (solo utiliza la librería estándar, sin dependencias externas).

---

## Instalación rápida con IA

Si estás usando **Antigravity (`agy`)** o cualquier otro agente de IA en tu terminal, clona este repositorio y pídele al agente:

> *"Lee el archivo `AGENTS.md` e instala este statusline para agy."*

El archivo [`AGENTS.md`](./AGENTS.md) contiene las instrucciones paso a paso para que la IA realice la copia, configure `settings.json` sin sobrescribir tus ajustes actuales y verifique que funciona.

---

## Instalación manual

### 1. Copiar el script y darle permisos de ejecución

Clona el repositorio y copia `statusline.py` al directorio de configuración de Antigravity CLI:

```bash
mkdir -p ~/.gemini/antigravity-cli
cp statusline.py ~/.gemini/antigravity-cli/statusline.py
chmod +x ~/.gemini/antigravity-cli/statusline.py
```

### 2. Activar el statusline en `agy`

Tienes dos formas de activarlo:

#### Opción A: Desde dentro de `agy` (comando slash)

Abre `agy` y ejecuta:

```text
/statusline ~/.gemini/antigravity-cli/statusline.py
```

#### Opción B: Editando `settings.json`

Abre (o crea) el archivo `~/.gemini/antigravity-cli/settings.json` y añade el bloque `statusLine`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.gemini/antigravity-cli/statusline.py",
    "enabled": true,
    "padding": 0,
    "stack_with_default": false
  }
}
```

> **Nota:** Si quieres conservar la barra de estado por defecto de `agy` y mostrar esta debajo, cambia `"stack_with_default": true`.

---

## Cómo usarlo y comandos útiles

Una vez configurado, `agy` ejecutará el script automáticamente cada vez que cambie el estado de la sesión.

Dentro de `agy` puedes controlar la barra de estado en cualquier momento con los siguientes comandos:

* `/statusline` — Alterna entre activar y desactivar la barra personalizada.
* `/statusline on` — Activa la barra personalizada.
* `/statusline off` — Desactiva temporalmente la barra personalizada y vuelve a la predeterminada.
* `/statusline reset` — Elimina la configuración personalizada y restaura la barra original de `agy`.

### Probar el script manualmente desde la terminal

Puedes verificar cómo se ve la salida simulando el payload JSON que envía `agy`:

```bash
echo '{
  "terminal_width": 110,
  "agent_state": "active",
  "cwd": "/Users/demo/agy-statusline",
  "vcs": {"branch": "main"},
  "model": {"display_name": "Gemini 2.5 Pro"},
  "quota": {
    "gemini-5h": {"remaining_fraction": 0.855},
    "gemini-weekly": {"remaining_fraction": 0.58, "reset_time": "2026-11-30T00:00:00Z"}
  }
}' | python3 ~/.gemini/antigravity-cli/statusline.py && echo ""
```

---

## ¿Cómo funciona el cálculo de consumo?

1. **Detección automática de proveedor**:
   * Si usas un modelo nativo (**Gemini**), lee las cuotas `gemini-5h` (diaria/5 horas) y `gemini-weekly` (semanal).
   * Si usas un modelo de terceros (**Claude / Sonnet / Opus / Haiku / GPT**), cambia automáticamente a las cuotas `3p-5h` y `3p-weekly`.
2. **Seguimiento mensual (`Month`)**:
   * Si el payload de `agy` no incluye cuota mensual directa, el script registra el pico máximo de consumo de cada ciclo semanal en `~/.gemini/antigravity-cli/cache/token_tracker.json` y estima el consumo acumulado del mes dividiendo entre `4.33` semanas promedio por mes.
