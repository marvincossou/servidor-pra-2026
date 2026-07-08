"""Gera a imagem de preview (Open Graph) usada quando o link da PWA é
compartilhado em WhatsApp, redes sociais etc. Script pontual: o PNG gerado
é commitado em `pwa/assets/og-image.png` — o build só copia, nunca regenera.

Uso local: `python scripts/gerar_og_image_pwa.py`
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
LOGO = RAIZ / "assets" / "logo_sme_rio.png"
DESTINO = RAIZ / "pwa" / "assets" / "og-image.png"

AZUL_SME = (0, 74, 128, 255)
LARGURA, ALTURA = 1200, 630
FONTE_TITULO = Path(r"C:\Windows\Fonts\segoeuib.ttf")
FONTE_SUBTITULO = Path(r"C:\Windows\Fonts\segoeui.ttf")


def main() -> None:
    canvas = Image.new("RGBA", (LARGURA, ALTURA), AZUL_SME)

    logo = Image.open(LOGO).convert("RGBA")
    # Logo original é 299x79 (mesmo fundo #004A80) - amplia preservando
    # proporção, com boa reamostragem, ate ~68% da largura do card.
    escala = (LARGURA * 0.68) / logo.width
    novo_tamanho = (int(logo.width * escala), int(logo.height * escala))
    logo_grande = logo.resize(novo_tamanho, Image.LANCZOS)

    pos_logo = ((LARGURA - logo_grande.width) // 2, 140)
    canvas.paste(logo_grande, pos_logo, logo_grande)

    draw = ImageDraw.Draw(canvas)
    fonte_titulo = ImageFont.truetype(str(FONTE_TITULO), 54)
    fonte_subtitulo = ImageFont.truetype(str(FONTE_SUBTITULO), 32)

    y_titulo = pos_logo[1] + logo_grande.height + 70
    draw.text(
        (LARGURA // 2, y_titulo),
        "Como funciona meu prêmio?",
        font=fonte_titulo,
        fill=(255, 255, 255, 255),
        anchor="mm",
    )
    draw.text(
        (LARGURA // 2, y_titulo + 60),
        "Premiação por Resultados de Aprendizagem — PRA 2026",
        font=fonte_subtitulo,
        fill=(214, 230, 247, 255),  # mesmo tom do subtítulo no header do app
        anchor="mm",
    )

    canvas.convert("RGB").save(DESTINO, "PNG")
    print(f"Imagem OG gerada em {DESTINO} ({LARGURA}x{ALTURA})")


if __name__ == "__main__":
    main()
