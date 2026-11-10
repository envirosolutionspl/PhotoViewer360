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


def _font(spec):
    """Czcionka z opisu (rozmiar w pikselach, pogrubienie) z gui/constants.py"""
    pixel_size, bold = spec
    font = QFont()
    font.setPixelSize(pixel_size)
    font.setBold(bold)
    return font


def renderDescriptionCard(rows, title_section, theme, collapsed, dpr):
    """
    Rysuje kartę z informacjami o zdjęciu.

    :param rows: lista par (nazwa pola, wartość)
    :param title_section: tytuł tabeli ("Informacje o zdjęciu")
    :param theme: 'light' albo 'dark'
    :param collapsed: True - widoczny tylko nagłówek
    :param dpr: skala ekranu (devicePixelRatio)
    :returns: (QImage z kartą i przezroczystym marginesem, QRectF przycisku zwijania we współrzędnych widoku)
    """
    c = CARD_COLORS[theme]
    card_h = CARD_HEADER_HEIGHT
    if not collapsed and rows:
        card_h += CARD_PANEL_TITLE_HEIGHT + CARD_ROW_HEIGHT * len(rows) + 2 * CARD_PANEL_MARGIN
    width = CARD_WIDTH + 2 * CARD_MARGIN
    height = card_h + 2 * CARD_MARGIN

    image = QImage(int(round(width * dpr)), int(round(height * dpr)), QImage.Format.Format_ARGB32_Premultiplied)
    image.setDevicePixelRatio(dpr)
    image.fill(Qt.GlobalColor.transparent)

    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    p.translate(CARD_MARGIN, CARD_MARGIN)

    # cień i tło karty
    card = QRectF(0.5, 0.5, CARD_WIDTH - 1, card_h - 1)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(0, 0, 0, CARD_SHADOW_ALPHA))
    p.drawRoundedRect(card.translated(0, CARD_SHADOW_OFFSET), CARD_RADIUS, CARD_RADIUS)
    p.setBrush(QColor(c['card']))
    p.setPen(QPen(QColor(c['card_border']), 1))
    p.drawRoundedRect(card, CARD_RADIUS, CARD_RADIUS)

    # nagłówek: ikona wtyczki, nazwa, "by EnviroSolutions · wersja"
    icon_y = (CARD_HEADER_HEIGHT - CARD_ICON_SIZE) / 2
    QSvgRenderer(os.path.join(plugin_dir, IMAGES_DIRECTORY, CARD_PLUGIN_ICON)).render(
        p, QRectF(CARD_HEADER_PADDING, icon_y, CARD_ICON_SIZE, CARD_ICON_SIZE))
    text_x = CARD_HEADER_PADDING + CARD_ICON_SIZE + CARD_ICON_TEXT_GAP
    text_w = CARD_WIDTH - text_x - CARD_COLLAPSE_SIZE - CARD_HEADER_PADDING - CARD_ICON_TEXT_GAP
    p.setPen(QColor(c['title']))
    p.setFont(_font(CARD_FONT_TITLE))
    p.drawText(QRectF(text_x, CARD_TITLE_RECT[0], text_w, CARD_TITLE_RECT[1]), ALIGN_LEFT_CENTER, CARD_TITLE)
    p.setPen(QColor(c['subtitle']))
    p.setFont(_font(CARD_FONT_SUBTITLE))
    p.drawText(QRectF(text_x, CARD_SUBTITLE_RECT[0], text_w, CARD_SUBTITLE_RECT[1]), ALIGN_LEFT_CENTER,
               CARD_SUBTITLE % PLUGIN_VERSION)

    # przycisk zwijania / rozwijania (okrąg ze strzałką)
    btn = QRectF(CARD_WIDTH - CARD_HEADER_PADDING - CARD_COLLAPSE_SIZE, (CARD_HEADER_HEIGHT - CARD_COLLAPSE_SIZE) / 2,
                 CARD_COLLAPSE_SIZE, CARD_COLLAPSE_SIZE)
    pen = QPen(QColor(c['icon']), CARD_COLLAPSE_PEN)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(btn.adjusted(1, 1, -1, -1))
    cx, cy = btn.center().x(), btn.center().y()
    d = 1 if collapsed else -1  # strzałka w dół, gdy karta zwinięta
    chevron = QPainterPath(QPointF(cx - CARD_CHEVRON_HALF_WIDTH, cy - CARD_CHEVRON_HALF_HEIGHT * d))
    chevron.lineTo(QPointF(cx, cy + CARD_CHEVRON_HALF_HEIGHT * d))
    chevron.lineTo(QPointF(cx + CARD_CHEVRON_HALF_WIDTH, cy - CARD_CHEVRON_HALF_HEIGHT * d))
    p.drawPath(chevron)

    if not collapsed and rows:
        # zielona linia pod nagłówkiem
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c['accent']))
        p.drawRect(QRectF(1, CARD_HEADER_HEIGHT - CARD_ACCENT_HEIGHT, CARD_WIDTH - 2, CARD_ACCENT_HEIGHT))

        # tabela "Informacje o zdjęciu" - przycięta do zaokrąglonej ramki
        panel = QRectF(CARD_PANEL_MARGIN, CARD_HEADER_HEIGHT + CARD_PANEL_MARGIN, CARD_WIDTH - 2 * CARD_PANEL_MARGIN,
                       CARD_PANEL_TITLE_HEIGHT + CARD_ROW_HEIGHT * len(rows))
        clip = QPainterPath()
        clip.addRoundedRect(panel, CARD_PANEL_RADIUS, CARD_PANEL_RADIUS)
        p.save()
        p.setClipPath(clip)
        p.fillRect(QRectF(panel.x(), panel.y(), panel.width(), CARD_PANEL_TITLE_HEIGHT), QColor(c['panel_title_bg']))
        label_font, value_font = _font(CARD_FONT_LABEL), _font(CARD_FONT_VALUE)
        value_metrics = QFontMetricsF(value_font)
        # kolumna nazw pól dopasowana do najdłuższej nazwy (np. "Section number" po angielsku)
        label_metrics = QFontMetricsF(label_font)
        label_column = max(CARD_LABEL_COLUMN,
                           max(label_metrics.horizontalAdvance(label) for label, _v in rows) + CARD_LABEL_GAP)
        value_w = panel.width() - label_column - CARD_TEXT_PADDING
        for i, (label, value) in enumerate(rows):
            row = QRectF(panel.x(), panel.y() + CARD_PANEL_TITLE_HEIGHT + i * CARD_ROW_HEIGHT,
                         panel.width(), CARD_ROW_HEIGHT)
            p.fillRect(row, QColor(c['row_alt'] if i % 2 else c['row']))
            p.setPen(QColor(c['label']))
            p.setFont(label_font)
            p.drawText(row.adjusted(CARD_TEXT_PADDING, 0, 0, 0), ALIGN_LEFT_CENTER, label)
            p.setPen(QColor(c['value']))
            p.setFont(value_font)
            text = value_metrics.elidedText(str(value), Qt.TextElideMode.ElideRight, value_w)
            p.drawText(QRectF(row.x() + label_column, row.y(), value_w, CARD_ROW_HEIGHT), ALIGN_LEFT_CENTER, text)
        p.restore()
        p.setPen(QColor(c['panel_title']))
        p.setFont(_font(CARD_FONT_SECTION))
        p.drawText(QRectF(panel.x() + CARD_TEXT_PADDING, panel.y(), panel.width() - 2 * CARD_TEXT_PADDING,
                          CARD_PANEL_TITLE_HEIGHT), ALIGN_LEFT_CENTER, title_section)
        p.setPen(QPen(QColor(c['panel_border']), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(panel.adjusted(0.5, 0.5, -0.5, -0.5), CARD_PANEL_RADIUS, CARD_PANEL_RADIUS)
    p.end()

    return image, btn.translated(CARD_MARGIN, CARD_MARGIN)


def imageToGlBytes(image):
    """QImage -> bajty RGBA (nie-premultiplikowane, wiersze od dołu) dla glDrawPixels.

    :returns: (szerokość, wysokość, bajty) w pikselach urządzenia
    """
    rgba = image.convertToFormat(QImage.Format.Format_RGBA8888).mirrored(False, True)
    data = rgba.constBits().asstring(rgba.sizeInBytes())
    return rgba.width(), rgba.height(), data
