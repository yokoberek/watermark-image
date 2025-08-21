import os
from PIL import Image, ImageDraw, ImageFont
import datetime
import shutil  # Import shutil for file copying

# --- Konfigurasi ---
INPUT_IMAGE_PATH = "input_image/1.jpg"  # Pastikan ada gambar ini di direktori yang sama
OUTPUT_DIR = "processed_images"  # Ganti nama folder output
FONT_PATH = "/usr/share/fonts/truetype/roboto/unhinted/RobotoCondensed-Bold.ttf"

# --- Informasi Watermark ---
SITE_NAME_WATERMARK = "tripkepapua"


# --- Fungsi Pengolah Gambar ---
def process_image(
    image_path,
    output_path,
    resize_width=None,
    apply_watermark=False,
    watermark_text=None,
    font_path=None,
    opacity=0.13,
):  # DEFAULT OPACITY DIGANTI KE 0.13
    try:
        img = Image.open(image_path)

        # Lakukan resize jika resize_width ditentukan dan gambar lebih besar
        if resize_width and img.width > resize_width:
            aspect_ratio = resize_width / img.width
            new_height = int(img.height * aspect_ratio)
            img = img.resize((resize_width, new_height), Image.Resampling.LANCZOS)

        # Konversi ke RGBA hanya jika watermark akan diaplikasikan
        if apply_watermark:
            img = img.convert("RGBA")

        img_width, img_height = img.size

        if apply_watermark and watermark_text:
            # Membuat layer teks watermark terpisah
            wm_font_size = int(img_width * 0.008)  # KECIL (1.2% lebar gambar)
            try:
                if font_path and os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, wm_font_size)
                else:
                    font = ImageFont.load_default()
                    print(
                        f"Warning: Font path '{font_path}' not found or not specified. Using default font."
                    )
            except Exception as e:
                print(f"Error loading font for watermark: {e}. Using default font.")
                font = ImageFont.load_default()

            # Hitung ukuran teks watermark
            try:
                left, top, right, bottom = ImageDraw.Draw(
                    Image.new("RGBA", (1, 1))
                ).textbbox((0, 0), watermark_text, font=font)
                text_width = right - left
                text_height = bottom - top
            except AttributeError:
                text_width, text_height = ImageDraw.Draw(
                    Image.new("RGBA", (1, 1))
                ).textsize(watermark_text, font=font)

            # Membuat tile watermark
            tile_width = text_width + int(img_width * 0.05)
            tile_height = text_height + int(img_width * 0.05)

            wm_tile = Image.new("RGBA", (tile_width, tile_height), (0, 0, 0, 0))
            draw_tile = ImageDraw.Draw(wm_tile)

            # Warna teks watermark
            fill_color = (255, 255, 255, int(255 * opacity))
            draw_tile.text((0, 0), watermark_text, font=font, fill=fill_color)

            # Buat gambar watermark besar dengan masonry pattern
            watermark_layer = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))

            for y in range(0, img_height + tile_height, tile_height):
                # Geser setengah tile ke kanan setiap baris genap (masonry)
                x_offset = 0 if (y // tile_height) % 2 == 0 else tile_width // 2
                for x in range(-x_offset, img_width + tile_width, tile_width):
                    watermark_layer.paste(wm_tile, (x, y))

            final_img_with_wm = Image.alpha_composite(img, watermark_layer)

            # Konversi kembali ke RGB
            final_img = final_img_with_wm.convert("RGB")

        else:
            # Jika tidak ada watermark, cukup pastikan mode RGB untuk JPEG
            final_img = img.convert("RGB")

        final_img.save(output_path, quality=85)  # Quality 85 untuk JPEG
        print(f"Successfully processed and saved: {output_path}")

    except FileNotFoundError:
        print(f"Error: Input image not found at {image_path}")
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


# --- Fungsi Utama Simulasi Upload ---
def simulate_image_upload(input_path):
    if not os.path.exists(input_path):
        print(f"Error: Input image '{input_path}' not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- 1. Menyimpan Gambar Original (Arsip) ---
    original_output_path = os.path.join(
        OUTPUT_DIR, "original_archive_" + os.path.basename(input_path)
    )
    try:
        shutil.copyfile(input_path, original_output_path)
        print(f"Original archive image saved: {original_output_path}")
    except Exception as e:
        print(f"Error saving original archive image: {e}")
        return

    # --- 2. Membuat Versi Web ---

    # Versi Web Besar (web_large) - Tidak di-resize, DENGAN watermark pattern
    web_large_path = os.path.join(
        OUTPUT_DIR, "web_large_" + os.path.basename(input_path)
    )
    process_image(
        image_path=input_path,
        output_path=web_large_path,
        resize_width=None,  # TIDAK AKAN MERESIZE, gunakan ukuran input
        apply_watermark=True,  # APLIKASIKAN watermark
        watermark_text=SITE_NAME_WATERMARK,
        font_path=FONT_PATH,
        opacity=0.10,  # OPACITY DITINGKATKAN KE 0.10 UNTUK WEB_LARGE
    )

    # Versi Web Card (web_card) - Di-resize, TANPA watermark
    CARD_VERSION_WIDTH = 800
    web_card_path = os.path.join(OUTPUT_DIR, "web_card_" + os.path.basename(input_path))
    process_image(
        image_path=input_path,
        output_path=web_card_path,
        resize_width=CARD_VERSION_WIDTH,  # Resize ke lebar tertentu
        apply_watermark=False,  # TANPA watermark
        watermark_text=None,
        font_path=None,
        opacity=0,
    )

    # Versi Web Thumbnail (web_thumbnail) - Di-resize, TANPA watermark
    THUMBNAIL_VERSION_WIDTH = 300
    web_thumbnail_path = os.path.join(
        OUTPUT_DIR, "web_thumbnail_" + os.path.basename(input_path)
    )
    process_image(
        image_path=input_path,
        output_path=web_thumbnail_path,
        resize_width=THUMBNAIL_VERSION_WIDTH,  # Resize ke lebar tertentu
        apply_watermark=False,  # TANPA watermark
        watermark_text=None,
        font_path=None,
        opacity=0,
    )

    print("\nSimulation Complete (Specific Watermark Placement)!")
    print(f"Check '{OUTPUT_DIR}' for:")
    print(
        f"- 'original_archive_{os.path.basename(input_path)}' (full quality, untouched)"
    )
    print(
        f"- 'web_large_{os.path.basename(input_path)}' (original size, WITH pattern watermark)"
    )
    print(
        f"- 'web_card_{os.path.basename(input_path)}' (resized to {CARD_VERSION_WIDTH}px, WITHOUT watermark)"
    )
    print(
        f"- 'web_thumbnail_{os.path.basename(input_path)}' (resized to {THUMBNAIL_VERSION_WIDTH}px, WITHOUT watermark)"
    )


# --- Jalankan Simulasi ---
if __name__ == "__main__":
    simulate_image_upload(INPUT_IMAGE_PATH)
