# System Stats Widget — Diagrams

## 1. Component Architecture

How the widget's major components connect: the Tkinter UI, the background
polling thread, and the three external data sources.

```mermaid
flowchart TB
    subgraph Widget["SysWidget (Tkinter)"]
        ML[mainloop]
        LBL[Label — stats text]
        MENU[Right-click → Close]
        DRAG[Click-drag to move]
    end

    subgraph Thread["Daemon Thread (1 s interval)"]
        FETCH[fetch_stats]
    end

    subgraph Sources["Data Sources"]
        NSMI[nvidia-smi subprocess]
        PSUTIL[psutil.virtual_memory]
        OLLAMA[Ollama API\n127.0.0.1:11434/api/ps]
    end

    ML -- "after(1000)" --> FETCH
    FETCH --> NSMI
    FETCH --> PSUTIL
    FETCH --> OLLAMA
    FETCH -- "after(0, update label)" --> LBL
```

## 2. Data Flow

What each data source returns and how values are formatted before reaching
the display.

```mermaid
flowchart LR
    subgraph nvidia-smi
        RAW_GPU["utilization.gpu\ntemperature.gpu\nmemory.used\nmemory.total"]
    end

    subgraph psutil
        RAW_RAM["virtual_memory().percent"]
    end

    subgraph Ollama API
        RAW_OLL["GET /api/ps → models[0].name"]
    end

    RAW_GPU --> FMT1["3D: 05%\nTMP: 48C\nVRAM: 32%"]
    RAW_RAM --> FMT2["RAM: 61%"]
    RAW_OLL --> FMT3["Ollama: llama3 | OFF"]

    FMT1 --> DISPLAY["Label text\n3D: 05% | TMP: 48C | VRAM: 32% | RAM: 61% | Ollama: llama3"]
    FMT2 --> DISPLAY
    FMT3 --> DISPLAY
```

## 3. Launch & Lifecycle

From double-clicking the batch file to the running widget, including how the
window is closed.

```mermaid
flowchart TD
    A[User double-clicks Launch.bat] --> B["pythonw app.py\n(no console window)"]
    B --> C[SysWidget.__init__]
    C --> D[Create frameless window\noverrideredirect + topmost]
    C --> E[Build Label + context menu]
    C --> F[update_stats_loop — first poll]

    F --> G{Every 1 second}
    G --> H[Spawn daemon thread]
    H --> I[fetch_stats]
    I --> J[Update label on main thread]
    J --> G

    E --> K[User right-clicks]
    K --> L[Context menu → Close]
    L --> M[self.destroy — exit]
```

## 4. SysWidget Class Map

All methods on the `SysWidget` class grouped by responsibility.

```mermaid
classDiagram
    class SysWidget {
        +font : tuple
        +fg_color : str
        +container : Frame
        +lbl_stats : Label
        +menu : Menu
        +__init__()
        +start_move(event)
        +do_move(event)
        +show_menu(event)
        +fetch_stats()
        +update_stats_loop()
    }

    SysWidget --|> tk.Tk

    class DataSources {
        <<external>>
        nvidia-smi subprocess
        psutil.virtual_memory()
        Ollama HTTP API
    }

    SysWidget ..> DataSources : polls every 1 s
```
