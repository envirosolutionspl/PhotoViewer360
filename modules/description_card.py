# -*- coding: utf-8 -*-
"""
Karta z informacjami o zdjęciu, rysowana na podglądzie panoramy (okno Street View).

Karta jest rysowana przez QPainter do obrazu RGBA w rozdzielczości ekranu (ostra przy skalowaniu 125-150%),
a ViewerWidget nakłada ją na widok OpenGL. Wygląd zgodny z projektem działu marketingu:
nagłówek (ikona, nazwa, "by EnviroSolutions · wersja", przycisk zwijania) i tabela "Informacje o zdjęciu".
Wszystkie wymiary, czcionki i kolory są w gui/constants.py (CARD_*).
"""

import os

from qgis.PyQt.QtCore import QRectF, QPointF, Qt
from qgis.PyQt.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QPainterPath, QPen
from qgis.PyQt.QtSvg import QSvgRenderer

from .. import plugin_dir, PLUGIN_VERSION
from ..constants import IMAGES_DIRECTORY
from ..gui.constants import (
    CARD_PLUGIN_ICON,
    CARD_TITLE,
    CARD_SUBTITLE,
    CARD_MARGIN,
    CARD_WIDTH,
    CARD_RADIUS,
    CARD_SHADOW_OFFSET,
    CARD_SHADOW_ALPHA,
    CARD_HEADER_HEIGHT,
    CARD_HEADER_PADDING,
    CARD_ICON_SIZE,
    CARD_ICON_TEXT_GAP,
    CARD_TITLE_RECT,
    CARD_SUBTITLE_RECT,
    CARD_ACCENT_HEIGHT,
    CARD_COLLAPSE_SIZE,
    CARD_COLLAPSE_PEN,
    CARD_CHEVRON_HALF_WIDTH,
    CARD_CHEVRON_HALF_HEIGHT,
    CARD_PANEL_MARGIN,
    CARD_PANEL_RADIUS,
    CARD_PANEL_TITLE_HEIGHT,
    CARD_ROW_HEIGHT,
    CARD_TEXT_PADDING,
    CARD_LABEL_COLUMN,
    CARD_LABEL_GAP,
    CARD_FONT_TITLE,
    CARD_FONT_SUBTITLE,
    CARD_FONT_SECTION,
    CARD_FONT_LABEL,
    CARD_FONT_VALUE,
    CARD_COLORS,
)

