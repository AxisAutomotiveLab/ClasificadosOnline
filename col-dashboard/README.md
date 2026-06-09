# Dashboard Competitivo — Clasificados Online PR

Dashboard de análisis competitivo de dealers de autos en Puerto Rico.  
Se actualiza automáticamente cada día a las 8:00 AM UTC via GitHub Actions.

---

## Estructura del proyecto

```
col-dashboard/
├── docs/
│   ├── index.html      ← Dashboard (Netlify sirve esta carpeta)
│   └── data.json       ← Datos generados por el scraper
├── .github/
│   └── workflows/
│       └── update.yml  ← GitHub Actions (corre scraper diariamente)
├── scraper.py          ← Scraper con Playwright
├── netlify.toml        ← Config de Netlify
└── README.md
```

---

## Configuración paso a paso

### Paso 1 — Subir a GitHub

1. Crea un repositorio nuevo en github.com (puede ser privado)
2. En tu computadora, abre la terminal:

```bash
cd col-dashboard
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### Paso 2 — Conectar con Netlify

1. Ve a [netlify.com](https://netlify.com) → "Add new site" → "Import an existing project"
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio que creaste
4. En "Build settings":
   - **Build command**: (dejar vacío)
   - **Publish directory**: `docs`
5. Haz clic en "Deploy site"
6. Netlify te dará una URL como `https://nombre-random.netlify.app`
7. Puedes cambiar el nombre en Site Settings → Domain management

### Paso 3 — Correr el scraper por primera vez

Antes de compartir la URL con los gerentes, necesitas generar el `data.json` inicial.

**Opción A — Desde tu computadora:**
```bash
pip install playwright
playwright install chromium
python scraper.py
git add docs/data.json
git commit -m "initial data"
git push
```

**Opción B — Disparar el workflow manualmente:**
1. Ve a tu repositorio en GitHub
2. Haz clic en "Actions" → "Scrape COL Data Daily"
3. Haz clic en "Run workflow" → "Run workflow"
4. Espera ~5 minutos a que termine
5. Netlify detectará el cambio y redesployará automáticamente

### Paso 4 — Verificar que todo funciona

1. Abre la URL de Netlify
2. Verifica que aparece "Última actualización: [fecha de hoy]"
3. Si ves el mensaje de error, el workflow no ha corrido todavía

---

## Actualización automática

El workflow corre automáticamente todos los días a las 8:00 AM UTC (4:00 AM hora de PR).

Si el scraper falla un día, el dashboard mostrará los datos del día anterior con el aviso **"Datos del día anterior"**.

Si quieres cambiar la hora, edita `.github/workflows/update.yml`:
```yaml
- cron: '0 8 * * *'   # 8:00 AM UTC = 4:00 AM PR
- cron: '0 12 * * *'  # 12:00 PM UTC = 8:00 AM PR
- cron: '0 14 * * *'  # 2:00 PM UTC = 10:00 AM PR
```

---

## Riesgos y soluciones

| Situación | Qué pasa | Solución |
|---|---|---|
| COL bloquea el scraper | El workflow falla, se muestra aviso "Datos del día anterior" | GitHub Actions te envía email automático. El scraper usa User-Agent real para minimizar bloqueos. |
| COL cambia su HTML | El scraper extrae 0 vehículos | El parser usa `itemprop` de schema.org, que es más estable. Si falla, contáctame. |
| GitHub Actions falla | Datos del día anterior | Recibes email automático de GitHub |

---

## Dealers monitoreados

| ID | Dealer | Ubicación |
|---|---|---|
| 34602 | Autocentro Mas ★ | San Juan - Río Piedras |
| 1158 | CAGUAX Auto Sales | Caguas |
| 5439 | PITA Auto Sales | Carolina |
| 4161 | Villa Victoria | Caguas |
| 568 | Eurojapon | Bayamón |
| 6160 | Autogermana Pre-Owned | San Juan - Hato Rey |
| 35021 | CARPRO | San Juan - Río Piedras |
| 27205 | Stuttgart Auto | Caguas |

---

## Agregar o quitar dealers

Edita la lista `DEALERS` en `scraper.py` y haz push. El scraper recogerá los cambios en la próxima ejecución.
