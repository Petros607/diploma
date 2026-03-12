# app/services/pdf_service.py
"""Сервис для работы с PDF-файлами лекций."""
from pathlib import Path
import re

import cairosvg
from fpdf import FPDF, XPos, YPos


class PdfService:
    """Сервис для работы с PDF-файлами лекций."""
    FONT_DIR = Path("app/static/resource/arial")
    FONT_FAMILY = "ArialCustom"

    def __init__(self):
        self.pdf = FPDF()
        self._register_fonts()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def _register_fonts(self):
        """Регистрируем TTF-шрифты для кириллицы"""
        self.pdf.add_font(
            self.FONT_FAMILY, "", str(self.FONT_DIR / "regular.ttf"), uni=True
        )
        self.pdf.add_font(
            self.FONT_FAMILY, "B", str(self.FONT_DIR / "bold.ttf"), uni=True
        )
        self.pdf.add_font(
            self.FONT_FAMILY, "I", str(self.FONT_DIR / "inclined.ttf"), uni=True
        )
        self.pdf.add_font(
            self.FONT_FAMILY, "BI", str(self.FONT_DIR / "bold_inclined.ttf"), uni=True
        )

    async def generate_pdf_from_summary(
        self,
        summary_path: str,
        slides_dir: str,
        output_path: str
    ) -> str:
        """Создает PDF лекции из summary.txt и svg слайдов"""

        slides = self._parse_summary(summary_path)

        # титульная страница
        self.pdf.add_page()
        self.pdf.set_font(self.FONT_FAMILY, "B", 24)
        self.pdf.multi_cell(self.pdf.epw, 12, "Конспект лекции")

        self.pdf.ln(10)
        self.pdf.set_font(self.FONT_FAMILY, "", 14)
        self.pdf.multi_cell(self.pdf.epw, 10, f"Количество слайдов: {len(slides)}")

        for slide in slides:
            self.pdf.add_page()
            await self._render_slide(slide, slides_dir)

        self.pdf.output(output_path)
        return output_path

    def _parse_summary(self, summary_path: str):
        """Парсит summary.txt"""
        text = Path(summary_path).read_text(encoding="utf-8")
        pattern = r"---Слайд\s+(\d+)\nТайминг:\s*(\d+)\s*сек\n\n(.*?)(?=\n---Слайд|\Z)"
        matches = re.findall(pattern, text, re.S)

        slides = []
        for slide_num, timing, content in matches:
            slides.append(
                {"slide": int(slide_num), "time": int(timing), "text": content.strip()}
            )
        return slides

    async def _render_slide(self, slide: dict, slides_dir: str):
        slide_number = slide["slide"]
        timing = slide["time"]
        text = slide["text"]

        effective_width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin

        # заголовок слайда
        self.pdf.set_font(self.FONT_FAMILY, "B", 16)
        self.pdf.multi_cell(effective_width, 10, f"Слайд {slide_number}")

        # тайминг
        self.pdf.set_font(self.FONT_FAMILY, "", 11)
        self.pdf.multi_cell(effective_width, 8, f"Тайминг: {timing} сек")
        self.pdf.ln(5)

        # изображение
        svg_path = Path(slides_dir) / f"slide{slide_number}.svg"
        if svg_path.exists():
            png_path = await self._svg_to_png(svg_path)

            # ширина изображения — максимум effective_width
            self.pdf.image(str(png_path), w=effective_width)
            self.pdf.ln(5)

        # текст конспекта
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                self.pdf.ln(4)
                continue

            if line.startswith("###"):
                self.pdf.set_font(self.FONT_FAMILY, "B", 13)
                self.pdf.multi_cell(effective_width, 7, line.replace("###", "").strip())
                self.pdf.set_font(self.FONT_FAMILY, "", 12)
            elif line.startswith("##"):
                self.pdf.set_font(self.FONT_FAMILY, "B", 14)
                self.pdf.multi_cell(effective_width, 8, line.replace("##", "").strip())
                self.pdf.set_font(self.FONT_FAMILY, "", 12)
            else:
                self.pdf.set_font(self.FONT_FAMILY, "", 12)
                self.pdf.multi_cell(effective_width, 7, line)

    async def _svg_to_png(self, svg_path: Path) -> Path:
        """Конвертирует SVG → PNG"""
        png_path = svg_path.with_suffix(".png")
        if not png_path.exists():
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(png_path),
                output_width=1600
            )
        return png_path
