"""
Pecuária Smart — Etapa 1
Captura de imagem da webcam com OpenCV.

Controles na janela de preview:
  ESPAÇO  -> salva a foto atual
  Q ou ESC -> encerra o programa
"""

from datetime import datetime
from pathlib import Path

import cv2

# Raiz do projeto: .../Pecuaria_Smart
ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "backend" / "data" / "captures"


def ensure_output_dir() -> None:
    """Garante que a pasta de saída existe."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def capture_from_webcam(camera_index: int = 0) -> None:
    """
    Abre a webcam, mostra preview em tempo real e salva fotos ao pressionar ESPAÇO.

    Args:
        camera_index: índice da câmera (0 = webcam padrão do Windows).
    """
    ensure_output_dir()

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(
            f"Não foi possível abrir a câmera (índice {camera_index}). "
            "Verifique se a webcam está conectada e não está em uso por outro app."
        )

    # Ajustes opcionais de resolução (nem todas as câmeras aceitam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("=" * 50)
    print("  Pecuária Smart — Captura de Webcam")
    print("=" * 50)
    print("Controles:")
    print("  ESPAÇO  -> salvar foto")
    print("  Q ou ESC -> sair")
    print(f"Salvando em: {OUTPUT_DIR}")
    print("=" * 50)

    window_name = "Pecuaria Smart - Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    saved_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro: não foi possível ler um frame da câmera.")
                break

            # Overlay com instruções na imagem
            cv2.putText(
                frame,
                "ESPACO: salvar | Q: sair",
                (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"Fotos salvas: {saved_count}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), ord("Q"), 27):  # Q ou ESC
                print("Encerrando...")
                break

            if key == 32:  # ESPAÇO
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = OUTPUT_DIR / f"captura_{timestamp}.jpg"
                success = cv2.imwrite(str(filepath), frame)
                if success:
                    saved_count += 1
                    print(f"Foto salva: {filepath}")
                else:
                    print(f"Falha ao salvar: {filepath}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"Total de fotos salvas nesta sessão: {saved_count}")


if __name__ == "__main__":
    capture_from_webcam()