ALIGN_LEFT_CENTER = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class DescriptionCard:
    """
    Karta z informacjami o zdjęciu.

    Użycie:
        card = DescriptionCard(rows, "Informacje o zdjęciu", 'light', collapsed=False, dpr=1.25)
        image, collapse_rect = card.render()
        width, height, data = DescriptionCard.toGlBytes(image)   # dane dla glDrawPixels

    render() rysuje kartę po kolei: tło, nagłówek, przycisk zwijania i (gdy karta jest rozwinięta) tabelę.
    """

    def __init__(self, rows, title_section, theme, collapsed, dpr):
        """
        :param rows: lista par (nazwa pola, wartość)
        :param title_section: tytuł tabeli ("Informacje o zdjęciu")
        :param theme: 'light' albo 'dark'
        :param collapsed: True - widoczny tylko nagłówek
        :param dpr: skala ekranu (devicePixelRatio)
        """
        self.rows = rows
        self.title_section = title_section
        self.colors = CARD_COLORS[theme]
        self.collapsed = collapsed
        self.dpr = dpr
        # tabela jest rysowana tylko w rozwiniętej karcie z danymi
        self.show_table = not collapsed and bool(rows)
        self.card_height = CARD_HEADER_HEIGHT
        if self.show_table:
            self.card_height += CARD_PANEL_TITLE_HEIGHT + CARD_ROW_HEIGHT * len(rows) + 2 * CARD_PANEL_MARGIN

    @staticmethod
    def _font(spec):
        """Czcionka z opisu (rozmiar w pikselach, pogrubienie) z gui/constants.py"""
        pixel_size, bold = spec
        font = QFont()
        font.setPixelSize(pixel_size)
        font.setBold(bold)
        return font

    @staticmethod
    def toGlBytes(image):
        """QImage -> bajty RGBA (nie-premultiplikowane, wiersze od dołu) dla glDrawPixels.

        :returns: (szerokość, wysokość, bajty) w pikselach urządzenia
        """
        rgba = image.convertToFormat(QImage.Format.Format_RGBA8888).mirrored(False, True)
        data = rgba.constBits().asstring(rgba.sizeInBytes())
        return rgba.width(), rgba.height(), data

    def render(self):
        """
        Rysuje całą kartę.

        :returns: (QImage z kartą i przezroczystym marginesem,
                   QRectF przycisku zwijania we współrzędnych widoku)
        """
        width = CARD_WIDTH + 2 * CARD_MARGIN
        height = self.card_height + 2 * CARD_MARGIN
        image = QImage(int(round(width * self.dpr)), int(round(height * self.dpr)),
                       QImage.Format.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(self.dpr)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.translate(CARD_MARGIN, CARD_MARGIN)

        self._drawBackground(painter)
        self._drawHeader(painter)
        collapse_rect = self._drawCollapseButton(painter)
        if self.show_table:
            self._drawInfoTable(painter)
        painter.end()

        return image, collapse_rect.translated(CARD_MARGIN, CARD_MARGIN)

    def _drawBackground(self, painter):
        """Cień i zaokrąglone tło karty"""
        card = QRectF(0.5, 0.5, CARD_WIDTH - 1, self.card_height - 1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, CARD_SHADOW_ALPHA))
        painter.drawRoundedRect(card.translated(0, CARD_SHADOW_OFFSET), CARD_RADIUS, CARD_RADIUS)
        painter.setBrush(QColor(self.colors['card']))
        painter.setPen(QPen(QColor(self.colors['card_border']), 1))
        painter.drawRoundedRect(card, CARD_RADIUS, CARD_RADIUS)

    def _drawHeader(self, painter):
        """Nagłówek: ikona wtyczki, nazwa i "by EnviroSolutions · wersja"
        (oraz zielona linia pod nagłówkiem, gdy pod spodem jest tabela)"""
        icon_y = (CARD_HEADER_HEIGHT - CARD_ICON_SIZE) / 2
        QSvgRenderer(os.path.join(plugin_dir, IMAGES_DIRECTORY, CARD_PLUGIN_ICON)).render(
            painter, QRectF(CARD_HEADER_PADDING, icon_y, CARD_ICON_SIZE, CARD_ICON_SIZE))

        text_x = CARD_HEADER_PADDING + CARD_ICON_SIZE + CARD_ICON_TEXT_GAP
        text_w = CARD_WIDTH - text_x - CARD_COLLAPSE_SIZE - CARD_HEADER_PADDING - CARD_ICON_TEXT_GAP
        painter.setPen(QColor(self.colors['title']))
        painter.setFont(self._font(CARD_FONT_TITLE))
        painter.drawText(QRectF(text_x, CARD_TITLE_RECT[0], text_w, CARD_TITLE_RECT[1]), ALIGN_LEFT_CENTER, CARD_TITLE)
        painter.setPen(QColor(self.colors['subtitle']))
        painter.setFont(self._font(CARD_FONT_SUBTITLE))
        painter.drawText(QRectF(text_x, CARD_SUBTITLE_RECT[0], text_w, CARD_SUBTITLE_RECT[1]), ALIGN_LEFT_CENTER,
                         CARD_SUBTITLE % PLUGIN_VERSION)

        if self.show_table:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.colors['accent']))
            painter.drawRect(QRectF(1, CARD_HEADER_HEIGHT - CARD_ACCENT_HEIGHT, CARD_WIDTH - 2, CARD_ACCENT_HEIGHT))

    def _drawCollapseButton(self, painter):
        """Przycisk zwijania / rozwijania (okrąg ze strzałką w górę lub w dół).

        :returns: QRectF przycisku we współrzędnych karty
        """
        rect = QRectF(CARD_WIDTH - CARD_HEADER_PADDING - CARD_COLLAPSE_SIZE,
                      (CARD_HEADER_HEIGHT - CARD_COLLAPSE_SIZE) / 2, CARD_COLLAPSE_SIZE, CARD_COLLAPSE_SIZE)
        pen = QPen(QColor(self.colors['icon']), CARD_COLLAPSE_PEN)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect.adjusted(1, 1, -1, -1))

        cx, cy = rect.center().x(), rect.center().y()
        direction = 1 if self.collapsed else -1  # strzałka w dół, gdy karta zwinięta
        chevron = QPainterPath(QPointF(cx - CARD_CHEVRON_HALF_WIDTH, cy - CARD_CHEVRON_HALF_HEIGHT * direction))
        chevron.lineTo(QPointF(cx, cy + CARD_CHEVRON_HALF_HEIGHT * direction))
        chevron.lineTo(QPointF(cx + CARD_CHEVRON_HALF_WIDTH, cy - CARD_CHEVRON_HALF_HEIGHT * direction))
        painter.drawPath(chevron)
        return rect

    def _drawInfoTable(self, painter):
        """Tabela "Informacje o zdjęciu": pasek tytułu i wiersze na przemian jasne/ciemniejsze,
        przycięte do zaokrąglonej ramki"""
        panel = QRectF(CARD_PANEL_MARGIN, CARD_HEADER_HEIGHT + CARD_PANEL_MARGIN, CARD_WIDTH - 2 * CARD_PANEL_MARGIN,
                       CARD_PANEL_TITLE_HEIGHT + CARD_ROW_HEIGHT * len(self.rows))
        clip = QPainterPath()
        clip.addRoundedRect(panel, CARD_PANEL_RADIUS, CARD_PANEL_RADIUS)
        painter.save()
        painter.setClipPath(clip)
        painter.fillRect(QRectF(panel.x(), panel.y(), panel.width(), CARD_PANEL_TITLE_HEIGHT),
                         QColor(self.colors['panel_title_bg']))

        label_font, value_font = self._font(CARD_FONT_LABEL), self._font(CARD_FONT_VALUE)
        value_metrics = QFontMetricsF(value_font)
        # kolumna nazw pól dopasowana do najdłuższej nazwy (np. "Section number" po angielsku)
        label_metrics = QFontMetricsF(label_font)
        label_column = max(CARD_LABEL_COLUMN,
                           max(label_metrics.horizontalAdvance(label) for label, _value in self.rows) + CARD_LABEL_GAP)
        value_w = panel.width() - label_column - CARD_TEXT_PADDING

        for index, (label, value) in enumerate(self.rows):
            row = QRectF(panel.x(), panel.y() + CARD_PANEL_TITLE_HEIGHT + index * CARD_ROW_HEIGHT,
                         panel.width(), CARD_ROW_HEIGHT)
            painter.fillRect(row, QColor(self.colors['row_alt'] if index % 2 else self.colors['row']))
            painter.setPen(QColor(self.colors['label']))
            painter.setFont(label_font)
            painter.drawText(row.adjusted(CARD_TEXT_PADDING, 0, 0, 0), ALIGN_LEFT_CENTER, label)
            painter.setPen(QColor(self.colors['value']))
            painter.setFont(value_font)
            text = value_metrics.elidedText(str(value), Qt.TextElideMode.ElideRight, value_w)
            painter.drawText(QRectF(row.x() + label_column, row.y(), value_w, CARD_ROW_HEIGHT), ALIGN_LEFT_CENTER, text)
        painter.restore()

        painter.setPen(QColor(self.colors['panel_title']))
        painter.setFont(self._font(CARD_FONT_SECTION))
        painter.drawText(QRectF(panel.x() + CARD_TEXT_PADDING, panel.y(), panel.width() - 2 * CARD_TEXT_PADDING,
                                CARD_PANEL_TITLE_HEIGHT), ALIGN_LEFT_CENTER, self.title_section)
        painter.setPen(QPen(QColor(self.colors['panel_border']), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(panel.adjusted(0.5, 0.5, -0.5, -0.5), CARD_PANEL_RADIUS, CARD_PANEL_RADIUS)
