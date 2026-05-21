"""
Configurações globais do Pecuária Smart (backend).
"""

import os
from pathlib import Path

# Raiz do projeto: .../Pecuaria_Smart
ROOT_DIR = Path(__file__).resolve().parents[2]

# Pastas de dados
CAPTURES_DIR = ROOT_DIR / "backend" / "data" / "captures"
SAMPLES_DIR = ROOT_DIR / "backend" / "data" / "samples"
OCR_OUTPUT_DIR = ROOT_DIR / "backend" / "data" / "ocr_output"

# Caminhos comuns do Tesseract no Windows (instalador oficial)
TESSERACT_WINDOWS_PATHS = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
]

# Permite sobrescrever via variável de ambiente (útil em Raspberry/Linux depois)
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "")
