# app/services/pdf_service.py
from pathlib import Path
import re
import cairosvg
from fpdf import FPDF

class PdfService:
    FONT_DIR = Path("app/static/resource/arial")
    FONT_FAMILY = "ArialCustom"
    FONT_SIZE = 11
    LEFT_MARGIN = 15
    RIGHT_MARGIN = 15
    TOP_MARGIN = 15
    BOTTOM_MARGIN = 20
    LINE_HEIGHT = 5.5

    def __init__(self):
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.set_left_margin(self.LEFT_MARGIN)
        self.pdf.set_right_margin(self.RIGHT_MARGIN)
        self.pdf.set_top_margin(self.TOP_MARGIN)
        self.pdf.set_auto_page_break(auto=True, margin=self.BOTTOM_MARGIN)
        self._register_fonts()
        self.pdf.set_font(self.FONT_FAMILY, "", self.FONT_SIZE)

    def _register_fonts(self):
        self.pdf.add_font(self.FONT_FAMILY, "", str(self.FONT_DIR / "regular.ttf"))
        self.pdf.add_font(self.FONT_FAMILY, "B", str(self.FONT_DIR / "bold.ttf"))
        self.pdf.add_font(self.FONT_FAMILY, "I", str(self.FONT_DIR / "inclined.ttf"))
        self.pdf.add_font(self.FONT_FAMILY, "BI", str(self.FONT_DIR / "bold_inclined.ttf"))

    async def generate_pdf_from_summary(self, summary_path: str, slides_dir: str, output_path: str) -> str:
        slides = self._parse_summary(summary_path)

        # Титульная страница
        self.pdf.add_page()
        self.pdf.set_font(self.FONT_FAMILY, "B", 28)
        self.pdf.set_text_color(0, 0, 0)
        self._write_text("Конспект лекции")
        self.pdf.ln(15)

        self.pdf.set_font(self.FONT_FAMILY, "", 14)
        self._write_text(f"Количество слайдов: {len(slides)}")
        self.pdf.ln(10)

        # Основные слайды
        for i, slide in enumerate(slides, 1):
            self.pdf.add_page()
            await self._render_slide(slide, slides_dir, i)

        self.pdf.output(output_path)
        return output_path

    def _parse_summary(self, summary_path: str):
        text = Path(summary_path).read_text(encoding="utf-8")
        pattern = r"---Слайд\s+(\d+)\nТайминг:\s*(\d+)\s*сек\n\n(.*?)(?=\n---Слайд|\Z)"
        return [{"slide": int(n), "time": int(t), "text": c.strip()} for n, t, c in re.findall(pattern, text, re.S)]

    async def _render_slide(self, slide: dict, slides_dir: str, slide_index: int = 0):
        """Отрисовка одного слайда"""
        slide_number = slide["slide"]
        timing = slide["time"]
        text = slide["text"]

        # Заголовок слайда
        self.pdf.set_font(self.FONT_FAMILY, "B", 16)
        self.pdf.set_text_color(0, 0, 60)
        self._write_text(f"Слайд {slide_number}")
        self.pdf.ln(1)

        # Тайминг
        self.pdf.set_font(self.FONT_FAMILY, "", 10)
        self.pdf.set_text_color(100, 100, 100)
        self._write_text(f"Тайминг: {timing} сек")
        self.pdf.ln(6)

        # Вставка слайда
        svg_path = Path(slides_dir) / f"slide{slide_number}.svg"
        if svg_path.exists():
            png_path = await self._svg_to_png(svg_path)
            # Рассчитываем размер изображения с учетом доступной ширины
            page_width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
            max_height = 100  # Максимальная высота изображения в мм
            self.pdf.image(str(png_path), w=page_width, h=max_height)
            self.pdf.ln(6)

        # Текст конспекта
        self.pdf.set_text_color(0, 0, 0)
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                self.pdf.ln(3)
                continue
            if line.startswith("###"):
                self.pdf.set_font(self.FONT_FAMILY, "B", 12)
                content = line.replace("###", "").strip()
                self._write_text(content)
                self.pdf.ln(2)
                self.pdf.set_font(self.FONT_FAMILY, "", self.FONT_SIZE)
            elif line.startswith("##"):
                self.pdf.set_font(self.FONT_FAMILY, "B", 13)
                content = line.replace("##", "").strip()
                self._write_text(content)
                self.pdf.ln(2)
                self.pdf.set_font(self.FONT_FAMILY, "", self.FONT_SIZE)
            else:
                self.pdf.set_font(self.FONT_FAMILY, "", self.FONT_SIZE)
                self._write_text(line)
                self.pdf.ln(self.LINE_HEIGHT)

    def _write_text(self, text: str):
        """Безопасная запись текста с автоматическим переносом"""
        page_width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        # Используем multi_cell с правильной шириной
        self.pdf.multi_cell(0, self.LINE_HEIGHT, text, align="L")

    def _multi_cell_safe(self, text: str, height: float):
        """Безопасная обёртка для multi_cell"""
        self.pdf.multi_cell(0, height, text, align="L")

    async def _svg_to_png(self, svg_path: Path) -> Path:
        """Конвертирует SVG в PNG с сохранением качества"""
        png_path = svg_path.with_suffix(".png")
        if not png_path.exists():
            # Конвертируем SVG с высоким качеством
            cairosvg.svg2png(
                url=str(svg_path), 
                write_to=str(png_path),
                output_width=1920,
                output_height=1440
            )
        return png_path
