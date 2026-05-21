"""
Pecuária Smart — Etapa 2
Lê texto de uma imagem estática usando Tesseract OCR + OpenCV (pré-processamento).
"""

import argparse
import re
import sys
from pathlib import Path

import cv2
import pytesseract
from pytesseract import TesseractNotFoundError

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config.settings import (  # noqa: E402
    CAPTURES_DIR,
    OCR_OUTPUT_DIR,
    SAMPLES_DIR,
    TESSERACT_CMD,
    TESSERACT_WINDOWS_PATHS,
)

DEFAULT_IMAGE = SAMPLES_DIR / "brinco_teste.png"


def configure_tesseract() -> str:
    """
    Localiza o executável do Tesseract e configura o pytesseract.

    Ordem de busca:
      1. Variável de ambiente TESSERACT_CMD
      2. Caminhos padrão do Windows
      3. PATH do sistema (shutil.which via pytesseract)
    """
    if TESSERACT_CMD:
        path = Path(TESSERACT_CMD)
        if path.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(path)
            return str(path)
        raise FileNotFoundError(
            f"TESSERACT_CMD definido, mas arquivo não encontrado: {path}"
        )

    for candidate in TESSERACT_WINDOWS_PATHS:
        if candidate.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(candidate)
            return str(candidate)

    # Deixa o pytesseract usar o que estiver no PATH
    try:
        version = pytesseract.get_tesseract_version()
        return f"tesseract no PATH (versão {version})"
    except TesseractNotFoundError as exc:
        raise FileNotFoundError(
            "Tesseract não encontrado.\n"
            "Instale em: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "Durante a instalação, marque 'Additional language data' se quiser.\n"
            "Depois adicione ao PATH ou defina:\n"
            '  $env:TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"'
        ) from exc


def preprocess_for_ocr(image_bgr):
    """
    Melhora contraste para OCR: escala de cinza, blur leve, limiar adaptativo.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10,
    )
    return thresh


def extract_text(image_bgr, lang: str = "eng") -> str:
    """Executa OCR na imagem pré-processada."""
    processed = preprocess_for_ocr(image_bgr)
    config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw = pytesseract.image_to_string(processed, lang=lang, config=config)
    return raw.strip()


def normalize_brinco_code(text: str) -> str:
    """
    Limpa o texto do OCR: remove espaços e mantém apenas letras/números.
    Ex.: 'BR 458 921' -> 'BR458921'
    """
    cleaned = re.sub(r"[^A-Za-z0-9]", "", text)
    return cleaned.upper()


def save_debug_images(image_bgr, base_name: str) -> None:
    """Salva imagem original e pré-processada para você inspecionar o OCR."""
    OCR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    processed = preprocess_for_ocr(image_bgr)

    original_path = OCR_OUTPUT_DIR / f"{base_name}_original.jpg"
    processed_path = OCR_OUTPUT_DIR / f"{base_name}_processed.jpg"

    cv2.imwrite(str(original_path), image_bgr)
    cv2.imwrite(str(processed_path), processed)
    print(f"Debug salvo: {original_path}")
    print(f"Debug salvo: {processed_path}")


def resolve_image_path(path_str: str | None) -> Path:
    if path_str:
        path = Path(path_str)
        if not path.is_file():
            raise FileNotFoundError(f"Imagem não encontrada: {path}")
        return path

    if DEFAULT_IMAGE.is_file():
        return DEFAULT_IMAGE

    # Tenta a captura mais recente da Etapa 1
    if CAPTURES_DIR.is_dir():
        captures = sorted(CAPTURES_DIR.glob("captura_*.jpg"), reverse=True)
        if captures:
            print(f"Usando última captura da webcam: {captures[0]}")
            return captures[0]

    raise FileNotFoundError(
        "Nenhuma imagem para OCR.\n"
        "Execute primeiro:\n"
        "  python backend/scripts/generate_test_brinco.py\n"
        "ou informe o caminho com --imagem"
    )


def run_ocr(image_path: Path, lang: str = "eng", save_debug: bool = True) -> None:
    tesseract_info = configure_tesseract()
    print(f"Tesseract: {tesseract_info}")
    print(f"Imagem: {image_path}")

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"OpenCV não conseguiu abrir a imagem: {image_path}")

    if save_debug:
        save_debug_images(image, image_path.stem)

    raw_text = extract_text(image, lang=lang)
    brinco_code = normalize_brinco_code(raw_text)

    print("-" * 50)
    print("Resultado OCR")
    print("-" * 50)
    print(f"Texto bruto : '{raw_text}'")
    print(f"Código limpo: '{brinco_code}'")
    print("-" * 50)

    if not brinco_code:
        print("Aviso: nenhum caractere reconhecido. Tente outra foto ou ajuste a luz.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pecuária Smart — OCR de brinco em imagem estática"
    )
    parser.add_argument(
        "--imagem",
        "-i",
        help="Caminho da imagem (jpg/png). Padrão: brinco_teste.png ou última captura.",
    )
    parser.add_argument(
        "--lang",
        default="eng",
        help="Idioma do Tesseract (padrão: eng).",
    )
    parser.add_argument(
        "--sem-debug",
        action="store_true",
        help="Não salvar imagens de debug em backend/data/ocr_output/",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    img_path = resolve_image_path(args.imagem)
    run_ocr(img_path, lang=args.lang, save_debug=not args.sem_debug)
