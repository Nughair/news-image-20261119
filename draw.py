#!/usr/bin/env python3
"""Draw the news-image-20261119 broadsheet: one image summing up the world
news of Thursday 19 November 2026. All content comes from the verified
STORIES dossier for this edition; nothing else is pictured. Original flat
illustrations drawn in code with Pillow; the world map is drawn from
hand-coded continent polygons projected from lon/lat."""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14
INK = (24, 24, 24)
PAPER = (250, 247, 238)
RED = (178, 34, 34)
NAVY = (24, 42, 72)
GREY = (110, 108, 100)
LIGHT_LINE = (190, 186, 174)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text; if it overflows max_lines, shrink the font until it fits."""
    size = fnt.size
    while size > 7:
        f = font(fnt.path, size) if hasattr(fnt, "path") else fnt
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
    return wrap(draw, text, font(fnt.path, 7), max_w), font(fnt.path, 7)


# ---------------------------------------------------------------- data
# region per story; tally is computed from this, not typed.
CARDS = [
    dict(n=1, place="SHENZHEN", beat="SUMMIT", region="ASIA",
         head="Trump, Xi and Putin hold first three-way summit",
         sub="90 minutes at Kylin Villa; a \u201cDeclaration on Peace\u201d: nuclear war "
             "\u201ccannot be won and must never be fought\u201d. No Ukraine, Iran, Taiwan or trade.",
         src="Reuters / AP", pin=(114.1, 22.5), scene="summit",
         bg=(232, 222, 200)),
    dict(n=2, place="THE HAGUE", beat="LAW", region="ASIA",
         head="World Court: Myanmar committed genocide",
         sub="ICJ finds Myanmar guilty over the Rohingya, 9\u20136 \u2014 its first-ever state "
             "genocide finding. About 10,000 killed; 700,000+ fled.",
         src="Reuters / BBC", pin=(4.3, 52.1), scene="court",
         bg=(214, 224, 232)),
    dict(n=3, place="ANTALYA", beat="CLIMATE", region="WORLD",
         head="COP31 draft drops fossil fuels and $120bn aid goal",
         sub="Slimmed text: 80 paragraphs, down from 144. Keeps the 35-by-35 goal; "
             "talks end Friday. A draft, not a deal.",
         src="Reuters / UN News", pin=(28.0, 39.0), scene="climate",
         bg=(210, 230, 208)),
    dict(n=4, place="CRIMEA", beat="WAR", region="EUROPE",
         head="Ukraine hits Kerch rail line a third time",
         sub="Kyiv says Neptune missiles struck overnight; Moscow halts trains, then "
             "restores one track. Road span fell 17 Nov.",
         src="Reuters / AP", pin=(38.5, 45.3), scene="bridge",
         bg=(228, 216, 208)),
    dict(n=5, place="RIYADH", beat="WAR", region="MIDDLE EAST",
         head="Houthi missiles shot down over Riyadh",
         sub="Coalition intercepts missiles aimed at the capital; debris damages a "
             "tower, no injuries. Saudi jets strike Sanaa.",
         src="Reuters / AFP", pin=(46.7, 24.7), scene="missiles",
         bg=(232, 220, 200)),
    dict(n=6, place="NEW YORK", beat="MARKETS", region="AMERICAS",
         head="Anthropic starts trading on Nasdaq",
         sub="Priced $83 Wednesday; opens $111.50, closes $97.17, up 17%. $81.3bn "
             "raised \u2014 the biggest IPO on record.",
         src="Nasdaq / AP", pin=(-72.0, 45.0), scene="markets",
         bg=(208, 224, 214)),
    dict(n=7, place="WORLDWIDE", beat="GAMES", region="WORLD",
         head="GTA VI goes on sale after a 13-year wait",
         sub="Midnight unlocks, New Zealand first; $79.99 on PS5 and Xbox Series X|S, "
             "no PC yet. Pre-load 212 GB.",
         src="Rockstar / PlayStation", pin=(174.8, -36.8), scene="games",
         bg=(226, 216, 232)),
    dict(n=8, place="ODISHA", beat="STORM", region="ASIA",
         head="Cyclone Akvan nears India's coast",
         sub="Odisha evacuates 72,000, with 200,000 listed to move. Landfall due "
             "Friday noon near Gopalpur; winds 90\u2013100 kmph.",
         src="IMD / ANI", pin=(85.0, 20.0), scene="cyclone",
         bg=(206, 224, 230)),
    dict(n=9, place="SEOUL", beat="EDUCATION", region="ASIA",
         head="Half a million sit Korea's big exam",
         sub="551,864 candidates at 1,312 centres; flights pause 35 minutes for the "
             "listening test. 98 rule violations.",
         src="Yonhap / AJP", pin=(127.0, 37.5), scene="exam",
         bg=(232, 228, 200)),
    dict(n=10, place="CANBERRA", beat="ECONOMY", region="OCEANIA",
         head="Australia's jobless rate hits 4.9%",
         sub="Highest since October 2021; employment falls 43,500 in October. Cash "
             "rate 4.85% after five hikes this year.",
         src="ABS / Reuters", pin=(149.1, -35.3), scene="economy",
         bg=(230, 222, 206)),
    dict(n=11, place="JAKARTA", beat="LAW", region="ASIA",
         head="Indonesia passes asset-seizure law after 18 years",
         sub="State may seize assets of Rp1bn or more without a conviction, for "
             "corruption, narcotics, terror, trafficking, IT fraud.",
         src="AP", pin=(106.8, -6.2), scene="law",
         bg=(216, 222, 230)),
    dict(n=12, place="GAZA", beat="WAR", region="MIDDLE EAST",
         head="Israel ends first raid past Gaza's Yellow Line",
         sub="Army says central Gaza operation complete; Salah al-Din road reopens. "
             "Hamas calls the raid, begun Wednesday, a breach.",
         src="Reuters / AFP", pin=(35.0, 30.0), scene="road",
         bg=(232, 218, 204)),
    dict(n=13, place="BOGOT\u00c1", beat="LABOUR", region="AMERICAS",
         head="Colombia's unions hold a national strike",
         sub="Teachers and workers march in five cities against President De la "
             "Espriella's Economic Rescue Law.",
         src="Reuters", pin=(-74.1, 4.6), scene="march",
         bg=(228, 210, 210)),
    dict(n=14, place="WASHINGTON", beat="IRAN WAR", region="MIDDLE EAST",
         head="Trump: no Iran decision until next year",
         sub="\u201cI'll talk to you about it after the beginning of the year,\u201d he says "
             "aboard Air Force One. \u201cWe've got time.\u201d",
         src="Reuters / Fox / Axios", pin=(-79.0, 36.0), scene="plane",
         bg=(214, 220, 232)),
    dict(n=15, place="GREENLAND", beat="SECURITY", region="EUROPE",
         head="Denmark backs Arctic pact with US, 109\u20130",
         sub="Parliament approves the Greenland defence agreement, signed in "
             "September, by 109 votes to none.",
         src="Folketing / Reuters", pin=(-51.7, 64.2), scene="vote",
         bg=(206, 226, 228)),
]

BRIEFS = [
    (16, "BERLIN", "EUROPE", "Allies meet hours after Shenzhen: ~30 leaders weigh security guarantees for Ukraine."),
    (17, "SHENZHEN", "ASIA", "APEC adopts its declaration; Xi pledges $20m for APEC cooperation; Vietnam hosts in 2027."),
    (18, "SHENZHEN", "ASIA", "Trump and Putin meet alone for about 40 minutes; Xi and Trump hold a bilateral first."),
    (19, "SHENZHEN", "ASIA", "Xi urges a ban on all nuclear arms, Chinese media report."),
    (20, "SHENZHEN", "ASIA", "Albanese tells Putin: \u201cEnd your war, end it now.\u201d"),
    (21, "MOSCOW", "EUROPE", "Putin rejects further ceasefire and warns Russia's response will be \u201cfar more painful\u201d."),
    (22, "KYIV", "EUROPE", "Russian strikes kill at least five and cut power in five regions."),
    (23, "LONDON", "EUROPE", "UK and Norway announce a joint programme of over \u00a3100m for two Ukrainian naval craft."),
    (24, "HORMUZ", "MIDDLE EAST", "Iran's navy says tankers struck mines in the strait. (Count disputed; not given.)"),
    (25, "WASHINGTON", "AMERICAS", "Senate rejects an Iran war-powers resolution, 51\u201348."),
    (26, "RIYADH", "MIDDLE EAST", "Crown prince and T\u00fcrkiye's president urge Trump not to resume strikes on Iran."),
    (27, "WASHINGTON", "AMERICAS", "Vance distances himself from the Iran war; Trump says \u201cwhat he said was right\u201d."),
    (28, "SANAA", "MIDDLE EAST", "Saudi jets strike the Houthi capital early on Thursday, Houthi media report."),
    (29, "GAZA", "MIDDLE EAST", "Five aid groups score the peace plan's implementation 4 out of 26."),
    (30, "NAIROBI", "AFRICA", "Marathon champion Jepchirchir is banned three years for EPO; her Sydney win is stripped."),
    (31, "DUBAI", "AFRICA", "SWISSAID says 591 tonnes of illicit African gold reached the UAE in 2024."),
    (32, "MOGADISHU", "AFRICA", "Somalia orders the UAE ambassador to leave within 72 hours and recalls its own envoy."),
    (33, "PORT SUDAN", "AFRICA", "Court sentences RSF chief Hemedti to death in absentia for a second time."),
    (34, "PRETORIA", "AFRICA", "Reserve Bank holds its rate at 7.25%; vote split 4\u20133; inflation 5.2%."),
    (35, "NAIROBI", "AFRICA", "Kenya floods kill six and affect 1,141 households; two missing after a boat capsizes."),
    (36, "DAKAR", "AFRICA", "Migrant boat sinks off Yenne; four bodies found, dozens missing, about 100 aboard."),
    (37, "CANARY ISLANDS", "AFRICA", "24,364 migrants arrived by sea in 2026 to 15 November, up nearly two-thirds."),
    (38, "BELGRADE", "EUROPE", "Student List's Aleksandar Cupic is elected parliament speaker, 140 votes to 97."),
    (39, "BRUSSELS", "EUROPE", "Eurozone inflation is confirmed at 4.0%."),
    (40, "BRUSSELS", "EUROPE", "EU delays its methane rules by two years."),
    (41, "KRASNODAR", "EUROPE", "Kyiv says it hit two oil refineries."),
    (42, "ZURICH", "WORLD", "FIFA confirms Diallo and Tashima will challenge Infantino; vote 18 March 2027 in Rabat."),
    (43, "LONDON", "EUROPE", "Bayesian inquiry finds the yacht vulnerable to knockdown in 70-knot winds; seven died."),
    (44, "SAN FRANCISCO", "AMERICAS", "Record rain from an atmospheric river floods streets and cuts power."),
    (45, "FLORIDA", "AMERICAS", "Broward and Miami-Dade schools shut for a second day after 15 inches of rain."),
    (46, "COOK ISLANDS", "OCEANIA", "Cyclone Xavier eases to Category 4; more than 300 people shelter on Pukapuka."),
    (47, "S\u00c3O PAULO", "AMERICAS", "Brazil's real hits a 19-month low; central bank sells $1bn of reserves."),
    (48, "SYDNEY", "OCEANIA", "ASX 200 falls 1.04% to 8,730.4 after the jobs data."),
    (49, "AUCKLAND", "OCEANIA", "New Zealanders are first into GTA VI as the midnight unlocks roll around the world."),
    (50, "PARIS", "EUROPE", "Greens' Tondelier opens the door to backing M\u00e9lenchon; Le Pen leads him 68.5\u201331.5 in a poll."),
]

NUMBERS = [
    ("3", "presidents at one table"),
    ("9\u20136", "ICJ vote on Myanmar"),
    ("$81.3bn", "Anthropic IPO raised"),
    ("551,864", "Suneung candidates"),
    ("72,000", "evacuated in Odisha"),
    ("109\u20130", "Greenland pact vote"),
]

DATE_CHECK = [
    ("18 NOV", "Iran drone interceptions over Kuwait and Bahrain; EU's \u20ac45bn Ukraine loan; "
     "Jeffries named House Democratic leader; Voyager 1 one light-day out; Peltola's Alaska win; "
     "Van Gogh sells for $190.4m; Hegseth's US\u2013Venezuela deal; Derna drug haul; William and Kate "
     "meet Modi; Australia's West Bank settler sanctions; Carney's China tariff relief; \u0130mamo\u011flu sentenced."),
    ("17 NOV", "Nvidia's $115.8bn quarter; Ebola tops 11,000 in DR Congo; measles-free status lost "
     "(US, Mexico, Bolivia); Knesset elects Kahana 66\u201352; Serbia's student MPs seated; An-12 crash "
     "in Siberia, 19 dead; Board of Peace warns the Gaza truce may collapse; Deutsche Bank\u2013Epstein files."),
    ("16 NOV", "First COP31 draft (144 paragraphs, fossil-fuel phase-out call)."),
    ("4 NOV", "Nature's \u201cmissing billion years\u201d study.   31 OCT: Bolivia's El Ni\u00f1o emergency declared."),
    ("20 NOV", "Friday, not Thursday: COP31's scheduled close; Cyclone Akvan's landfall, due Friday noon."),
]

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]

# Brief-place dots on the map (lon, lat).
BRIEF_DOTS = [(13.4, 52.5), (37.6, 55.8), (30.5, 50.4), (-0.1, 51.5), (56.5, 26.5),
              (44.2, 15.3), (36.8, -1.3), (55.3, 25.2), (45.3, 2.0), (37.2, 19.6),
              (28.2, -25.7), (-17.4, 14.7), (-15.6, 28.3), (20.5, 44.8), (4.35, 50.85),
              (39.0, 45.0), (8.5, 47.4), (-122.4, 37.8), (-80.2, 25.8), (-160.0, -21.2),
              (-46.6, -23.5), (151.2, -33.9), (2.35, 48.85)]

# Coarse continent outlines (lon, lat), drawn from memory of the world map.
EURASIA = [(-10, 36), (-9, 43), (-2, 48), (0, 51), (3, 53), (8, 57), (10, 59), (5, 62),
           (12, 65), (18, 69), (28, 71), (32, 70), (40, 66), (48, 68), (60, 69), (70, 72),
           (80, 73), (100, 76), (110, 74), (130, 72), (150, 70), (170, 66), (178, 65),
           (170, 60), (162, 56), (156, 51), (150, 59), (142, 59), (141, 52), (140, 45),
           (135, 43), (130, 42), (127, 40), (126, 38), (122, 37), (120, 35), (122, 32),
           (120, 28), (110, 21), (108, 18), (105, 10), (103, 8), (100, 8), (98, 10),
           (95, 16), (92, 21), (89, 22), (86, 20), (83, 18), (80, 15), (77, 8), (75, 12),
           (72, 20), (68, 23), (65, 25), (60, 25), (57, 26), (54, 27), (52, 29), (50, 30),
           (48, 30), (50, 26), (52, 25), (56, 26), (58, 24), (59, 22), (55, 17), (52, 15),
           (48, 14), (44, 13), (43, 12), (40, 15), (39, 20), (38, 25), (37, 29), (36, 36),
           (33, 36), (30, 36), (27, 37), (23, 36), (22, 37), (19, 40), (19, 42), (16, 44),
           (14, 45), (12, 44), (10, 44), (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37),
           (-6, 36), (-9, 37), (-10, 36)]
N_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66), (-80, 73),
             (-70, 62), (-65, 60), (-60, 55), (-55, 47), (-60, 45), (-70, 42), (-75, 35),
             (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-97, 26), (-105, 20), (-110, 23),
             (-115, 28), (-120, 34), (-125, 40), (-124, 48), (-130, 55), (-145, 60),
             (-155, 58), (-165, 60), (-168, 66)]
S_AMERICA = [(-80, 10), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18), (-70, -23),
             (-70, -30), (-72, -37), (-73, -44), (-70, -52), (-66, -55), (-68, -50),
             (-62, -41), (-58, -34), (-52, -32), (-48, -27), (-41, -22), (-35, -9),
             (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-55, 5), (-60, 8), (-70, 10),
             (-77, 8), (-80, 10)]
AFRICA = [(-6, 35), (-10, 31), (-17, 15), (-17, 12), (-13, 9), (-8, 5), (-4, 5), (0, 6),
          (6, 4), (9, 4), (9, -1), (12, -5), (13, -12), (12, -18), (14, -22), (16, -28),
          (18, -34), (20, -35), (26, -34), (32, -28), (35, -24), (40, -16), (40, -10),
          (42, -4), (46, -1), (51, 2), (51, 11), (48, 11), (43, 12), (40, 15), (38, 18),
          (37, 22), (35, 28), (32, 31), (30, 31), (22, 33), (19, 32), (11, 34), (10, 37),
          (5, 37), (-1, 35), (-6, 35)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
             (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
             (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20), (113, -22)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (178, -37), (175, -40),
      (173, -42), (170, -44), (167, -45)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 70), (-22, 74),
             (-30, 76), (-40, 78), (-55, 76), (-58, 74), (-60, 70), (-55, 64), (-55, 60)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 38), (141, 40),
         (142, 42), (144, 44), (142, 44), (140, 42), (139, 38), (137, 37), (135, 34),
         (132, 33), (130, 31)]
INDONESIA = [(95, 5), (98, 8), (100, 6), (103, 1), (105, -2), (107, -6), (110, -7),
             (114, -8), (118, -9), (120, -10), (122, -8), (125, -9), (128, -4), (130, -2),
             (132, 0), (135, -1), (138, -2), (140, -4), (141, -8), (138, -8), (135, -7),
             (132, -5), (130, -4), (128, -3), (125, -2), (122, 0), (120, 1), (118, 2),
             (115, 4), (112, 4), (108, 3), (105, 2), (102, 4), (98, 8), (95, 5)]
CONTINENTS = [EURASIA, N_AMERICA, S_AMERICA, AFRICA, AUSTRALIA, NZ, GREENLAND, UK,
              JAPAN, INDONESIA]


# ---------------------------------------------------------------- scenes
def draw_scene(d, box, card):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=card["bg"])
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    s = card["scene"]
    if s == "summit":  # three flags over a table
        for i, col in enumerate([(178, 34, 34), (200, 40, 40), (40, 70, 160)]):
            fx = x0 + 14 + i * 26
            d.rectangle([fx, y0 + 4, fx + 18, y0 + 18], fill=col, outline=INK)
            d.line([fx + 9, y0 + 18, fx + 9, y0 + 24], fill=INK, width=1)
        d.rectangle([x0 + 6, y0 + 24, x1 - 6, y1 - 2], fill=(120, 90, 60))
        d.rectangle([x0 + 6, y0 + 24, x1 - 6, y0 + 26], fill=(240, 235, 220))
    elif s == "court":  # courthouse columns + scales
        d.rectangle([x0 + 8, y0 + 4, x1 - 8, y0 + 8], fill=NAVY)
        for i in range(3):
            px = x0 + 16 + i * 22
            d.rectangle([px, y0 + 8, px + 7, y0 + 22], fill=(250, 250, 250), outline=INK)
        d.rectangle([x0 + 8, y0 + 22, x1 - 8, y1 - 2], fill=NAVY)
        d.ellipse([x1 - 26, y0 + 10, x1 - 14, y0 + 22], outline=RED, width=2)
    elif s == "climate":  # sun over a green globe
        d.ellipse([cx - 11, cy - 9, cx + 11, cy + 9], fill=(90, 160, 90), outline=INK)
        d.arc([cx - 11, cy - 9, cx + 11, cy + 9], 200, 340, fill=(40, 90, 40), width=2)
        d.ellipse([cx + 12, y0 + 3, cx + 20, y0 + 11], fill=(230, 170, 40))
        d.line([x0 + 8, y1 - 4, x1 - 8, y1 - 4], fill=(60, 120, 60), width=2)
    elif s == "bridge":  # arc bridge over water, burst above
        d.line([x0 + 6, y1 - 6, x1 - 6, y1 - 6], fill=(60, 110, 180), width=4)
        d.arc([x0 + 10, y0 + 8, x1 - 10, y1 + 6], 180, 360, fill=RED, width=3)
        for i in range(4):
            px = x0 + 18 + i * 16
            d.line([px, y0 + 14, px, y1 - 7], fill=INK, width=1)
        d.ellipse([cx - 4, y0 + 2, cx + 4, y0 + 10], fill=(240, 180, 40))
    elif s == "missiles":  # two trails met by bursts
        d.line([x0 + 10, y1 - 4, cx - 6, y0 + 8], fill=INK, width=2)
        d.line([x1 - 10, y1 - 4, cx + 6, y0 + 8], fill=INK, width=2)
        for bx, by in [(cx - 8, y0 + 8), (cx + 8, y0 + 8)]:
            d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(240, 180, 40),
                      outline=RED, width=1)
        d.polygon([(x0 + 30, y1 - 2), (x0 + 38, y1 - 12), (x0 + 46, y1 - 2)],
                  fill=(90, 90, 90))
    elif s == "markets":  # rising line chart
        pts = [(x0 + 8, y1 - 8), (x0 + 26, y1 - 14), (x0 + 42, y1 - 10),
               (x0 + 58, y1 - 18), (x0 + 76, y0 + 6)]
        d.line(pts, fill=(30, 120, 60), width=3)
        d.ellipse([pts[-1][0] - 3, pts[-1][1] - 3, pts[-1][0] + 3, pts[-1][1] + 3],
                  fill=RED)
        d.line([x0 + 8, y1 - 5, x1 - 8, y1 - 5], fill=GREY, width=1)
    elif s == "games":  # game controller
        d.rounded_rectangle([x0 + 14, y0 + 7, x1 - 14, y1 - 5], radius=8,
                            fill=(60, 60, 90), outline=INK)
        d.ellipse([x0 + 22, cy - 2, x0 + 28, cy + 4], fill=(250, 250, 250))
        d.ellipse([x1 - 28, cy - 2, x1 - 22, cy + 4], fill=(240, 180, 40))
        d.ellipse([x1 - 36, cy - 6, x1 - 30, cy], fill=(240, 80, 80))
    elif s == "cyclone":  # spiral
        for r in (12, 8, 4):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=NAVY, width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
        for i in range(3):
            d.line([x0 + 12 + i * 8, y1 - 3, x0 + 10 + i * 8, y1 - 8],
                   fill=(60, 110, 180), width=2)
    elif s == "exam":  # desk, paper, pencil
        d.rectangle([x0 + 10, y1 - 8, x1 - 10, y1 - 4], fill=(150, 110, 70))
        d.rectangle([cx - 14, y0 + 5, cx + 6, y0 + 20], fill=(255, 255, 255),
                    outline=INK)
        d.line([cx - 10, y0 + 9, cx + 2, y0 + 9], fill=GREY, width=1)
        d.line([cx - 10, y0 + 13, cx + 2, y0 + 13], fill=GREY, width=1)
        d.line([cx + 12, y0 + 4, cx + 22, y0 + 18], fill=(230, 170, 40), width=3)
        d.ellipse([x1 - 18, y0 + 3, x1 - 8, y0 + 13], outline=INK, width=2)
    elif s == "economy":  # falling bars
        heights = [16, 13, 9, 6]
        for i, hh in enumerate(heights):
            bx = x0 + 14 + i * 18
            d.rectangle([bx, y1 - 4 - hh, bx + 11, y1 - 4], fill=(178, 60, 40))
        d.line([x0 + 8, y0 + 6, x1 - 8, y1 - 6], fill=INK, width=2)
    elif s == "law":  # gavel + document
        d.rectangle([x0 + 10, y0 + 6, x0 + 34, y0 + 20], fill=(255, 255, 255),
                    outline=INK)
        d.line([x0 + 14, y0 + 10, x0 + 30, y0 + 10], fill=GREY, width=1)
        d.line([x0 + 14, y0 + 14, x0 + 30, y0 + 14], fill=GREY, width=1)
        d.ellipse([x0 + 24, y0 + 16, x0 + 32, y1 - 4], fill=RED)
        d.rectangle([x1 - 30, y0 + 8, x1 - 12, y0 + 13], fill=(120, 90, 60))
        d.line([x1 - 21, y0 + 13, x1 - 21, y0 + 22], fill=(120, 90, 60), width=3)
    elif s == "road":  # road with dashed yellow line and gate
        d.rectangle([x0, cy - 5, x1, cy + 5], fill=(80, 80, 80))
        for i in range(6):
            dx = x0 + 6 + i * 15
            d.line([dx, cy, dx + 8, cy], fill=(240, 200, 40), width=2)
        d.rectangle([cx - 2, y0 + 3, cx + 2, cy - 5], fill=RED)
        d.rectangle([cx - 8, y0 + 3, cx + 8, y0 + 6], fill=RED)
    elif s == "march":  # crowd heads + placard
        for i, (hx, hy) in enumerate([(x0 + 16, cy + 2), (x0 + 34, cy - 1),
                                      (x0 + 52, cy + 2), (x0 + 70, cy)]):
            d.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], fill=(210, 170, 140),
                      outline=INK)
            d.arc([hx - 8, hy + 4, hx + 8, hy + 12], 180, 360, fill=INK, width=2)
        d.rectangle([x1 - 26, y0 + 3, x1 - 8, y0 + 12], fill=(255, 255, 255),
                    outline=RED)
        d.line([x1 - 17, y0 + 12, x1 - 17, y0 + 20], fill=INK, width=1)
    elif s == "plane":  # aeroplane silhouette
        d.polygon([(x0 + 8, cy), (x0 + 30, cy - 7), (x1 - 16, cy - 5),
                   (x1 - 8, cy - 2), (x1 - 16, cy + 1), (x0 + 30, cy + 4)],
                  fill=NAVY)
        d.polygon([(cx - 4, cy - 5), (cx + 8, cy - 14), (cx + 12, cy - 5)],
                  fill=NAVY)
        d.line([x0 + 8, y1 - 5, x1 - 8, y1 - 5], fill=GREY, width=1)
        for i in range(3):
            d.ellipse([x0 + 10 + i * 12, y1 - 9, x0 + 14 + i * 12, y1 - 5],
                      fill=GREY)
    elif s == "vote":  # ballot box with tick
        d.rectangle([cx - 14, y0 + 8, cx + 14, y1 - 4], fill=(255, 255, 255),
                    outline=INK)
        d.rectangle([cx - 6, y0 + 4, cx + 6, y0 + 9], fill=INK)
        d.line([cx - 9, cy + 1, cx - 2, cy + 7, cx + 10, cy - 6], fill=(30, 120, 60),
               width=3)
        d.line([x0 + 8, y1 - 3, x1 - 8, y1 - 3], fill=GREY, width=1)


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- tally, computed from the story data
    counts = {r: 0 for r in REGION_ORDER}
    for c in CARDS:
        counts[c["region"]] += 1
    for _, _, r, _ in BRIEFS:
        counts[r] += 1
    assert sum(counts.values()) == 50, counts
    assert counts == {"EUROPE": 12, "MIDDLE EAST": 7, "ASIA": 9, "AFRICA": 8,
                      "AMERICAS": 7, "OCEANIA": 4, "WORLD": 3}, counts

    # --- masthead
    d.rectangle([0, 0, W, 4], fill=INK)
    f_mast = font(SERIF_B, 44)
    mast = "Thursday 19 November 2026"
    mw = d.textlength(mast, font=f_mast)
    d.text(((W - mw) / 2, 8), mast, font=f_mast, fill=INK)
    f_deck = font(SERIF, 15)
    deck = ("Trump, Xi and Putin meet in Shenzhen  \u00b7  World Court: Myanmar committed "
            "genocide  \u00b7  Anthropic's $81.3bn debut")
    dw = d.textlength(deck, font=f_deck)
    d.text(((W - dw) / 2, 58), deck, font=f_deck, fill=RED)
    d.line([MARGIN, 78, W - MARGIN, 78], fill=INK, width=2)

    # --- count strip
    d.rectangle([MARGIN, 84, W - MARGIN, 106], fill=NAVY)
    f_strip = font(SANS_B, 13)
    strip = "50 STORIES  \u00b7  7 REGIONS  \u00b7  ALL FROM THURSDAY 19 NOVEMBER 2026"
    sw = d.textlength(strip, font=f_strip)
    d.text(((W - sw) / 2, 89), strip, font=f_strip, fill=(255, 255, 255))

    # --- region tally bar (computed)
    f_tally = font(SANS_B, 11)
    tally = "   \u00b7   ".join("%s %d" % (r, counts[r]) for r in REGION_ORDER)
    tw = d.textlength(tally, font=f_tally)
    d.text(((W - tw) / 2, 112), tally, font=f_tally, fill=INK)

    # --- cards: 3 columns x 5 rows
    cw = (W - 2 * MARGIN - 2 * 10) // 3
    ch, gap = 92, 4
    y_top = 124
    f_kick = font(SANS_B, 8)
    for i, card in enumerate(CARDS):
        row, col = divmod(i, 3)
        x = MARGIN + col * (cw + 10)
        y = y_top + row * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], outline=LIGHT_LINE, width=1)
        draw_scene(d, (x + 1, y + 1, x + cw - 1, y + 27), card)
        # number badge
        bx, by = x + 13, y + 14
        d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=RED, outline=(255, 255, 255), width=1)
        f_num = font(SANS_B, 11)
        ns = str(card["n"])
        d.text((bx - d.textlength(ns, font=f_num) / 2, by - 8), ns, font=f_num,
               fill=(255, 255, 255))
        # kicker
        d.text((x + 6, y + 30), "%s \u00b7 %s" % (card["place"], card["beat"]),
               font=f_kick, fill=RED)
        # headline, max 2 lines
        lines, f_head = fit_lines(d, card["head"], font(SERIF_B, 12), cw - 12, 2)
        hy = y + 41
        for ln in lines:
            d.text((x + 6, hy), ln, font=f_head, fill=INK)
            hy += 13
        # sub-deck, max 2 lines
        slines, f_sub = fit_lines(d, card["sub"] + " \u2014 " + card["src"],
                                  font(SANS, 9), cw - 12, 2)
        if len(slines) > 2:
            print("WARN card", card["n"], "sub needs", len(slines), "lines")
        sy = y + 67
        for ln in slines[:2]:
            d.text((x + 6, sy), ln, font=f_sub, fill=(60, 58, 52))
            sy += 10

    # --- by the numbers strip (label lives inside the strip)
    ny = 604
    d.rectangle([MARGIN, ny, W - MARGIN, ny + 24], fill=INK)
    lab_x = MARGIN + 8
    f_nlab = font(SANS_B, 8)
    d.text((lab_x, ny + 4), "BY THE", font=f_nlab, fill=(255, 220, 120))
    d.text((lab_x, ny + 13), "NUMBERS", font=f_nlab, fill=(255, 220, 120))
    x0n = MARGIN + 92
    cell_w = (W - MARGIN - x0n) // 6
    f_big = font(SERIF_B, 14)
    f_lab = font(SANS, 7)
    for i, (fig, lab) in enumerate(NUMBERS):
        cx = x0n + i * cell_w + cell_w // 2
        fw = d.textlength(fig, font=f_big)
        d.text((cx - fw / 2, ny + 2), fig, font=f_big, fill=(255, 255, 255))
        lw = d.textlength(lab, font=f_lab)
        d.text((cx - lw / 2, ny + 17), lab, font=f_lab, fill=(200, 198, 190))
        if i:
            d.line([x0n + i * cell_w, ny + 4, x0n + i * cell_w, ny + 20],
                   fill=(90, 88, 80), width=1)

    # --- map + date check
    my = 632
    mh = 176
    map_x, map_w = MARGIN, 616
    d.rectangle([map_x, my, map_x + map_w, my + mh], outline=INK, width=1)
    d.rectangle([map_x, my, map_x + map_w, my + 16], fill=NAVY)
    d.text((map_x + 6, my + 3), "WHERE IT HAPPENED  \u2014  numbered pins are the 15 cards; dots are the briefs",
           font=font(SANS_B, 9), fill=(255, 255, 255))
    sea = (214, 228, 238)
    d.rectangle([map_x + 1, my + 17, map_x + map_w - 1, my + mh - 1], fill=sea)
    lat_top, lat_bot = 72.0, -46.0

    def proj(lon, lat):
        px = map_x + 1 + (lon + 180.0) / 360.0 * (map_w - 2)
        py = my + 17 + (lat_top - lat) / (lat_top - lat_bot) * (mh - 18)
        return px, py

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(226, 222, 205),
                  outline=(120, 116, 100))
    for lon, lat in BRIEF_DOTS:
        px, py = proj(lon, lat)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(90, 88, 84))
    f_pin = font(SANS_B, 8)
    for card in CARDS:
        px, py = proj(*card["pin"])
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        ns = str(card["n"])
        d.text((px - d.textlength(ns, font=f_pin) / 2, py - 6), ns, font=f_pin,
               fill=(255, 255, 255))

    # --- date check box
    dx = map_x + map_w + 10
    dw_ = W - MARGIN - dx
    d.rectangle([dx, my, dx + dw_, my + mh], outline=RED, width=2)
    d.text((dx + 6, my + 4), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    d.text((dx + 6, my + 18), "First reported on other days, so NOT on this page:",
           font=font(SANS_B, 8), fill=INK)
    f_dc = font(SANS, 8)
    yy = my + 30
    for day, text in DATE_CHECK:
        para = day + ": " + text
        for ln in wrap(d, para, f_dc, dw_ - 12):
            d.text((dx + 6, yy), ln, font=f_dc, fill=(50, 48, 44))
            yy += 9
        yy += 1

    # --- briefs
    by = 814
    d.text((MARGIN, by), "ALSO ON THURSDAY 19 NOVEMBER", font=font(SANS_B, 10), fill=INK)
    d.line([MARGIN, by + 13, W - MARGIN, by + 13], fill=INK, width=1)
    col_w = (W - 2 * MARGIN - 20) // 2
    rows = 18
    row_h = 9
    for j, (n, place, region, text) in enumerate(BRIEFS):
        col, r = divmod(j, rows)
        bx = MARGIN + col * (col_w + 20)
        yy = by + 17 + r * row_h
        lead = "%d %s \u2014 " % (n, place)
        f_lead, f_body = font(SANS_B, 9), font(SANS, 9)
        while (d.textlength(lead, font=f_lead)
               + d.textlength(text, font=f_body) > col_w and f_body.size > 8):
            f_lead = font(SANS_B, f_lead.size - 1)
            f_body = font(SANS, f_body.size - 1)
        if d.textlength(lead, font=f_lead) + d.textlength(text, font=f_body) > col_w:
            print("WARN brief", n, "too wide")
        d.text((bx, yy), lead, font=f_lead, fill=INK)
        d.text((bx + d.textlength(lead, font=f_lead), yy), text, font=f_body,
               fill=(50, 48, 44))

    # --- footer
    fy = 997
    d.line([MARGIN, fy - 4, W - MARGIN, fy - 4], fill=INK, width=1)
    f_foot = font(SANS, 9)
    foot = ("Every story on this page happened, or was first reported, on Thursday 19 November 2026. "
            "Disputed claims are attributed, not stated as fact. Pictures and map: original, drawn in code.")
    d.text((MARGIN, fy), foot, font=f_foot, fill=INK)
    foot2 = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Euronews, ABC, RNZ, IMD, ABS, SARB, AIU, FIFA."
    d.text((MARGIN, fy + 12), foot2, font=f_foot, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
