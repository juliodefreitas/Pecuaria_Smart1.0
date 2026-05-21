"""
Pecuária Smart — Etapa 2 (auxiliar)
Gera uma imagem de teste simulando um brinco com número legível.
Use esta imagem para testar o OCR antes de usar fotos reais da webcam.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# Permite importar backend.config ao rodar: python backend/scripts/...
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config.settings import SAMPLES_DIR  # noqa: E402

DEFAULT_BRINCO_TEXT = "BR458921"


def generate_test_brinco_image(
    text: str = DEFAULT_BRINCO_TEXT,
    output_path: Path | None = None,
) -> Path:
    """Cria PNG com fundo claro e texto escuro (estilo brinco)."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        output_path = SAMPLES_DIR / "brinco_teste.png"

    height, width = 400, 800
    image = np.full((height, width, 3), (220, 230, 240), dtype=np.uint8)

    cv2.rectangle(image, (30, 80), (width - 30, height - 80), (40, 40, 40), 3)

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 2.2
    thickness = 4
    text_size, _ = cv2.getTextSize(text, font, scale, thickness)
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    cv2.putText(
        image,
        text,
        (text_x, text_y),
        font,
        scale,
        (20, 20, 20),
        thickness,
        cv2.LINE_AA,
    )

    noise = np.random.randint(0, 15, image.shape, dtype=np.uint8)
    image = cv2.add(image, noise)

    if not cv2.imwrite(str(output_path), image):
        raise RuntimeError(f"Falha ao salvar imagem de teste: {output_path}")

    print(f"Imagem de teste criada: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_test_brinco_image()
