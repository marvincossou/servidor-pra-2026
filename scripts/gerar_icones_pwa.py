"""Gera os ícones da PWA a partir de um emoji, uma única vez (script pontual).

Uso local: `python scripts/gerar_icones_pwa.py`. Os PNGs gerados são
commitados em `pwa/icons/` — o build (`scripts/build_pwa.py`) só copia,
nunca regenera.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "pwa" / "icons"

AZUL_SME = (0, 74, 128, 255)
EMOJI = "\U0001f393"  # 🎓 — mesmo ícone usado no page_icon do Streamlit
FONTE_EMOJI = Path(r"C:\Windows\Fonts\seguiemj.ttf")


def _icone_quadrado(tamanho: int, proporcao_emoji: float) -> Image.Image:
    img = Image.new("RGBA", (tamanho, tamanho), AZUL_SME)
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.truetype(str(FONTE_EMOJI), int(tamanho * proporcao_emoji))
    draw.text((tamanho // 2, tamanho // 2), EMOJI, font=fonte, anchor="mm", embedded_color=True)
    return img


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)

    # Ícones "any": emoji ocupa quase todo o quadro.
    _icone_quadrado(192, 0.62).save(DESTINO / "icon-192.png")
    _icone_quadrado(512, 0.62).save(DESTINO / "icon-512.png")

    # Ícone "maskable": conteúdo precisa caber na "safe zone" central (~40%
    # de raio a partir do centro, i.e. ~80% do lado) para não ser cortado
    # por máscaras circulares/arredondadas do sistema operacional.
    _icone_quadrado(512, 0.45).save(DESTINO / "icon-maskable-512.png")

    # Apple touch icon: iOS não lê o manifest, precisa do <link> dedicado.
    _icone_quadrado(180, 0.62).save(DESTINO / "apple-touch-icon.png")

    print(f"Ícones gerados em {DESTINO}")


if __name__ == "__main__":
    main()
