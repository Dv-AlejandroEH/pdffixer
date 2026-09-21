# 📄 PDF Fixer

**Editor visual de PDF para corregir, recortar, rotar y reorganizar páginas mediante una interfaz gráfica sencilla.**

PDF Fixer es una aplicación de escritorio desarrollada en Python que permite realizar modificaciones visuales sobre documentos PDF sin necesidad de utilizar herramientas complejas de edición.

La aplicación proporciona una vista previa de cada página y permite definir de forma interactiva operaciones como recortes, rotaciones, reflejos y movimientos de fragmentos entre páginas.

---

## ✨ Características

* 📂 Carga de documentos PDF.
* 👁️ Vista previa visual de las páginas.
* 🔢 Navegación entre páginas.
* 🔎 Salto directo a una página concreta.
* 🔄 Rotación de páginas en pasos de 90°.
* 🪞 Reflejo horizontal de páginas.
* ✂️ Recorte visual mediante selección con el ratón.
* ⬆️ Movimiento de la parte superior de una página hacia la página anterior.
* ⬇️ Movimiento de la parte inferior de una página hacia la página siguiente.
* 🎚️ Ajuste preciso de la posición de corte.
* 🗑️ Eliminación de páginas.
* 💾 Exportación del documento modificado a un nuevo PDF.
* ⚡ Vista previa optimizada mediante caché de imágenes.

La configuración de cada página se mantiene de forma independiente, incluyendo la operación seleccionada, posición del corte, reflejo, rotación y área de recorte.

---

## 🖥️ Vista general

La interfaz está diseñada alrededor de una vista previa central y un panel lateral de herramientas.

```text
┌──────────────────────────────────────────────────────────────┐
│  📁 Cargar PDF                     💾 Exportar PDF Arreglado │
├──────────────────────────────────────────────┬───────────────┤
│                                              │  Navegación   │
│                                              │               │
│                                              │  ◄  Página ►  │
│                                              │               │
│               VISTA PREVIA                   │  Gestión      │
│                  DEL PDF                     │  de página    │
│                                              │               │
│                                              │  🪞 Espejo    │
│                                              │               │
│                                              │  Acción       │
│                                              │  de corte     │
│                                              │               │
│                                              │  Ajuste       │
│                                              │  de línea     │
└──────────────────────────────────────────────┴───────────────┘
```

La aplicación utiliza `Tkinter` para construir la interfaz y un `Canvas` para mostrar la página y las herramientas de selección directamente sobre ella.

---

## 🛠️ Operaciones disponibles

### Página completa

Mantiene la página sin aplicar ninguna operación de corte.

```text
NONE
```

### ✂️ Recortar área

Permite dibujar un rectángulo sobre la página para seleccionar exactamente la zona que se conservará.

```text
CROP
```

La selección se realiza directamente con el ratón sobre la vista previa.

### ⬆️ Mover parte superior

Permite separar la parte superior de una página y añadirla a la página anterior.

```text
MOVE_TOP_UP
```

### ⬇️ Mover parte inferior

Permite separar la parte inferior de una página y trasladarla a la siguiente.

```text
MOVE_BOTTOM_DOWN
```

Ambas operaciones utilizan una posición de corte configurable entre el 5 % y el 95 % de la altura de la página.

---

## 🔄 Rotación y espejo

Cada página puede rotarse en incrementos de 90°:

```text
0° → 90° → 180° → 270° → 0°
```

La aplicación también permite aplicar un **reflejo horizontal** mediante la opción:

> 🪞 Efecto Espejo (Reflejar)

## Estas transformaciones se aplican tanto a la vista previa como durante la exportación.

## 📋 Requisitos

* **Python 3.x**
* **Tkinter**
* **PyMuPDF**
* **Pillow**

### Dependencias Python

```text
pymupdf
Pillow
```

Las librerías estándar `tkinter`, `io` y `warnings` también forman parte del proyecto.

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

### 2. Crear un entorno virtual

Se recomienda utilizar un entorno virtual:

```bash
python -m venv .venv
```

Activación en **Windows**:

```powershell
.venv\Scripts\activate
```

En **Linux/macOS**:

```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install pymupdf pillow
```

### 4. Ejecutar la aplicación

```bash
python pdffixer.py
```

---

## 🧑‍💻 Uso

### 1. Cargar un PDF

Pulsa:

> 📁 **Cargar PDF**

y selecciona el documento que quieres editar.

La aplicación carga el documento y prepara la configuración individual de cada página.

### 2. Seleccionar una página

Puedes utilizar:

* **◄ Ant** para retroceder.
* **Sig ►** para avanzar.
* El campo numérico para ir directamente a una página.

### 3. Aplicar modificaciones

Selecciona una de las operaciones disponibles:

* Página completa.
* Recortar área.
* Mover trozo superior.
* Mover trozo inferior.

### 4. Ajustar el resultado visualmente

Para los movimientos entre páginas puedes modificar la posición de la línea de corte:

* Arrastrando la línea directamente sobre la página.
* Utilizando el control deslizante.

Para un recorte, simplemente dibuja el área deseada con el ratón.

### 5. Exportar

Pulsa:

> 💾 **Exportar PDF Arreglado**

y selecciona el nombre y ubicación del nuevo PDF.

El documento original no se sobrescribe directamente durante este proceso; se genera un nuevo documento de salida.

---

## ⚙️ Cómo funciona internamente

El flujo de procesamiento puede resumirse así:

