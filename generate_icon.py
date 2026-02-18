"""
Script para gerar o ícone do GTA V Launcher.
Cria um ícone profissional com gradiente e símbolo de raio.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fundo com gradiente circular (verde escuro -> preto)
        cx, cy = size // 2, size // 2
        for r in range(size // 2, 0, -1):
            ratio = r / (size // 2)
            g = int(0 + (40 * ratio))
            color = (0, g, int(20 * ratio), 255)
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=color,
            )

        # Borda externa com brilho verde
        border_w = max(1, size // 32)
        for i in range(border_w):
            alpha = int(200 - (i * 60))
            if alpha < 0:
                alpha = 0
            draw.ellipse(
                [i, i, size - 1 - i, size - 1 - i],
                outline=(0, 210, 106, alpha),
            )

        # Hexágono interno
        margin = size * 0.2
        hex_points = []
        import math
        for angle_deg in range(0, 360, 60):
            angle = math.radians(angle_deg - 90)
            px = cx + (cx - margin) * math.cos(angle)
            py = cy + (cy - margin) * math.sin(angle)
            hex_points.append((px, py))

        draw.polygon(hex_points, fill=(10, 10, 10, 200), outline=(0, 210, 106, 180))

        # Texto "V" centralizado
        try:
            font_size = int(size * 0.45)
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("segoeui.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        text = "V"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2
        ty = (size - th) // 2 - size * 0.04

        # Glow por trás do texto
        for offset in range(3, 0, -1):
            alpha = int(80 / offset)
            draw.text(
                (tx, ty),
                text,
                fill=(0, 210, 106, alpha),
                font=font,
            )

        # Texto principal
        draw.text((tx, ty), text, fill=(0, 230, 120, 255), font=font)

        # Pequeno raio embaixo
        bolt_size = size * 0.12
        bolt_x = cx
        bolt_y = cy + size * 0.28
        bolt_points = [
            (bolt_x - bolt_size * 0.3, bolt_y - bolt_size),
            (bolt_x + bolt_size * 0.1, bolt_y - bolt_size * 0.1),
            (bolt_x + bolt_size * 0.3, bolt_y - bolt_size * 0.1),
            (bolt_x - bolt_size * 0.1, bolt_y + bolt_size),
            (bolt_x - bolt_size * 0.1, bolt_y + bolt_size * 0.1),
            (bolt_x - bolt_size * 0.3, bolt_y + bolt_size * 0.1),
        ]
        if size >= 32:
            draw.polygon(bolt_points, fill=(0, 230, 120, 230))

        images.append(img)

    # Salvar como ICO
    output_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    images[0].save(output_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])

    # Também salvar PNG para uso no app
    png_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    images[0].save(png_path, format="PNG")

    print(f"✅ Ícone criado: {output_path}")
    print(f"✅ PNG criado: {png_path}")
    return output_path


if __name__ == "__main__":
    create_icon()
