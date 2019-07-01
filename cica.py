#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fontforge
import psMat
import os
import sys
import math
import glob
import width_parser
from datetime import datetime

# ASCENT = 850
# DESCENT = 174
ASCENT = 820
DESCENT = 204
SOURCE = './source'
LICENSE = open('./LICENSE.txt').read()
COPYRIGHT = open('./COPYRIGHT.txt').read()
VERSION = '5.0.1'
FAMILY = 'Cica'

def log(_str):
    """ログ出力
    fontforgeにquietオプションが無いので悲しい
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now + " " + _str)

ignoring_center = [i for i in range(0x20, 0x6ff)]
ignoring_center.extend([
    0x3001, 0x3002, 0x3008, 0x3009, 0x300a, 0x300b, 0x300c, 0x300d,
    0x300e, 0x300f, 0x3010, 0x3011, 0x3014, 0x3015, 0x3016, 0x3017,
    0x3018, 0x3019, 0x301a, 0x301b, 0x301d, 0x301e, 0x3099, 0x309a,
    0x309b, 0x309c, 0xff0c, 0xff0e,
])

def align_to_center(_g):
    """グリフを中央寄せにする
    """
    width = 0

    if _g.width > 700:
        width = 1024
    else:
        width = 512

    _g.width = width
    if _g.encoding in ignoring_center:
        return

    _g.left_side_bearing = _g.right_side_bearing = (_g.left_side_bearing + _g.right_side_bearing)/2
    _g.width = width

    return

def align_to_left(_g):
    """グリフを左寄せにする
    """
    width = _g.width
    _g.left_side_bearing = 0
    _g.width = width

def align_to_right(_g):
    """グリフを右寄せにする
    """
    width = _g.width
    bb = _g.boundingBox()
    left = width - (bb[2] - bb[0])
    _g.left_side_bearing = left
    _g.width = width

def fix_overflow(glyph):
    """上が820を超えている、または下が-204を超えているグリフを
    1024x1024の枠にはまるように修正する
    ※全角のグリフのみに実施する
    """
    if glyph.width < 1024:
        return glyph
    if glyph.isWorthOutputting:
        bb = glyph.boundingBox()
        height = bb[3] - bb[1]
        if height > 1024:
            # resize
            scale = 1024 / height
            glyph.transform(psMat.scale(scale, scale))
        bb = glyph.boundingBox()
        bottom = bb[1]
        top = bb[3]
        if bottom < -204:
            glyph.transform(psMat.translate(0, -204 - bottom))
        elif top > 820:
            glyph.transform(psMat.translate(0, 820 - top))
    return glyph

def modify_nerd(_g):
    """nerdfontの大きさと位置をCica用に調整
    """
    align_left = [
        0xe0b0, 0xe0b1, 0xe0b4, 0xe0b5, 0xe0b8, 0xe0b9, 0xe0bc,
        0xe0bd, 0xe0c0, 0xe0c1, 0xe0c4, 0xe0c6, 0xe0c8, 0xe0cc, 0xe0cd,
        0xe0d1, 0xe0d2,
    ]
    align_right = [
        0xe0b2, 0xe0b3, 0xe0b6, 0xe0b7, 0xe0b7, 0xe0ba, 0xe0bb, 0xe0be,
        0xe0bf, 0xe0c2, 0xe0c3, 0xe0c5, 0xe0c7, 0xe0ca, 0xe0ce, 0xe0d4,
    ]
    # Powerline
    if _g.encoding >= 0xe0b0 and _g.encoding <= 0xe0d4:
        _g.transform(psMat.translate(0, 5))
        _g.width = 1024

        if _g.encoding >= 0xe0b0 and _g.encoding <= 0xe0b7:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024

        if _g.encoding >= 0xe0b8 and _g.encoding <= 0xe0bf:
            _g.transform(psMat.compose(psMat.scale(0.8, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024

        if _g.encoding >= 0xe0c0 and _g.encoding <= 0xe0c3:
            _g.transform(psMat.scale(0.7, 1.0))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding >= 0xe0c4 and _g.encoding <= 0xe0c7:
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding == 0xe0c8 or _g.encoding == 0xe0ca:
            _g.transform(psMat.scale(0.7, 1.0))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding == 0xe0ce:
            _g.transform(psMat.scale(0.8, 1.0))
            bb = _g.boundingBox()
            left = 1024 - (bb[2] - bb[0])
            _g.left_side_bearing = left
            _g.width = 1024
        if _g.encoding == 0xe0cf:
            _g.transform(psMat.scale(0.9, 1.0))
            align_to_center(_g)
        if _g.encoding == 0xe0d0:
            align_to_center(_g)
        if _g.encoding == 0xe0d1:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            _g.left_side_bearing = 0
            _g.width = 1024
        if _g.encoding == 0xe0d2 or _g.encoding == 0xe0d4:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
    elif _g.encoding >= 0xf000 and _g.encoding <= 0xf2e0:
        _g.transform(psMat.compose(psMat.scale(0.75, 0.75), psMat.translate(0, 55)))
        _g.width = 1024
        align_to_center(_g)
    else:
        _g.transform(psMat.translate(0, -55))
        _g.width = 1024
        align_to_center(_g)

    return _g

def modify_iconsfordevs(_g):
    """iconsfordevsの大きさと位置をCica用に調整
    """
    _g.transform(psMat.compose(psMat.scale(2), psMat.translate(0, -126)))
    _g.width = 1024
    align_to_center(_g)
    return _g


class Cica:
    def __init__(self, family, name, output_name, weight, weight_name, style_name, font_en, font_jp, italic):
        self.family = family
        self.name = name
        self.output_name = output_name
        self.weight = weight
        self.weight_name = weight_name
        self.style_name = style_name
        self.font_en = fontforge.open('./source/%s' % font_en)
        self.font_jp = fontforge.open('./source/%s' % font_jp)
        self.italic = italic
        self.nerd = fontforge.open('./source/nerd.sfd')
        self.icons_for_devs = fontforge.open('./source/iconsfordevs.ttf')

    def remove_glyph_from_en(self):
        """jpフォント側を採用したいグリフをenフォントから削除
        """
        glyphs = [
                0x2026, # …
                ]

        for g in glyphs:
            self.font_en.selection.select(g)
            self.font_en.clear()

    def set_os2_values(self):
        """フォントメタ情報の設定
        """
        weight = self.weight
        style_name = self.style_name
        self.font_jp.os2_weight = weight
        self.font_jp.os2_width = 5
        self.font_jp.os2_fstype = 0
        if style_name == 'Regular':
            self.font_jp.os2_stylemap = 64
        elif style_name == 'Bold':
            self.font_jp.os2_stylemap = 32
        elif style_name == 'Italic':
            self.font_jp.os2_stylemap = 1
        elif style_name == 'Bold Italic':
            self.font_jp.os2_stylemap = 33
        self.font_jp.os2_vendor = 'TMNM'
        self.font_jp.os2_version = 1
        self.font_jp.os2_winascent = ASCENT
        self.font_jp.os2_winascent_add = False
        self.font_jp.os2_windescent = DESCENT
        self.font_jp.os2_windescent_add = False

        self.font_jp.os2_typoascent = -150
        self.font_jp.os2_typoascent_add = True
        self.font_jp.os2_typodescent = 100
        self.font_jp.os2_typodescent_add = True
        self.font_jp.os2_typolinegap = 0

        self.font_jp.hhea_ascent = -150
        self.font_jp.hhea_ascent_add = True
        self.font_jp.hhea_descent = 100
        self.font_jp.hhea_descent_add = True
        self.font_jp.hhea_linegap = 0
        self.font_jp.os2_panose = (2, 11, int(weight / 100), 9, 2, 2, 3, 2, 2, 7)


    def add_dejavu(self):
        dejavu = None
        weight_name = self.weight_name
        if weight_name == "Regular":
            dejavu = fontforge.open('./source/DejaVuSansMono.ttf')
        elif weight_name == "Bold":
            dejavu = fontforge.open('./source/DejaVuSansMono-Bold.ttf')

        for g in dejavu.glyphs():
            g.transform(psMat.compose(psMat.scale(0.45, 0.45), psMat.translate(-21, 0)))
            g.width = 512

        self.font_jp.importLookups(dejavu, dejavu.gpos_lookups)

        # 0x0300 - 0x036f - Combining Diacritical Marks
        for g in dejavu.glyphs():
            if g.encoding < 0x0300 or g.encoding > 0x036f or g.encoding == 0x0398:
                continue
            else:
                if len(g.references) > 0:
                    anchorPoints = g.anchorPoints
                    g.anchorPoints = ()
                    g.transform(psMat.scale(2.22, 2.22))
                    g.transform(psMat.translate(50, 0))
                    g.width = 512
                    g.anchorPoints = anchorPoints

                if g.encoding <= 0x0304:
                    anchorPoints = g.anchorPoints
                    g.anchorPoints = ()
                    g.transform(psMat.scale(1.2, 1.2))
                    g.transform(psMat.translate(-100, -60))
                    g.width = 512
                    g.anchorPoints = anchorPoints
                elif g.encoding == 0x0305:
                    g.transform(psMat.translate(0, -60))
                elif g.encoding <= 0x0315:
                    g.transform(psMat.translate(0, 0))
                elif g.encoding <= 0x0317:
                    g.transform(psMat.translate(0, 302))
                elif g.encoding <= 0x0319:
                    g.transform(psMat.translate(0, 200))
                elif g.encoding <= 0x031b:
                    g.transform(psMat.translate(0, -60))
                elif g.encoding <= 0x031c:
                    g.transform(psMat.translate(0, 22))
                elif g.encoding <= 0x031f:
                    g.transform(psMat.translate(0, 141))
                elif g.encoding <= 0x0332:
                    g.transform(psMat.translate(0, 90))
                elif g.encoding == 0x0333:
                    g.transform(psMat.compose(psMat.scale(0.9, 0.9), psMat.translate(-415, 29)))
                    g.width = 512
                elif g.encoding <= 0x0338:
                    g.transform(psMat.translate(0, 0))
                elif g.encoding <= 0x033c:
                    g.transform(psMat.translate(0, 138))
                else:
                    g.transform(psMat.translate(0, 0))
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()
        # 0x0370 - 0x03ff - GREEK
        for g in dejavu.glyphs():
            if g.encoding < 0x0370 or g.encoding > 0x03ff or g.encoding == 0x0398:
                continue
            else:
                if len(g.references) == 0:
                    bb = g.boundingBox()
                    g.anchorPoints = (('Anchor-7', 'mark', 256, bb[3] + 20),)
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2100 - 0x214f Letterlike Symbols
        for g in dejavu.glyphs():
            if g.encoding < 0x2100 or g.encoding > 0x214f or g.encoding == 0x2122:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2150 - 0x218f Number Forms
        for g in dejavu.glyphs():
            if g.encoding < 0x2150 or g.encoding > 0x218f:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2190 - 0x21ff Arrows
        # TODO: 矢印を全角のままにしたパターンも生成したい
        for g in dejavu.glyphs():
            if g.encoding < 0x2190 or g.encoding > 0x21ff:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2200 - 0x22ff Mathematical Operators
        for g in dejavu.glyphs():
            if g.encoding < 0x2200 or g.encoding > 0x22ff:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2300 - 0x23ff Miscellaneous Technical
        for g in dejavu.glyphs():
            if g.encoding < 0x2300 or g.encoding > 0x23ff:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        dejavu.close()


    def vertical_line_to_broken_bar(self):
        """縦線を破線にする
        """
        self.font_jp.selection.select(0x00a6)
        self.font_jp.copy()
        self.font_jp.selection.select(0x007c)
        self.font_jp.paste()

    def emdash_to_broken_dash(self):
        """ダッシュ記号を破線にする
        """
        self.font_jp.selection.select(0x006c)
        self.font_jp.copy()
        self.font_jp.selection.select(0x2014)
        self.font_jp.pasteInto()
        self.font_jp.intersect()

    def zenkaku_space(self):
        """全角スペースに枠をつけて可視化する
        """
        self.font_jp.selection.select(0x2610)
        self.font_jp.copy()
        self.font_jp.selection.select(0x3000)
        self.font_jp.paste()
        self.font_jp.selection.select(0x271a)
        self.font_jp.copy()
        self.font_jp.selection.select(0x3000)
        self.font_jp.pasteInto()
        self.font_jp.intersect()
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)

    def dotted_zero(self):
        """半角数字の0をドットゼロにする
        """
        self.font_jp.selection.select(0x4f)
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.paste()
        self.font_jp.selection.select(0xb7)
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.pasteInto()
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)

    def slashed_zero(self):
        """半角数字の0をスラッシュゼロにする
        """
        self.font_jp.selection.select(0x4f)
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.paste()
        self.font_jp.selection.select(0x2f)
        self.font_jp.copy()
        self.font_jp.selection.select(0x1)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.scale(0.7, 0.75), psMat.translate(80, 115)))
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.pasteInto()
        self.font_jp.removeOverlap()

    def modify_WM(self):
        """WとMの字体を調整
        """
        self.font_jp.selection.select(0x57)
        self.font_jp.transform(psMat.compose(psMat.scale(0.95, 1.0), psMat.translate(10, 0)))
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)
        self.font_jp.copy()
        self.font_jp.selection.select(0x4d)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.rotate(math.radians(180)), psMat.translate(512, 627)))
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)

    def modify_m(self, _weight):
        """mの中央の棒を少し短くする
        """
        m = fontforge.open('./source/m-Regular.sfd')
        if _weight == 'Bold':
            m.close()
            m = fontforge.open('./source/m-Bold.sfd')
        m.selection.select(0x6d)
        m.copy()
        self.font_en.selection.select(0x6d)
        self.font_en.paste()
        for g in m.glyphs():
            if g.encoding == 0x6d:
                anchorPoints = g.anchorPoints
        for g in self.font_en.glyphs():
            if g.encoding == 0x6d:
                g.anchorPoints = anchorPoints


    def add_smalltriangle(self):
        """小さいサンカクを追加
        NerdTree用
        """
        self.font_jp.selection.select(0x25bc)
        self.font_jp.copy()
        self.font_jp.selection.select(0x25be)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.scale(0.64), psMat.translate(0, 68)))
        self.font_jp.copy()
        self.font_jp.selection.select(0x25b8)
        self.font_jp.paste()
        self.font_jp.transform(psMat.rotate(math.radians(90)))
        self.font_jp.transform(psMat.translate(0, 212))

        for g in self.font_jp.glyphs():
            if g.encoding == 0x25be or g.encoding == 0x25b8:
                g.width = 512
                align_to_center(g)

    def fix_box_drawings(self):
        """罫線を調整
        """
        left = [
            0x2510, 0x2518, 0x2524, 0x2555, 0x2556, 0x2557, 0x255b, 0x255c, 0x255d,
            0x2561, 0x2562, 0x2563, 0x256e, 0x256f, 0x2574, 0x2578,
            0xf2510, 0xf2518, 0xf2524, 0xf2555, 0xf2556, 0xf2557, 0xf255b, 0xf255c, 0xf255d,
            0xff2561, 0xf2562, 0xf2563, 0xf256e, 0xf256f, 0xf2574, 0xf2578
        ]
        right = [
            0x250c, 0x2514, 0x251c, 0x2552, 0x2553, 0x2554, 0x2558, 0x2559, 0x255a,
            0x255e, 0x255f, 0x2560, 0x256d, 0x2570, 0x2576, 0x257a,
            0xf250c, 0xf2514, 0xf251c, 0xf2552, 0xf2553, 0xf2554, 0xf2558, 0xf2559, 0xf255a,
            0xf255e, 0xf255f, 0xf2560, 0xf256d, 0xf2570, 0xf2576, 0xf257a
        ]

        for g in self.font_jp.glyphs():
            if g.encoding < 0x2500:
                continue
            if g.encoding > 0x256c and g.encoding < 0xf2500:
                continue
            if g.encoding in left:
                align_to_left(g)
            elif g.encoding in right:
                align_to_right(g)

    def reiwa(self, _weight):
        """令和グリフを追加
        """
        reiwa = fontforge.open('./source/reiwa.sfd')
        if _weight == 'Bold':
            reiwa.close()
            reiwa = fontforge.open('./source/reiwa-Bold.sfd')
        for g in reiwa.glyphs():
            if g.isWorthOutputting:
                reiwa.selection.select(0x00)
                reiwa.copy()
                self.font_jp.selection.select(0x32ff)
                self.font_jp.paste()
        reiwa.close()

    def import_svg(self):
        """オリジナルのsvgグリフをインポートする
        """
        files = glob.glob('source/svg/*.svg')
        for f in files:
            filename, _ = os.path.splitext(os.path.basename(f))
            g = self.font_jp.createChar(int(filename, 16))
            g.width = 1024
            g.vwidth = 1024
            g.clear()
            g.importOutlines(f)
            g.transform(psMat.translate(0, -61))

    def add_notoemoji(self):
        notoemoji = fontforge.open('./source/NotoEmoji-Regular.ttf')
        for g in notoemoji.glyphs():
            if g.isWorthOutputting and g.encoding > 0x04f9:
                g.transform((0.42,0,0,0.42,0,0))
                align_to_center(g)
                notoemoji.selection.select(g.encoding)
                notoemoji.copy()
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()
        notoemoji.close()

    def add_gopher(self):
        """半身Gopherくんを追加
        """
        gopher = fontforge.open('./source/gopher.sfd')
        for g in gopher.glyphs():
            if g.isWorthOutputting:
                gopher.selection.select(0x40)
                gopher.copy()
                self.font_jp.selection.select(0xE160)
                self.font_jp.paste()
                g.transform(psMat.compose(psMat.scale(-1, 1), psMat.translate(g.width, 0)))
                gopher.copy()
                self.font_jp.selection.select(0xE161)
                self.font_jp.paste()
        gopher.close()

    def resize_supersub(self):
        """上付文字、下付文字を調整して可読性を上げる
        """
        superscripts = [
                {"src": 0x0031, "dest": 0x00b9}, {"src": 0x0032, "dest": 0x00b2},
                {"src": 0x0033, "dest": 0x00b3}, {"src": 0x0030, "dest": 0x2070},
                {"src": 0x0069, "dest": 0x2071}, {"src": 0x0034, "dest": 0x2074},
                {"src": 0x0037, "dest": 0x2077}, {"src": 0x0038, "dest": 0x2078},
                {"src": 0x0039, "dest": 0x2079}, {"src": 0x002b, "dest": 0x207a},
                {"src": 0x002d, "dest": 0x207b}, {"src": 0x003d, "dest": 0x207c},
                {"src": 0x0028, "dest": 0x207d}, {"src": 0x0029, "dest": 0x207e},
                {"src": 0x006e, "dest": 0x207f},
                # ↓上付きの大文字
                {"src": 0x0041, "dest": 0x1d2c}, {"src": 0x00c6, "dest": 0x1d2d},
                {"src": 0x0042, "dest": 0x1d2e}, {"src": 0x0044, "dest": 0x1d30},
                {"src": 0x0045, "dest": 0x1d31}, {"src": 0x018e, "dest": 0x1d32},
                {"src": 0x0047, "dest": 0x1d33}, {"src": 0x0048, "dest": 0x1d34},
                {"src": 0x0049, "dest": 0x1d35}, {"src": 0x004a, "dest": 0x1d36},
                {"src": 0x004b, "dest": 0x1d37}, {"src": 0x004c, "dest": 0x1d38},
                {"src": 0x004d, "dest": 0x1d39}, {"src": 0x004e, "dest": 0x1d3a},
                ## ↓REVERSED N なのでNを左右反転させる必要あり
                {"src": 0x004e, "dest": 0x1d3b, "reversed": True},
                {"src": 0x004f, "dest": 0x1d3c}, {"src": 0x0222, "dest": 0x1d3d},
                {"src": 0x0050, "dest": 0x1d3e}, {"src": 0x0052, "dest": 0x1d3f},
                {"src": 0x0054, "dest": 0x1d40}, {"src": 0x0055, "dest": 0x1d41},
                {"src": 0x0057, "dest": 0x1d42},
                # ↓上付きの小文字
                {"src": 0x0061, "dest": 0x1d43}, {"src": 0x0250, "dest": 0x1d44},
                {"src": 0x0251, "dest": 0x1d45}, {"src": 0x1d02, "dest": 0x1d46},
                {"src": 0x0062, "dest": 0x1d47}, {"src": 0x0064, "dest": 0x1d48},
                {"src": 0x0065, "dest": 0x1d49}, {"src": 0x0259, "dest": 0x1d4a},
                {"src": 0x025b, "dest": 0x1d4b}, {"src": 0x025c, "dest": 0x1d4c},
                {"src": 0x0067, "dest": 0x1d4d},
                ## ↓TURNED i なので 180度回す必要あり
                {"src": 0x0069, "dest": 0x1d4e, "turned": True},
                {"src": 0x006b, "dest": 0x1d4f}, {"src": 0x006d, "dest": 0x1d50},
                {"src": 0x014b, "dest": 0x1d51}, {"src": 0x006f, "dest": 0x1d52},
                {"src": 0x0254, "dest": 0x1d53}, {"src": 0x1d16, "dest": 0x1d54},
                {"src": 0x1d17, "dest": 0x1d55}, {"src": 0x0070, "dest": 0x1d56},
                {"src": 0x0074, "dest": 0x1d57}, {"src": 0x0075, "dest": 0x1d58},
                {"src": 0x1d1d, "dest": 0x1d59}, {"src": 0x026f, "dest": 0x1d5a},
                {"src": 0x0076, "dest": 0x1d5b}, {"src": 0x1d25, "dest": 0x1d5c},
                {"src": 0x03b2, "dest": 0x1d5d}, {"src": 0x03b3, "dest": 0x1d5e},
                {"src": 0x03b4, "dest": 0x1d5f}, {"src": 0x03c6, "dest": 0x1d60},
                {"src": 0x03c7, "dest": 0x1d61},
                {"src": 0x0056, "dest": 0x2c7d}, {"src": 0x0068, "dest": 0x02b0},
                {"src": 0x0266, "dest": 0x02b1}, {"src": 0x006a, "dest": 0x02b2},
                {"src": 0x006c, "dest": 0x02e1}, {"src": 0x0073, "dest": 0x02e2},
                {"src": 0x0078, "dest": 0x02e3}, {"src": 0x0072, "dest": 0x02b3},
                {"src": 0x0077, "dest": 0x02b7}, {"src": 0x0079, "dest": 0x02b8},
                {"src": 0x0063, "dest": 0x1d9c}, {"src": 0x0066, "dest": 0x1da0},
                {"src": 0x007a, "dest": 0x1dbb}, {"src": 0x0061, "dest": 0x00aa},
                {"src": 0x0252, "dest": 0x1d9b}, {"src": 0x0255, "dest": 0x1d9d},
                {"src": 0x00f0, "dest": 0x1d9e}, {"src": 0x025c, "dest": 0x1d9f},
                {"src": 0x025f, "dest": 0x1da1}, {"src": 0x0261, "dest": 0x1da2},
                {"src": 0x0265, "dest": 0x1da3}, {"src": 0x0268, "dest": 0x1da4},
                {"src": 0x0269, "dest": 0x1da5}, {"src": 0x026a, "dest": 0x1da6},
                {"src": 0x1d7b, "dest": 0x1da7}, {"src": 0x029d, "dest": 0x1da8},
                {"src": 0x026d, "dest": 0x1da9}, {"src": 0x1d85, "dest": 0x1daa},
                {"src": 0x029f, "dest": 0x1dab}, {"src": 0x0271, "dest": 0x1dac},
                {"src": 0x0270, "dest": 0x1dad}, {"src": 0x0272, "dest": 0x1dae},
                {"src": 0x0273, "dest": 0x1daf}, {"src": 0x0274, "dest": 0x1db0},
                {"src": 0x0275, "dest": 0x1db1}, {"src": 0x0278, "dest": 0x1db2},
                {"src": 0x0282, "dest": 0x1db3}, {"src": 0x0283, "dest": 0x1db4},
                {"src": 0x01ab, "dest": 0x1db5}, {"src": 0x0289, "dest": 0x1db6},
                {"src": 0x028a, "dest": 0x1db7}, {"src": 0x1d1c, "dest": 0x1db8},
                {"src": 0x028b, "dest": 0x1db9}, {"src": 0x028c, "dest": 0x1dba},
                {"src": 0x0290, "dest": 0x1dbc}, {"src": 0x0291, "dest": 0x1dbd},
                {"src": 0x0292, "dest": 0x1dbe}, {"src": 0x03b8, "dest": 0x1dbf},

        ]
        subscripts = [
                {"src": 0x0069, "dest": 0x1d62}, {"src": 0x0072, "dest": 0x1d63},
                {"src": 0x0075, "dest": 0x1d64}, {"src": 0x0076, "dest": 0x1d65},
                {"src": 0x03b2, "dest": 0x1d66}, {"src": 0x03b3, "dest": 0x1d67},
                {"src": 0x03c1, "dest": 0x1d68}, {"src": 0x03c6, "dest": 0x1d69},
                {"src": 0x03c7, "dest": 0x1d6a}, {"src": 0x006a, "dest": 0x2c7c},
                {"src": 0x0030, "dest": 0x2080}, {"src": 0x0031, "dest": 0x2081},
                {"src": 0x0032, "dest": 0x2082}, {"src": 0x0033, "dest": 0x2083},
                {"src": 0x0034, "dest": 0x2084}, {"src": 0x0035, "dest": 0x2085},
                {"src": 0x0036, "dest": 0x2086}, {"src": 0x0037, "dest": 0x2087},
                {"src": 0x0038, "dest": 0x2088}, {"src": 0x0039, "dest": 0x2089},
                {"src": 0x002b, "dest": 0x208a}, {"src": 0x002d, "dest": 0x208b},
                {"src": 0x003d, "dest": 0x208c}, {"src": 0x0028, "dest": 0x208d},
                {"src": 0x0029, "dest": 0x208e}, {"src": 0x0061, "dest": 0x2090},
                {"src": 0x0065, "dest": 0x2091}, {"src": 0x006f, "dest": 0x2092},
                {"src": 0x0078, "dest": 0x2093}, {"src": 0x0259, "dest": 0x2094},
                {"src": 0x0068, "dest": 0x2095}, {"src": 0x006b, "dest": 0x2096},
                {"src": 0x006c, "dest": 0x2097}, {"src": 0x006d, "dest": 0x2098},
                {"src": 0x006e, "dest": 0x2099}, {"src": 0x0070, "dest": 0x209a},
                {"src": 0x0073, "dest": 0x209b}, {"src": 0x0074, "dest": 0x209c}
        ]

        for g in superscripts:
            self.font_jp.selection.select(g["src"])
            self.font_jp.copy()
            self.font_jp.selection.select(g["dest"])
            self.font_jp.paste()
        for g in subscripts:
            self.font_jp.selection.select(g["src"])
            self.font_jp.copy()
            self.font_jp.selection.select(g["dest"])
            self.font_jp.paste()

        for g in self.font_jp.glyphs("encoding"):
            if g.encoding > 0x2c7d:
                continue
            elif self.in_scripts(g.encoding, superscripts):
                if g.encoding == 0x1d5d or g.encoding == 0x1d61:
                    g.transform(psMat.scale(0.70, 0.70))
                elif g.encoding == 0x1d3b:
                    g.transform(psMat.scale(0.75, 0.75))
                    g.transform(psMat.compose(psMat.scale(-1, 1), psMat.translate(g.width, 0)))
                elif g.encoding == 0x1d4e:
                    g.transform(psMat.scale(0.75, 0.75))
                    g.transform(psMat.rotate(3.14159))
                    g.transform(psMat.translate(0, 512))
                else:
                    g.transform(psMat.scale(0.75, 0.75))
                bb = g.boundingBox()
                g.transform(psMat.translate(0, 244))
                align_to_center(g)
            elif self.in_scripts(g.encoding, subscripts):
                if g.encoding == 0x1d66 or g.encoding == 0x1d6a:
                    g.transform(psMat.scale(0.70, 0.70))
                else:
                    g.transform(psMat.scale(0.75, 0.75))
                bb = g.boundingBox()
                y = -144
                if bb[1] < -60: # DESCENT - 144
                    y = -60
                g.transform(psMat.translate(0, y))
                align_to_center(g)

    def in_scripts(self, encoding, scripts):
        """scriptsの中にencodingが含まれるかをチェックする
        """
        for s in scripts:
            if encoding == s["dest"]:
                return True
        return False

    def modify_ellipsis(self):
        """3点リーダーを半角にする
        DejaVuSansMono の U+22EF(⋯) をU+2026(…)、U+22EE(⋮)、U+22F0(⋰)、U+22F1(⋱)
        にコピーした上で回転させて生成

        三点リーダの文字幅について · Issue #41 · miiton/Cica https://github.com/miiton/Cica/issues/41
        """
        self.font_jp.selection.select(0x22ef)
        self.font_jp.copy()
        self.font_jp.selection.select(0x2026)
        self.font_jp.paste()
        self.font_jp.selection.select(0x22ee)
        self.font_jp.paste()
        self.font_jp.selection.select(0x22f0)
        self.font_jp.paste()
        self.font_jp.selection.select(0x22f1)
        self.font_jp.paste()
        for g in self.font_jp.glyphs("encoding"):
            if g.encoding < 0x22ee:
                continue
            elif g.encoding > 0x22f1:
                break
            elif g.encoding == 0x22ee:
                bb = g.boundingBox()
                cx = (bb[2] + bb[0]) / 2
                cy = (bb[3] + bb[1]) / 2
                trcen = psMat.translate(-cx, -cy)
                rotcen = psMat.compose(trcen, psMat.compose(psMat.rotate(math.radians(90)), psMat.inverse(trcen)))
                g.transform(rotcen)
            elif g.encoding == 0x22f0:
                bb = g.boundingBox()
                cx = (bb[2] + bb[0]) / 2
                cy = (bb[3] + bb[1]) / 2
                trcen = psMat.translate(-cx, -cy)
                rotcen = psMat.compose(trcen, psMat.compose(psMat.rotate(math.radians(45)), psMat.inverse(trcen)))
                g.transform(rotcen)
            elif g.encoding == 0x22f1:
                bb = g.boundingBox()
                cx = (bb[2] + bb[0]) / 2
                cy = (bb[3] + bb[1]) / 2
                trcen = psMat.translate(-cx, -cy)
                rotcen = psMat.compose(trcen, psMat.compose(psMat.rotate(math.radians(-45)), psMat.inverse(trcen)))
                g.transform(rotcen)

    def stroked_d(self):
        """DをĐにする
        """
        self.font_jp.selection.select(0x110)
        self.font_jp.copy()
        self.font_jp.selection.select(0x44)
        self.font_jp.paste()


    def build_font(self, emoji):

        log('remove_glyph_from_en()')
        self.remove_glyph_from_en()

        log('transform font_en')
        for g in self.font_en.glyphs():
            g.transform((0.42,0,0,0.42,0,0))
            align_to_center(g)

        self.modify_m(self.weight_name)

        log('transform font_jp')
        for g in self.font_jp.glyphs():
            g.transform((0.91,0,0,0.91,0,0))
            full_half_threshold = 700
            if self.italic:
                g.transform(psMat.skew(0.25))
                skew_amount = g.font.ascent * 0.91 * 0.25
                g.width = g.width + skew_amount
                full_half_threshold += skew_amount
            if g.width > full_half_threshold:
                width = 1024
            else:
                width = 512
            g.transform(psMat.translate((width - g.width)/2, 0))
            g.width = width
            align_to_center(g)

        log('modify border glyphs')
        for g in self.font_en.glyphs():
            if  g.isWorthOutputting:
                if self.italic:
                    g.transform(psMat.skew(0.25))
                if g.encoding >= 0x2500 and g.encoding <= 0x257f:
                    # 全角の罫線を0xf0000以降に退避
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.copy()
                    self.font_jp.selection.select(g.encoding + 0xf0000)
                    self.font_jp.paste()
                if g.encoding >= 0x2500 and g.encoding <= 0x25af:
                    g.transform(psMat.compose(psMat.scale(1.024, 1.024), psMat.translate(0, -30)))
                    align_to_center(g)
                self.font_en.selection.select(g.encoding)
                self.font_en.copy()
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()

        log('modify nerd glyphs')
        for g in self.nerd.glyphs():
            if g.encoding < 0xe0a0 or g.encoding > 0xfd46:
                continue
            g = modify_nerd(g)
            self.nerd.selection.select(g.encoding)
            self.nerd.copy()
            if g.encoding >= 0xf500:
                # Material Design IconsはNerd Fontsに従うとアラビア文字等を壊して
                # しまうので、0xf0000〜に配置する
                self.font_jp.selection.select(g.encoding + 0xf0000)
                self.font_jp.paste()
            else:
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()

        log('modify icons_for_devs glyphs')
        for g in self.icons_for_devs.glyphs():
            if g.encoding < 0xe900 or g.encoding > 0xe950:
                continue
            g = modify_iconsfordevs(g)
            self.icons_for_devs.selection.select(g.encoding)
            self.icons_for_devs.copy()
            self.font_jp.selection.select(g.encoding)
            self.font_jp.paste()

        self.fix_box_drawings()
        self.zenkaku_space()
        self.dotted_zero()
        self.slashed_zero()
        self.stroked_d()
        self.modify_WM()
        self.vertical_line_to_broken_bar()
        self.emdash_to_broken_dash()
        self.reiwa(self.weight_name)
        self.add_gopher()
        self.modify_ellipsis()
        if emoji:
            self.add_notoemoji()
        self.add_smalltriangle()
        self.add_dejavu()
        self.resize_supersub()

        log("fix_overflow()")
        for g in self.font_jp.glyphs():
            g = fix_overflow(g)
        log("import_svg()")
        self.import_svg()
        self.font_jp.ascent = ASCENT
        self.font_jp.descent = DESCENT
        self.font_jp.upos = 45
        self.font_jp.fontname = self.family
        self.font_jp.familyname = self.family
        self.font_jp.fullname = self.name
        self.font_jp.weight = self.weight_name
        self.set_os2_values()
        self.font_jp.appendSFNTName(0x411,0, COPYRIGHT)
        self.font_jp.appendSFNTName(0x411,1, self.family)
        self.font_jp.appendSFNTName(0x411,2, self.style_name)
        self.font_jp.appendSFNTName(0x411,4, self.name)
        self.font_jp.appendSFNTName(0x411,5, "Version " + VERSION)
        self.font_jp.appendSFNTName(0x411,6, self.family + "-" + self.weight_name)
        self.font_jp.appendSFNTName(0x411,13, LICENSE)
        self.font_jp.appendSFNTName(0x411,16, self.family)
        self.font_jp.appendSFNTName(0x411,17, self.style_name)
        self.font_jp.appendSFNTName(0x409,0, COPYRIGHT)
        self.font_jp.appendSFNTName(0x409,1, self.family)
        self.font_jp.appendSFNTName(0x409,2, self.style_name)
        self.font_jp.appendSFNTName(0x409,3, VERSION + ";" + self.family + "-" + self.style_name)
        self.font_jp.appendSFNTName(0x409,4, self.name)
        self.font_jp.appendSFNTName(0x409,5, "Version " + VERSION)
        self.font_jp.appendSFNTName(0x409,6, self.name)
        self.font_jp.appendSFNTName(0x409,13, LICENSE)
        self.font_jp.appendSFNTName(0x409,16, self.family)
        self.font_jp.appendSFNTName(0x409,17, self.style_name)
        if emoji:
            fontpath = './dist/%s' % self.output_name
        else:
            fontpath = './dist/noemoji/%s' % self.output_name

        self.font_jp.generate(fontpath)

        self.font_jp.close()
        self.font_en.close()
        self.nerd.close()
        self.icons_for_devs.close()

fonts = [
    {
        'family': FAMILY,
        'name': FAMILY + '-Regular',
        'filename': FAMILY + '-Regular.ttf',
        'weight': 400,
        'weight_name': 'Regular',
        'style_name': 'Regular',
        'hack': 'Hack-Regular.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-regular.ttf',
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-RegularItalic',
        'filename': FAMILY + '-RegularItalic.ttf',
        'weight': 400,
        'weight_name': 'Regular',
        'style_name': 'Italic',
        'hack': 'Hack-Regular.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-regular.ttf',
        'italic': True,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-Bold',
        'filename': FAMILY + '-Bold.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold',
        'hack': 'Hack-Bold.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-bold.ttf',
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-BoldItalic',
        'filename': FAMILY + '-BoldItalic.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold Italic',
        'hack': 'Hack-Bold.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-bold.ttf',
        'italic': True,
    }
]


def main():
    for _f in fonts:
        cica = Cica(_f["family"],
                _f["name"],
                _f["filename"],
                _f["weight"],
                _f["weight_name"],
                _f["style_name"],
                _f["hack"],
                _f["mgen_plus"],
                _f["italic"]
                )
        cica.build_font(True)

if __name__ == '__main__':
    main()
