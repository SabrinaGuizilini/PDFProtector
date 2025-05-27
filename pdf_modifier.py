from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import pikepdf
import os

def create_watermark(text, position, color="#000000", page_width=595.27, page_height=841.89):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    color = color.lstrip("#")
    r, g, b = tuple(int(color[i:i+2], 16)/255 for i in (0, 2 ,4))
    can.setFillColorRGB(r, g, b)
    can.setFont("Helvetica", 10)

    margin = 40
    text_width = can.stringWidth(text, "Helvetica", 12)

    if position == "top-left":
        x = margin
        y = page_height - margin
    elif position == "top-right":
        x = page_width - text_width - margin
        y = page_height - margin
    elif position == "bottom-left":
        x = margin
        y = margin
    else:
        x = page_width - text_width - margin
        y = margin

    can.drawString(x, y, text)
    can.save()
    packet.seek(0)
    return PdfReader(packet)


def modify_pdf(
    input_pdf_path,
    chk_watermark,
    chk_password,
    chk_metadata,
    chk_permissions,
    password_pdf,
    watermark_text,
    watermark_color,
    watermark_position,
    not_insert_watermark_first_page,
    metadatas_keys,
    metadatas_values,
    block_printing,
    block_copy,
    block_editing
):
    temp_output_path = input_pdf_path.replace('.pdf', '_temp.pdf')

    # 1) Marca d’água
    if chk_watermark:
        original_pdf = PdfReader(input_pdf_path)
        output = PdfWriter()

        for i, page in enumerate(original_pdf.pages):
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            if not_insert_watermark_first_page and i == 0:
                output.add_page(page)
                continue

            watermark_pdf = create_watermark(watermark_text, watermark_position, watermark_color, width, height)
            watermark_page = watermark_pdf.pages[0]

            page.merge_page(watermark_page)
            output.add_page(page)
    else:
        # Se não tem watermark, apenas copia o PDF
        original_pdf = PdfReader(input_pdf_path)
        output = PdfWriter()
        for page in original_pdf.pages:
            output.add_page(page)

    # 2) Metadados
    if chk_metadata:
        keys = [k.strip() for k in metadatas_keys.split(';') if k.strip()]
        values = [v.strip() for v in metadatas_values.split(';') if v.strip()]
        if len(keys) != len(values):
            raise ValueError("Número de chaves e valores de metadados não coincidem.")
        metadata_dict = {f"/{k}": v for k, v in zip(keys, values)}
        output.add_metadata(metadata_dict)

    # 3) Salva temporariamente sem senha e permissões ainda
    with open(temp_output_path, "wb") as f:
        output.write(f)

    # 4) Aplica senha e permissões (independentes)
    if chk_password or chk_permissions:
        allow_perms = pikepdf.Permissions(
            print_highres = not block_printing,
            print_lowres = not block_printing,
            extract = not block_copy,
            modify_other = not block_editing,
        )

        encryption_args = {
            "encryption": pikepdf.Encryption(
                user=password_pdf if chk_password else "",
                owner=password_pdf + "_owner" if chk_password else "default_owner_pw",
                allow=allow_perms,
                R=4
            )
        }

        with pikepdf.open(temp_output_path) as pdf:
            pdf.save(input_pdf_path, **encryption_args)

        os.remove(temp_output_path)
    else:
        # Se não há senha nem permissões, substitui o original pelo temp
        os.replace(temp_output_path, input_pdf_path)

     