```text
PDF original
     │
     ▼
┌───────────────┐
│ Cargar PDF    │
└───────┬───────┘
        │
        ▼
┌───────────────────┐
│ Renderizar página │
└─────────┬─────────┘
          │
          ▼
┌─────────────────────┐
│ Aplicar configuración│
│ de la página         │
└──────────┬──────────┘
           │
           ├── Rotación
           ├── Espejo
           ├── Recorte
           └── Movimiento
                    │
                    ▼
             ┌────────────┐
             │ Imagen/PDF │
             └─────┬──────┘
                   │
                   ▼
             PDF de salida
```

Durante la exportación, las páginas se renderizan a **150 DPI**, se transforman mediante Pillow y posteriormente se incorporan al documento PDF generado con PyMuPDF.

---

## 📁 Estructura del proyecto

Actualmente el proyecto está compuesto por un único archivo principal:

```text
pdf-fixer/
│
├── pdffixer.py
└── README.md
```

### `pdffixer.py`

Contiene:

* Interfaz gráfica.
* Gestión del documento PDF.
* Navegación entre páginas.
* Estado de edición de cada página.
* Vista previa.
* Herramientas de selección.
* Operaciones de transformación.
* Exportación del PDF final.

La aplicación se inicia mediante:

```python
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFFixerApp(root)
    root.mainloop()
```

---

## 🧱 Arquitectura

La aplicación está organizada alrededor de la clase principal:

```python
PDFFixerApp
```

Esta clase gestiona tanto la interfaz como el estado del documento.

Entre sus responsabilidades se encuentran:

| Componente                    | Responsabilidad                       |
| ----------------------------- | ------------------------------------- |
| `load_pdf()`                  | Carga el documento                    |
| `load_page_into_ui()`         | Carga la página actual en la interfaz |
| `rebuild_thumbnail()`         | Genera la vista previa                |
| `rotate_page()`               | Rota la página                        |
| `delete_current_page()`       | Elimina la página actual              |
| `goto_page()`                 | Navega a una página concreta          |
| `prev_page()` / `next_page()` | Navegación                            |
| `on_mouse_down()`             | Inicio de selección                   |
| `on_mouse_drag()`             | Actualización de selección            |
| `on_mouse_up()`               | Finalización del recorte              |
| `export_pdf()`                | Generación del PDF final              |

---

## 🛡️ Gestión de imágenes

El programa desactiva los mensajes internos de error de MuPDF para evitar que determinados errores de visualización interfieran con la interfaz.

También configura Pillow para permitir el procesamiento de imágenes de gran tamaño y desactiva la advertencia correspondiente:

```python
fitz.TOOLS.mupdf_display_errors(False)
Image.MAX_IMAGE_PIXELS = None
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
```

> **Nota:** estas configuraciones permiten trabajar con imágenes grandes, pero también hacen recomendable utilizar archivos de origen confiables.

---

## ⚠️ Limitaciones actuales

* La exportación procesa las páginas como imágenes antes de generar el PDF.
* El proyecto actualmente no incluye una función de deshacer/rehacer.
* No existe actualmente una interfaz específica para gestionar varios documentos simultáneamente.
* La aplicación no incluye todavía un sistema integrado de empaquetado o instalador.
* La licencia del proyecto todavía debe definirse.

Estas limitaciones se basan en la implementación actual del proyecto.

---

## 🗺️ Roadmap

Ideas para futuras versiones:

* [ ] Sistema **Undo / Redo**.
* [ ] Miniaturas de todas las páginas.
* [ ] Reordenación de páginas mediante **drag & drop**.
* [ ] Zoom manual de la vista previa.
* [ ] Atajos de teclado.
* [ ] Soporte para más operaciones de transformación.
* [ ] Indicador de progreso durante la exportación.
* [ ] Mensajes de error más detallados.
* [ ] Generación de ejecutable para Windows.
* [ ] Empaquetado para Linux/macOS.
* [ ] Tests automatizados.
* [ ] Archivo de configuración del proyecto (`pyproject.toml`).

---

## 🤝 Contribuir

Las contribuciones son bienvenidas.

1. Haz un fork del proyecto.
2. Crea una rama para tu cambio:

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realiza tus cambios.
4. Haz commit:

```bash
git commit -m "Añadir nueva funcionalidad"
```

5. Sube la rama:

```bash
git push origin feature/nueva-funcionalidad
```

6. Abre un Pull Request.

Para cambios importantes, se recomienda explicar previamente el objetivo y el comportamiento esperado.

---

## 🐛 Reportar problemas

Si encuentras un error, abre un **Issue** indicando:

* Sistema operativo.
* Versión de Python.
* Versión de PyMuPDF.
* Versión de Pillow.
* Pasos para reproducir el problema.
* Mensaje de error, si existe.
* Descripción del resultado esperado y del resultado obtenido.

Cuando sea posible, incluye un documento PDF de prueba que pueda distribuirse legalmente.

---

## 📜 Licencia

Actualmente **no se ha especificado una licencia para el proyecto**.

Antes de distribuirlo públicamente, añade un archivo `LICENSE` con la licencia elegida.

---

## ⭐ Agradecimientos

Proyecto desarrollado en **Python** utilizando:

* [Tkinter](https://docs.python.org/3/library/tkinter.html)
* [PyMuPDF](https://pymupdf.readthedocs.io/)
* [Pillow](https://pillow.readthedocs.io/)

---

<p align="center">
  <b>PDF Fixer</b><br>
  Editor visual de PDF sencillo y orientado a operaciones de corrección y reorganización.
</p>
