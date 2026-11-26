# agy-statusline

Barra de estado personalizada (*custom statusline*) para **Antigravity CLI (`agy`)** que muestra en tiempo real el consumo de cuota de tokens (**Día**, **Semana** y **Mes**), el estado del agente, el directorio actual, la rama de Git y el modelo activo.

---

## Vista previa

```text
 ● active agy-statusline (main)                    [Day: 14.5% | Week: 42.0% | Month: 9.7%]  [Gemini 2.5 Pro] 
```

### Diseño adaptativo (Responsive)

El script mide automáticamente el ancho de tu terminal y adapta la vista para evitar cortes de línea:

| Ancho de terminal | Formato mostrado |
| :--- | :--- |
| **>= 95 columnas** | `● active carpeta (rama)          [Day: 14.5% | Week: 42.0% | Month: 9.7%]  [Modelo]` |
| **< 95 columnas** | `● active carpeta (rama)          [D: 14.5% | W: 42.0% | M: 9.7%]  [Modelo]` |
| **Compacto** | `● active                         [D: 14.5% | W: 42.0% | M: 9.7%]  [Modelo]` |
| **Mínimo** | `● active                         [14.5%|42.0%|9.7%] [Modelo]` |

### Código de colores por consumo

* 🟢 **Verde** (`< 50%`): Consumo bajo / normal.
* 🟡 **Amarillo** (`50% - 79.9%`): Consumo moderado.
* 🔴 **Rojo** (`80% - 94.9%`): Consumo alto.
* 🚨 **Rojo en negrita** (`>= 95%`): Cuota próxima a agotarse.

---

## Requisitos

* **Antigravity CLI (`agy`)** instalado.
* **Python 3.7+** (funciona de fábrica con el Python 3.9 incluido en **macOS** y cualquier distribución **Linux**, sin instalar paquetes ni dependencias externas).

---

## Instalación en 1 comando

Coloca `statusline.py` en cualquier carpeta (o clona este repositorio) y ejecuta:

```bash
python3 statusline.py --install
```

Este comando:
1. Copia el script a `~/.gemini/antigravity-cli/statusline.py` y le asigna permisos de ejecución (`chmod +x`).
2. Actualiza `~/.gemini/antigravity-cli/settings.json` conservando intactas todas tus demás configuraciones.
3. Muestra una vista previa en tu terminal para confirmar que funciona.

### Otras opciones del script

* **Instalar sin mover el archivo (usarlo desde donde lo colocaste):**
  ```bash
  python3 statusline.py --install-here
  ```
* **Probar cómo se ve la barra en tu terminal actual:**
  ```bash
  python3 statusline.py --test
  ```
* **Desinstalar y restaurar la barra original de `agy`:**
  ```bash
  python3 statusline.py --uninstall
  ```

---

## Instalación con IA

Si estás usando **Antigravity (`agy`)**, Claude Code o Cursor, pídele al agente:

> *"Instala este statusline para agy."*

El archivo [`AGENTS.md`](./AGENTS.md) guía al agente para ejecutar `python3 ./statusline.py --install` en un solo paso.

---

## Comandos útiles dentro de `agy`

Una vez instalado, `agy` ejecutará el script automáticamente en cada actualización de estado. También puedes controlarlo desde dentro de `agy` con:

* `/statusline` — Alterna entre activar y desactivar la barra personalizada.
* `/statusline on` — Activa la barra personalizada.
* `/statusline off` — Desactiva temporalmente la barra personalizada y vuelve a la predeterminada.
* `/statusline reset` — Elimina la configuración personalizada y restaura la barra original de `agy`.

---

## ¿Cómo funciona el cálculo de consumo?

1. **Detección automática de proveedor**:
   * Si usas un modelo nativo (**Gemini**), lee las cuotas `gemini-5h` (diaria/5 horas) y `gemini-weekly` (semanal).
   * Si usas un modelo de terceros (**Claude / Sonnet / Opus / Haiku / GPT**), cambia automáticamente a las cuotas `3p-5h` y `3p-weekly`.
2. **Seguimiento mensual (`Month`)**:
   * Si el payload de `agy` no incluye cuota mensual directa, el script registra el pico máximo de consumo de cada ciclo semanal en `~/.gemini/antigravity-cli/cache/token_tracker.json` y estima el consumo acumulado del mes dividiendo entre `4.33` semanas promedio por mes.
