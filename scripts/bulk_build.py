#!/usr/bin/env python3
"""
Bulk build — generate ~100 posts per brand with rotating content types, angles,
and real content pulled from Vista CSVs + brand-world docs.

OpenAI gpt-image-2 1024x1280 tier only (~$0.04/image, ~$4 per 100).
Parallel dispatch via ThreadPoolExecutor (default 8 concurrent).

Usage:
    python3 scripts/bulk_build.py --brand blue_mezcal --count 100
    python3 scripts/bulk_build.py --brand jackson_house --count 100
    python3 scripts/bulk_build.py --brand el_azteca --count 100
    python3 scripts/bulk_build.py --brand all --count 100   # does all three
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import pathlib
import random
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNER = ROOT / "scripts" / "nano_banana_runner.py"


# ============================================================
# ASSET INVENTORIES (pulled from real CSVs + brand profiles)
# ============================================================

BM_FOOD_IMAGES = [
    ("B-44", "Raw Oysters", "Mignonette. Lemon. Cold as promised."),
    ("B-47", "Raw Oysters", "Straight from the ice."),
    ("B-56", "Seafood Parillada", "Grill. Smoke. Share."),
    ("B-57", "Seafood Parillada", "Surf, turf, fire."),
    ("B-62", "Guacamole con Chicharrón", "Avocado. Chicharrón. Lime."),
    ("B-70", "Guacamole con Crudités", "Crisp. Cool. Shared."),
    ("B-73", "Guacamole con Chicharrón", "Made to order."),
]

BM_COCKTAIL_IMAGES = [
    ("B-3", "Cucumber Margarita", "Black salt rim. Cucumber crown. Cool and dangerous."),
    ("B-1", "Cucumber Margarita", "Impossible to have one."),
    ("B-7", "Spicy Margarita", "Smoke, citrus, slow."),
    ("B-8", "Spicy Margarita", "A slow fire."),
    ("B-35", "HOMBRE Old Fashioned", "Bourbon. Smoke. A handshake."),
    ("B-36", "HOMBRE Old Fashioned", "One more. You'll survive."),
    ("B-37", "HOMBRE Old Fashioned", "Cool and dangerous."),
]

BM_DICHOS = [
    ("Para todo mal, mezcal;", "para todo bien, también."),
    ("Smoke, citrus, slow.", "Blue Mezcal · Middletown DE"),
    ("One more. You'll survive.", "Cocktail Hour · Blue Mezcal"),
    ("Impossible to have one.", "Blue Mezcal · Middletown DE"),
    ("Cool and dangerous.", "Blue Mezcal · Middletown DE"),
]

BM_FLYERS = [
    ("Mezcal Monday.", "Half-off flights · 5–8pm · Espadín · Tobalá · Cuishe"),
    ("Happy Hour.", "Monday–Thursday · 5–7pm · Half-off mezcal flights"),
    ("Día de Muertos.", "Nov 1–2 · Ofrenda Menu · Limited Seatings"),
    ("Agave Tasting.", "Saturdays · 7pm · Tobalá · Espadín · Cuishe"),
    ("Brunch.", "Sundays · 11am–3pm · Bottomless Mimosas"),
    ("Chef's Table.", "Fridays · 7:30pm · Six courses · Reserve ahead"),
]

BM_CULTURAL = [
    ("On the slow things.", "Mezcal is not hurried. Neither are we."),
    ("On agave.", "Seven years in the ground. One moment in the glass."),
    ("On smoke.", "The fire is part of the flavor."),
    ("On the copita.", "Small glass. Big patience."),
]

BM_UTILITY = [
    ("Now On DoorDash.", "Yes, even the guac."),
    ("Reservations Open.", "Book ahead. Walk-ins welcome."),
    ("Closed Today.", "Back tomorrow at 5pm."),
    ("New Hours.", "Tuesday–Sunday · 5pm–11pm"),
]

BM_LOCATION = [
    ("Find us.", "826 Kohl Ave · Middletown, DE"),
    ("You are here.", "826 Kohl Ave · Middletown, DE"),
]

BM_MENU_HIGHLIGHTS = [
    ("New menu.", "Raw Oysters · Seafood Parillada · Guacamole con Chicharrón · HOMBRE Old Fashioned · Mezcal Negroni"),
    ("This week.", "Chef's Tasting · Agave Flights · Brunch Sunday"),
]

BM_CAMPAIGN_MASTHEADS = [
    ("New Menu. New Era.", "May 5 · Blue Mezcal"),
    ("Summer.", "New Cocktails. New Dishes. One Address."),
]

# -----

JH_FOOD_IMAGES = [
    ("T-72", "Chimichurri Steak", "Chimichurri. Charred rim. Mid-rare."),
    ("T-73", "Chimichurri Steak", "Heritage cut. Mid-rare by default."),
    ("T-87", "Orecchiette", "Hand-rolled. Sausage. Broccoli rabe."),
    ("T-88", "Orecchiette", "Hand-rolled pasta, the old way."),
    ("T-61", "Lobster Roll", "Toasted brioche. Cream sauce. Chives."),
    ("T-62", "Lobster Roll", "New on the menu. Already a favorite."),
    ("T-70", "Elote Burger", "We're not going to explain this one."),
    ("T-67", "Elote Burger", "Just order it."),
    ("T-64", "Summer Scallops", "Charred, citrus, clean."),
]

JH_COCKTAILS_NO_PHOTO = [
    ("Heard's The Last Word.", "(It usually is.)"),
    ("Bite The Bulleit.", "Bourbon. Bite. Bulleit."),
    ("Grapefruitty Tuti.", "Care free, spirit free."),
    ("La Ultima.", "The last word. In Spanish."),
    ("Spritz From Switz.", "Alpine lift. Brooklyn pour."),
    ("One In A Melon.", "(She said it, not us.)"),
    ("Lychee Spritz.", "Crisp. Floral. Cold."),
    ("Toast Of The Town.", "Raise a glass."),
    ("Nada De Mango.", "Everything to say."),
    ("Key Lime Mule.", "Citrus. Ginger. Kick."),
]

JH_DICHOS = [
    ("You already know.", "Jackson House · Middletown Delaware"),
    ("Some things don't need to be complicated.", "Jackson House · 17 Wood St"),
    ("Dry-aged 28 days.", "That's the whole sentence."),
    ("Warm out of the oven.", "Butter melts on contact."),
    ("Reserve your table.", "Jackson House · Middletown Delaware"),
]

JH_FLYERS = [
    ("Wine Dinner.", "Five courses. Five wines. One evening."),
    ("Private Dining.", "Parties of 10–24 · Reserve ahead"),
    ("Whiskey Flight Night.", "Bourbon · Rye · Single Malt"),
    ("Brunch.", "Saturdays & Sundays · 10am–2pm"),
    ("Steak Night.", "Bison Ribeye · Wagyu · Dry-aged"),
    ("Live Jazz.", "Thursdays · 7pm–10pm"),
]

JH_CULTURAL = [
    ("On patience.", "Some things are worth the wait."),
    ("On technique.", "The right temperature is a form of respect."),
    ("On heritage.", "The classics for a reason."),
    ("On hospitality.", "The pour. The welcome. The detail."),
    ("On quality.", "Everything on the plate earned its place."),
]

JH_UTILITY = [
    ("Now on DoorDash.", "The whole menu. Delivered."),
    ("Reservations Open.", "Book ahead · OpenTable"),
    ("Closed Christmas.", "Back the 26th with steak."),
    ("Patio Open.", "Weather permitting · First-come"),
]

JH_LOCATION = [
    ("Find us.", "17 Wood St · Middletown, DE"),
    ("Worth the drive.", "17 Wood St · Middletown, DE"),
]

JH_MENU_HIGHLIGHTS = [
    ("This week.", "Chimichurri Steak · Orecchiette · Lobster Roll · Summer Scallops"),
    ("Chef's picks.", "Bison Ribeye · Passionfruit Salmon · Elote Burger"),
    ("The bar.", "Heard's The Last Word · Bite The Bulleit · Grapefruitty Tuti"),
    ("On the menu.", "Seasonal. Heritage. Handcrafted."),
]

JH_CAMPAIGN_MASTHEADS = [
    ("New Menu.", "Chef-driven. Heritage-rooted. Now serving."),
    ("Delaware Today.", "Best New Restaurant 2025."),
    ("Spring Menu.", "Now on the pass."),
    ("Anniversary.", "One year. Many thanks."),
    ("Private Dining.", "Now booking · 17 Wood St · Middletown DE"),
    ("Reservations Open.", "Book ahead · link in bio"),
    ("Summer.", "Patio open. Menu live."),
    ("Chef's Table.", "Six courses. Fridays only."),
    ("Holiday Menu.", "Reserve ahead · Limited seatings"),
    ("Gift Cards.", "Jackson House · available at the host stand"),
]

# -----

AZ_FOOD_IMAGES = [
    ("AZ-8", "Guacamole, but make it octopus.", "Octopus. Avocado. House chips."),
    ("AZ-9", "Guacamole, but make it octopus.", "Not your average appetizer."),
    ("AZ-22", "Cóctel de Camarón", "Shrimp. Salsa. Cold."),
    ("AZ-23", "Cóctel de Camarón", "Classic for a reason."),
    ("AZ-37", "Whole Fried Tilapia", "Whole fish. Whole flavor."),
    ("AZ-49", "Carne Asada", "Grilled. Charred. De la casa."),
    ("AZ-50", "Carne Asada", "Classic for a reason."),
    ("AZ-51", "Carne Asada", "Grilled over fire."),
    ("AZ-68", "Fajita Baked Potato", "We don't do things halfway."),
    ("AZ-64", "Elote", "Street corn. Classic."),
    ("AZ-80", "Steak and Enchilada Combo", "Pick your poison."),
    ("AZ-86", "Huevos Rancheros", "Brunch done right."),
    ("AZ-89", "Chocolate Lava Cake", "Warm center."),
    ("AZ-91", "Churros", "Cinnamon. Sugar. Crisp."),
    ("AZ-97", "Flan", "De la abuela."),
    ("AZ-102", "Fried Ice Cream", "Cold inside. Warm outside."),
    ("AZ-32", "Tilapia a la Mexicana", "Fresh fish. Fresh salsa."),
]

AZ_DRINKS = [
    ("AZ-47", "Cocktail hour.", "Margaritas · Micheladas · Pick your poison"),
    ("AZ-73", "Pick your poison.", "Happy Hour · All week"),
]

AZ_DICHOS = [
    ("De la casa.", "El Azteca · Delaware · Rehoboth"),
    ("Auténtico.", "El Azteca · Delaware · Rehoboth"),
    ("Classic for a reason.", "El Azteca"),
    ("Con gusto.", "El Azteca · Delaware · Rehoboth"),
    ("La comida es amor.", "El Azteca"),
]

AZ_FLYERS = [
    ("Taco Tuesday.", "Since forever · Every Tuesday · $2 tacos"),
    ("Happy Hour.", "Monday–Friday · 4–6pm · Margaritas · Micheladas"),
    ("Día de Muertos.", "Nov 1–2 · Altar Menu"),
    ("Día de la Independencia.", "Sept 16 · Menu Especial"),
    ("Sunday Brunch.", "11am–3pm · Family Style"),
    ("Cumbia Night.", "Fridays · Live music · 8pm"),
    ("Mother's Day.", "Reserve ahead · Family menu"),
    ("Cinco de Mayo.", "Live music · Menú especial"),
    ("Margarita Monday.", "Half-off all house margs"),
    ("Kids Eat Free.", "Sunday nights · One kid per adult"),
]

AZ_CULTURAL = [
    ("La sobremesa.", "The moment after the meal. Stay longer."),
    ("De la abuela.", "Recipes passed down. Hands that know."),
    ("El maíz es todo.", "Corn is everything. Start there."),
    ("La familia.", "The table is always bigger than it looks."),
    ("Hecho a mano.", "Tortillas pressed fresh. Every day."),
]

AZ_UTILITY = [
    ("Ahora en DoorDash.", "Now on DoorDash."),
    ("Abierto.", "Mon–Sun · 11am–10pm"),
    ("Reservaciones.", "Book ahead · link in bio"),
    ("Closed Christmas Day.", "Back December 26"),
    ("Mother's Day.", "Reservaciones abiertas · Book ahead"),
]

AZ_LOCATION = [
    ("Estamos aquí.", "Delaware · Rehoboth"),
    ("Find us.", "Two locations · Delaware · Rehoboth"),
    ("Delaware + Rehoboth.", "Two tables · One family"),
]

AZ_MENU_HIGHLIGHTS = [
    ("The menu.", "Guacamole Octopus · Carne Asada · Cóctel de Camarón · Whole Fried Tilapia"),
    ("Del bar.", "Margaritas · Micheladas · Aguas Frescas"),
    ("Postres.", "Flan · Churros · Chocolate Lava Cake · Tres Leches"),
    ("Brunch.", "Huevos Rancheros · Chilaquiles · Breakfast Enchiladas"),
    ("Favorites.", "Tacos · Enchiladas · Fajitas · Burritos"),
]

AZ_CAMPAIGN_MASTHEADS = [
    ("Bienvenidos.", "El Azteca · Delaware + Rehoboth"),
    ("El menú.", "Clásicos · Favoritos · De la casa"),
    ("Family Style.", "Always room at the table."),
    ("Abrimos a las 11.", "Every single day."),
    ("Taco Tuesday.", "Since forever · Every Tuesday"),
]


# ============================================================
# ANGLE TEMPLATES (rotation keys)
# ============================================================

# Each angle is an atomic visual-direction prompt. Per content type, 3 angles
# rotate so no content type looks repetitive.

ANGLES_BM = {
    "food_hero": [
        "GHIA CLEAN-GROUND EDITORIAL. Bone-cream ground (#F3ECD8) divided vertically: photo RIGHT 55% at full scale, cream field LEFT 45%. Left carries: refined GT Sectra italic caps in cobalt (#1E3A8A) at 130-160px stacked, small-caps Söhne support line in cobalt 26-30px, hairline cobalt rule + venue tag '826 KOHL AVE · MIDDLETOWN DE' small-caps at bottom. 5-7% paper-grain on cream. Cobalt + cream only.",
        "DRAMATIC CLOSE-CROP + POETIC LINE. Photo fills 65-70% canvas cropped tight on a hero detail of the dish (garnish, texture, sauce pool). Negative space upper-right 30% carries a poetic cobalt italic Canela line at 80-110px right-aligned, one line drawn from the support copy. Small-caps Söhne subject subhead below in cobalt 28-32px. Hairline cobalt rule + tiny venue dateline at bottom. Bone-cream ground for negative space zone with 5% tonal gradient.",
        "VERTICAL COBALT STRIP. Photo fills RIGHT 70% full-scale. LEFT 30% solid cobalt (#1E3A8A) with 8-12% tonal gradient. Strip carries GT Sectra italic caps in warm cream stacked vertically at 100-130px, small-caps Söhne support below, hairline cream rule + tiny address at bottom of strip. No marigold accent. Cobalt + cream.",
    ],
    "cocktail_hero": [
        "FRENCHETTE CUT-OUT ON CREAM. Bone-cream ground #F3ECD8 with 10% paper-gradient. Cocktail glass silhouetted as clean cut-out in lower 55% canvas. Top 35%: mixed-weight script+serif lockup in cobalt — connecting word in Canela italic 90-110px, power word in GT Sectra caps 1.4x scale, stacked. Hairline cobalt rule. Small-caps support line in cobalt. Tiny '826 KOHL AVE · MIDDLETOWN DE' dateline at bottom. One-color cobalt + cream.",
        "VOICE-FIRST TYPE HERO. Bone-cream ground with 8-10% paper-gradient. Upper 55% canvas: OVERSIZED cobalt italic Canela / GT Sectra headline 160-200px stacked 2-3 lines tight leading. Lower 40%: cocktail glass photo cut-out center-lower ~30% canvas height. Small-caps Söhne support in cobalt. Hairline rule + dateline bottom. Voice is hero, drink is receipt. Cobalt + cream only.",
        "DRAMATIC RIM CLOSE-CROP. Photo cropped extreme-tight on the rim + garnish (salt rim, cucumber crown, citrus twist). Upper-right 30% negative-space zone carries a cobalt italic Canela one-line poetic mood-line at 90-120px, right-aligned. Small-caps subject subhead below. Hairline rule + dateline at bottom. 5% tonal gradient on the cream negative-space zone.",
    ],
    "typography_first": [
        "BRUTALIST DICHO WALLPAPER. Bone-cream ground 8% paper-gradient. Spanish phrase repeats as tight wallpaper pattern across canvas, rows stacked, each row offset horizontally ~90px zigzag, cobalt GT Sectra italic caps 85-110px tight leading 1.05. Center: rectangular KNOCKOUT WINDOW at 65% width × 30% height — cream field punching through wallpaper. Inside window: small italic Canela translation/continuation line 42-50px, hairline cobalt rule, tiny 'BLUE MEZCAL · MIDDLETOWN DE' small-caps. 5-8% linen paper-grain.",
        "HAND-PAINTED BRUSH WORDMARK. Bone-cream ground 10-12% paper-gradient. Single word dominates canvas at 480-560px, rendered as HAND-PAINTED BRUSH STROKE in cobalt — visible brush texture, bleed edges, intentional paint splatters, calligrapher's one-shot feel. One tiny marigold paint splatter near final period. Below at 40% height: italic Canela in cobalt 42-50px one line. Hairline cobalt rule + small-caps dateline.",
        "ITALIC SERIF MASTHEAD ON CREAM. Bone-cream ground 10% gradient. Oversized italic Canela or GT Sectra serif in cobalt dominating upper 60% at 160-220px, stacked 2-3 lines tight leading 1.0, one word italicized for emphasis. Hairline cobalt rule beneath. Small-caps support line in cobalt 32-38px. Bottom dateline + hairline rule. 5% linen paper-grain. Pure editorial restraint.",
    ],
    "flyer": [
        "HERITAGE POSTER NOCTURNAL. Charred black ground #0B0B0B 10% tonal gradient. TOP 30%: masthead in brass-foil gradient serif caps Farnham Display 180-230px stacked 2 lines tight tracking, hairline brass rule beneath. MIDDLE 40%: single hand-drawn cobalt or brass COPITA silhouette centered, line-art only, hairline underline, 3 small smoke curls. LOWER 25%: small-caps warm cream support info-lockup at 30-36px tracked wide, hairline brass rule separators. BOTTOM strip: tiny cream dateline small-caps wide-tracked. 5-7% film grain.",
        "EDITORIAL EVENT ON CREAM. Bone-cream ground 10% paper-gradient. TOP 25%: event name in cobalt GT Sectra italic caps 170-210px stacked. Hairline cobalt rule. MIDDLE 45%: a hand-drawn editorial illustration (copita, agave leaf, or cocktail stirrer) in cobalt hairline ink centered. LOWER 25%: small-caps cobalt info-lockup 30-36px stacked 2-3 lines, hairline rules between. BOTTOM: hairline rule + tiny address dateline. 5-7% linen paper-grain.",
        "BOLD COLOR-BLOCK POSTER. Cobalt ground #1E3A8A 10% tonal gradient filling upper 60% canvas, bone-cream field filling lower 40%. Cobalt upper: event name in warm-cream Canela italic caps 180-220px stacked tight tracking. Cream lower: small-caps cobalt info at 32-38px stacked, hairline rules, dateline at bottom. 5-7% paper-grain.",
    ],
    "carousel_masthead": [
        "OVERSIZED ITALIC MASTHEAD. Bone-cream ground 8% gradient. Full-canvas oversized italic Canela serif in cobalt 240-300px stacked 2 lines tight leading 1.0, center-aligned. Hairline cobalt rule beneath at 40% canvas width. Small-caps support line in cobalt at 30-36px tracked wide. Tiny 'BLUE MEZCAL · SLIDE TO SEE MORE' small-caps at very bottom. Pure editorial restraint.",
        "COBALT FIELD + WARM CREAM TYPE. Full-canvas cobalt #1E3A8A with 10% tonal gradient. Center: warm cream GT Sectra italic serif 220-280px stacked 2 lines, tight tracking. Warm cream hairline rule beneath. Small-caps support in warm cream. 'SLIDE' arrow hint at right edge. 5% noise grain overlay.",
        "TYPE STACK WITH HAIRLINE GRID. Bone-cream ground 5% gradient. Editorial grid of hairlines: thin cobalt rule at top, middle, bottom. Between them: title in Canela italic caps, subtitle in small-caps Söhne. All cobalt. Hairline horizontal rules create an editorial table-of-contents feel. Carousel intent — 'SWIPE →' small-caps at bottom-right.",
    ],
    "utility": [
        "UTILITY POSTER EDITORIAL CREAM. Bone-cream ground 8% gradient. Upper 55%: headline in cobalt italic Canela caps 160-200px stacked. Hairline cobalt rule beneath. Middle 25%: italic serif pullquote 60-70px in cobalt. Lower 20%: small-caps cobalt tracked wide one line + hairline rule + tiny italic CTA. NO photo. Designed, not plain.",
        "UTILITY POSTER COBALT GROUND. Cobalt #1E3A8A 10% tonal gradient. Warm-cream italic Canela caps headline 180-220px stacked, hairline cream rule beneath. Warm-cream small-caps support line. Hairline rule + tiny address at bottom. Editorial, no degradation.",
        "UTILITY SPLIT FIELD. Top 50% cobalt field, bottom 50% cream field. Cobalt: warm-cream headline italic serif. Cream: cobalt small-caps support + hairline rule + dateline. Clean split, editorial.",
    ],
    "multi_dish_showcase": [
        "MULTI-DISH CAROUSEL CARD. Bone-cream ground 8% gradient. Full-canvas typographic list — 4-5 dish names in cobalt GT Sectra italic caps at 90-110px each, stacked, hairline cobalt rules between, each separated. Title at top 'This Week.' in cobalt italic 170-210px. Small-caps dateline at bottom + hairline rule. 5-7% linen paper-grain.",
        "GRID OF DISH NAMES. Bone-cream ground 5% gradient. 2×3 editorial grid of dish titles — each cell carries a dish name in cobalt italic Canela at 70-90px with a small-caps subtitle beneath in Söhne. Hairline cobalt rules between cells. Title at top in italic Canela + support below. Bottom dateline.",
        "TICKER-TAPE REPEATING DISH NAMES. Bone-cream ground. A horizontal RUNNING banner across the middle of canvas listing dishes separated by hairline dots: 'Raw Oysters · Seafood Parillada · Guacamole · HOMBRE Old Fashioned ·' repeating. Above: masthead italic caps title in cobalt. Below: small-caps date + address. Editorial ticker-banner feel.",
    ],
    "cultural": [
        "ETCHED EDITORIAL ON CREAM. Bone-cream ground 10% paper-gradient. Top 18%: italic cobalt Canela serif headline 130-160px italic centered. Middle 50%: hand-etched pen-and-ink line-art illustration of an agave plant or mezcal still, cobalt hairline. Short body paragraph below in cobalt Söhne regular 30-34px, 3-4 lines centered. Hairline cobalt rule beneath body. Small-caps dateline bottom. 5-7% linen paper-grain. Single-ink cobalt only.",
        "BIG TYPE CULTURAL POST. Bone-cream ground 8% gradient. Upper 40%: oversized cobalt italic Canela caps headline 200-260px stacked. Middle 35%: 3-4 line body paragraph in cobalt Söhne regular 30-36px centered. Hairline cobalt rule beneath. Bottom: small-caps dateline. No illustration. Type-only cultural editorial.",
        "COBALT FIELD EDITORIAL CULTURE. Cobalt #1E3A8A ground 10% gradient. Warm cream italic Canela headline 150-190px. Warm cream body paragraph 30-34px 3-4 lines centered. Hairline cream rule beneath. Small-caps cream dateline at bottom. Paper-grain + 5-7% noise.",
    ],
    "location_map": [
        "HAND-DRAWN VECTOR MAP. Bone-cream ground with 5-8% linen paper-grain. Canvas is an illustrated map of Middletown DE rendered in cobalt (#1E3A8A) 1-2px hairline ink — streets as thin parallel lines, small hand-drawn cobalt landmarks (church, town hall, Appoquinimink River). Blue Mezcal marked with a small hand-drawn agave-plant cobalt silhouette at 826 Kohl Ave location. Script annotation 'You are here.' in cobalt italic near BM location. Top: small-caps 'BLUE MEZCAL · 826 KOHL AVE' in cobalt. Bottom: compass rose + scale bar + tiny italic Middletown DE.",
        "PAINTED AERIAL MAP. Bone-cream ground. Full-canvas painted bird's-eye gouache illustration of Middletown DE — streets as thin hand-painted cobalt lines, buildings as cobalt silhouettes, trees as marigold + agave-green brush dabs, river as pale cobalt wash. Blue Mezcal is a prominent marigold-and-cobalt building landmark slightly larger with painted glowing halo. Script 'You are here.' in cobalt italic with arrow. Top small-caps 'BLUE MEZCAL' with hairline rule. Bottom compass rose + scale + italic address. 8-10% watercolor-paper texture. Vintage travel-poster aesthetic.",
    ],
    "menu_highlight_text": [
        "TYPOGRAPHIC MENU LIST. Bone-cream ground 5-8% paper-grain. Top 15%: cobalt italic Canela title 150-190px. Middle 60%: editorial list — 5 dish names in cobalt GT Sectra italic caps stacked, each 60-80px, hairline cobalt rules between. Each dish name italic-emphasized. Bottom 20%: hairline cobalt rule + small-caps 'BLUE MEZCAL · MIDDLETOWN DE' + tiny italic dateline. Editorial menu-card discipline. Cobalt + cream only. NO photo.",
        "COBALT MENU CARD. Cobalt #1E3A8A ground 10% tonal gradient. Warm-cream italic Canela title at top. Warm-cream list of 4-5 dish names stacked tight, hairline cream rules between. Warm-cream small-caps dateline at bottom + hairline rule. Pure text menu card, NO photo, NO illustration.",
    ],
}

ANGLES_JH = {
    "food_hero": [
        "GHIA HERITAGE EDITORIAL. Warm cream ground #F2EADF divided: photo RIGHT 55% full-scale, cream field LEFT 45%. Left carries: brass-foil gradient serif caps Farnham Display 120-150px stacked 2 lines tight tracking. Beneath: small-caps Trade Gothic Condensed deep charcoal support line tracked wide 26-30px. Hairline brass rule + tiny italic Caslon 'Jackson House' 32-36px. BOTTOM LEFT: small-caps 'DELAWARE TODAY 2025 · BEST NEW RESTAURANT' 20-24px + hairline rule + '17 WOOD ST · MIDDLETOWN DE'. 5-7% paper-grain. Brass + cream + charcoal only.",
        "DRAMATIC CROP ON CHARRED BLACK. Charred-black ground #0A0A0A 10% tonal gradient. Photo cropped tight on dish detail (sear, char, garnish) fills 65% canvas lower-right. Upper-left 35% negative space carries brass-foil gradient serif caps stacked 130-160px plus small-caps warm-cream subject subhead below. Hairline brass rule + tiny dateline at bottom. 5-7% film grain. Moody.",
        "VERTICAL OXBLOOD STRIP. Photo fills RIGHT 70% full-scale. LEFT 30% solid deep oxblood #5B1A1A with 10-14% tonal gradient. Brass-foil gradient serif caps in strip at 100-130px stacked vertically fits strip width. Small-caps warm-cream support beneath. Hairline brass rule + tiny address at bottom of strip. Oxblood + brass + cream only.",
    ],
    "cocktail_selena": [
        "SELENA MASTHEAD BLACK. Charred-black ground 10% tonal gradient. Full-canvas SCRIPT+SERIF LOCKUP — connecting word in Farnham Italic 180-220px warm cream, power words in refined serif CAPS Farnham Display 260-320px brass-foil gradient + specular, stacked 2-3 lines tight tracking asymmetric centering. Brass hairline rule. Small italic Caslon pullquote warm cream 50-60px centered below. Small-caps 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' 22-26px tracked wide at bottom. 5-7% film grain.",
        "SELENA MASTHEAD OXBLOOD. Deep oxblood #5B1A1A 12% tonal gradient (warmer top, darker corners). SCRIPT+SERIF LOCKUP — italic cursive 180-220px warm cream + serif caps 280-340px brass-foil gradient, stacked slight asymmetric tilt tight tracking. Brass hairline rule + italic Caslon pullquote warm cream + small-caps dateline. 5-7% film grain.",
        "SELENA CUT-OUT CREAM. Warm cream ground 10% paper-gradient. Center 50%: hand-painted gouache cocktail glass silhouette in one-color watercolor wash (matching drink character — rose-pink for spritz, amber for bourbon, green for mule). Top: SCRIPT+SERIF lockup — italic cursive at 140-170px deep charcoal + serif caps 1.4x scale deep charcoal stacked. Italic Caslon pullquote beneath painted glass. Small-caps dateline at bottom. Painted illustration, NOT photo.",
    ],
    "typography_first": [
        "BRASS-FOIL TYPE ON BLACK. Charred-black #0A0A0A 10% tonal gradient. Centered: phrase in brass-foil gradient serif caps Farnham Display 280-340px tight tracking with specular. Brass hairline rule beneath at 40% canvas width. Small-caps 'JACKSON HOUSE · DELAWARE TODAY 2025 · BEST NEW RESTAURANT' warm cream 22-26px tracked wide + hairline rule + tiny address. 5-7% film grain.",
        "ITALIC SERIF HEADLINE CREAM. Warm cream ground 10% paper-gradient. Italic Caslon serif headline in deep charcoal 180-230px stacked 2-3 lines tight leading 1.0. Hairline charcoal rule beneath. Small-caps support in deep charcoal 30-36px tracked wide. Bottom dateline + tiny italic CTA. Editorial restraint.",
        "FOREST-GREEN FIELD. Deep forest green #1F3B2D 12% tonal gradient. Warm cream Farnham Italic headline 200-260px stacked. Brass hairline rule beneath. Small-caps warm cream support + hairline rule + tiny address bottom. 5-7% film grain.",
    ],
    "flyer": [
        "OXBLOOD EVENT POSTER. Deep oxblood #5B1A1A 12% gradient. Top 30%: brass-foil gradient serif caps Farnham Display 220-270px stacked 2 lines. Brass hairline rule. Middle 40%: hand-etched brass-foil illustration (wine glass, decanter, rosemary sprig) pen-and-ink engraving register. Lower 25%: small-caps warm cream info at 30-36px tracked wide + hairline brass rule + address + tiny italic CTA. 6-8% film grain.",
        "FOREST-GREEN HERITAGE POSTER. Deep forest green #1F3B2D 12% gradient. Top 30%: brass-foil gradient serif caps event title stacked. Brass hairline rule. Middle 40%: etched brass-foil illustration (game, seasonal produce, wine). Lower 25%: small-caps cream info + hairline brass rule + address + italic CTA. Charcoal + brass + cream only.",
        "CHARRED-BLACK EVENT POSTER. Charred-black #0A0A0A ground 10% gradient. Brass-foil event title top stacked. Engraved brass-foil ornament middle. Small-caps warm cream info-lockup bottom + hairline rules. 5-7% film grain.",
    ],
    "carousel_masthead": [
        "BRASS-FOIL TITLE ON BLACK. Charred-black #0A0A0A 10% gradient. Full-canvas brass-foil gradient serif caps Farnham Display 240-300px stacked 2 lines tight tracking + specular. Brass hairline rule beneath at 40% canvas width. Small-caps warm-cream support + SLIDE arrow hint at right edge. 5-7% film grain.",
        "CREAM EDITORIAL TITLE. Warm cream #F2EADF ground 8% gradient. Italic Caslon serif title in deep charcoal 220-280px stacked tight leading. Hairline charcoal rule + small-caps support + SWIPE arrow at right. Paper-grain texture.",
        "OXBLOOD CAROUSEL. Oxblood #5B1A1A 12% gradient. Warm-cream italic Farnham serif title 220-280px stacked. Brass hairline rule + warm-cream small-caps support. 5-7% film grain.",
    ],
    "utility": [
        "HERITAGE UTILITY POSTER BLACK. Charred-black #0A0A0A 10% gradient. Top 55%: brass-foil gradient serif caps Farnham Display 200-260px stacked 2 lines tight tracking. Brass hairline rule. Middle 25%: italic Caslon pullquote warm cream 60-70px centered. Bottom 20%: small-caps warm cream 22-26px tracked wide + hairline rule + tiny italic CTA. 5-7% film grain.",
        "HERITAGE UTILITY CREAM. Warm cream #F2EADF 8% gradient. Charcoal italic Caslon serif headline 170-210px stacked. Hairline charcoal rule. Small-caps support. Tiny italic address + CTA at bottom. Paper-grain.",
        "OXBLOOD UTILITY. Oxblood #5B1A1A 12% gradient. Warm cream italic Farnham headline stacked. Brass hairline rule. Warm-cream small-caps support + address + CTA. Film grain.",
    ],
    "multi_dish_showcase": [
        "HERITAGE MENU LIST BLACK. Charred-black ground. Top 15%: warm-cream italic Farnham title 160-200px. Middle 60%: editorial list of 4-5 dish names in brass-foil gradient serif caps each 70-90px stacked, hairline brass rules between. Each dish italic-emphasized. Bottom: hairline brass rule + small-caps warm-cream 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' + tiny dateline. Charred + brass + cream.",
        "HERITAGE MENU CARD CREAM. Warm cream ground 5-8% paper-grain. Charcoal italic Caslon title top. Charcoal serif dish name list stacked with hairline charcoal rules between. Small-caps dateline + address at bottom. Editorial menu-card discipline.",
        "HERITAGE TICKER. Charred-black ground. Horizontal running banner of dish names separated by hairline brass dots in middle canvas. Brass-foil masthead title above. Small-caps warm-cream date + address below.",
    ],
    "cultural": [
        "ETCHED EDITORIAL ALFRED REGISTER. Warm cream #F2EADF ground 10% paper-gradient. Top 18%: italic deep-charcoal Caslon serif headline 130-160px centered. Middle 50%: hand-etched pen-and-ink line-art illustration of a heritage subject (cast-iron skillet with steak, whiskey glass, dry-age cellar, fireplace, brass menu case) rendered in deep charcoal hairline crosshatch engraving. Below illustration: 3-4 line body paragraph in warm charcoal Caslon text 30-34px centered. Hairline brass rule beneath body. Small-caps deep-charcoal dateline + 'DELAWARE TODAY 2025 · BEST NEW RESTAURANT' at bottom. 5-7% linen paper-grain. Single-ink deep charcoal.",
        "HERITAGE QUOTE ON BLACK. Charred-black ground 10% gradient. Brass-foil gradient serif caps quote centered 240-300px stacked tight tracking. Brass hairline rule beneath. Small italic Caslon attribution line warm cream below. Bottom dateline + address. 5-7% film grain.",
        "OXBLOOD CULTURAL POST. Deep oxblood #5B1A1A 12% gradient. Warm cream italic Farnham headline 170-210px. Etched brass-foil ornament middle. Small-caps warm-cream body paragraph 3-4 lines. Hairline brass rule + dateline. Film grain.",
    ],
    "location_map": [
        "ETCHED MAP MIDDLETOWN. Warm cream ground 10% paper-gradient. Full-canvas engraved line-art illustrated map of Middletown DE rendered in deep-charcoal hairline ink. Jackson House rendered as prominent hand-drawn building landmark at 17 Wood St. Surrounding blocks hairline architectural silhouettes. Top small-caps 'JACKSON HOUSE · 17 WOOD ST' in charcoal + hairline rule. Bottom compass rose + scale bar + tiny italic 'Middletown, Delaware'. Vintage Saturday-Evening-Post illustration register. 5-7% linen paper-grain.",
        "ETCHED MAP BRASS. Deep oxblood ground #5B1A1A 10% gradient. Engraved line-art map of Middletown DE in brass-foil hairline ink. Jackson House as prominent building. Brass compass rose + scale bar + italic address. 5-7% film grain.",
    ],
    "menu_highlight_text": [
        "CREAM MENU LIST. Warm cream ground 5-8% paper-grain. Top 15%: deep-charcoal italic Caslon title 150-190px. Middle 60%: editorial list 5 dish names in deep-charcoal Farnham italic caps stacked each 60-80px, hairline charcoal rules between. Each dish italic-emphasized. Bottom 20%: hairline rule + small-caps 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' + tiny italic CTA. Editorial. NO photo.",
        "BRASS-FOIL MENU CARD BLACK. Charred-black ground 10% gradient. Warm-cream italic Farnham title top. Brass-foil gradient serif caps list of 4-5 names stacked, hairline brass rules between. Small-caps warm-cream dateline + address at bottom. Pure text menu card.",
        "OXBLOOD MENU CARD. Oxblood #5B1A1A 12% gradient. Warm-cream italic title. Warm-cream serif caps dish list hairline rules. Small-caps dateline + address at bottom.",
        "FOREST-GREEN MENU. Deep forest green #1F3B2D 12% gradient. Warm-cream italic title. Warm-cream dish list. Brass hairline rules. Dateline + address.",
    ],
    "campaign_masthead": [
        "BRASS-FOIL MASTHEAD BLACK. Charred-black ground 10% gradient. Full-canvas brass-foil gradient serif caps Farnham Display 240-320px stacked 2 lines tight tracking with specular. Brass hairline rule at 40% width beneath. Warm-cream small-caps support 28-34px tracked wide. Bottom dateline + hairline rule + 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' + tiny italic CTA. 5-7% film grain.",
        "CREAM EDITORIAL MASTHEAD. Warm cream ground 8% gradient. Deep-charcoal italic Caslon serif headline 240-300px stacked 2 lines tight leading 1.0. Hairline charcoal rule. Small-caps deep-charcoal support + dateline + address + italic CTA. Paper-grain.",
        "OXBLOOD MASTHEAD. Oxblood #5B1A1A 12% gradient. Warm-cream italic Farnham headline stacked. Brass hairline rule + warm-cream small-caps support + dateline + address + tiny italic CTA. Film grain.",
    ],
}

ANGLES_AZ = {
    "food_hero": [
        "ARROW-LABELED PASTEL GROUND. Pastel-saturated ground (pick chile-red #E63946, turquoise #1FB5B0, cream #F8F2DF, or pink #FF5BA7 based on dish). Photo full-scale 3/4 angle or overhead centered. 3-5 HAND-DRAWN MARKER ARROWS each originating from a short Spanish-primary ingredient label (2-4 words: camarón, salsa, aguacate, elote) TERMINATING at the visible ingredient in the photo. Arrow weight 2-3px marker-wobble. Warrior logo 80-120px in corner full-color. Chunky display caps Cooper Black OR Sharp Grotesk Ultra subject title at top 180-240px clean readable no distress ON the letters. Small-caps bilingual support. Halftone-dot background texture 45°. 60-120px soft gradient dissolve where color field meets photo edge.",
        "CLEAN EDITORIAL NO ARROWS. Pastel-saturated ground. Photo 60%+ canvas centered or 3/4. NO arrows this time. Chunky display caps Cooper Black subject title at top 200-260px. Hand-drawn small brand-ornament accent (chile silhouette, corn cob, lime wedge, tortilla-press mark) in corner — optional one only. Warrior logo 80-120px corner full-color. Small-caps bilingual support. Halftone background texture 45°. Soft gradient dissolve.",
        "DIAGONAL CURVE DUAL PHOTO. Pastel-saturated ground. Canvas split with a soft curved diagonal line — one hue on left (chile-red), complementary hue on right (turquoise or cream). Primary photo fills one side at full scale. Chunky Cooper Black subject title straddling the curve. Small-caps bilingual support. Warrior logo corner. Halftone texture. 60-120px gradient dissolve.",
    ],
    "drink_hero": [
        "PASTEL GROUND DRINK SPOTLIGHT. Pink or turquoise pastel-saturated ground 60-120px gradient edge. Glass photo 55%+ canvas. Chunky Cooper Black drink title at top 180-240px. Hand-drawn citrus/lime/chile ornament corner optional. Warrior logo corner. Small-caps Spanish-primary support. Halftone texture.",
        "ARROW-LABELED DRINK. Same as food-hero arrows but pointing at drink components (rim, garnish, ice, liquid). 3-4 arrows max Spanish-primary labels. Chunky title. Warrior logo. Halftone.",
        "CUT-OUT GLASS ON SOLID. Chile-red or pink pastel ground 10% gradient. Glass silhouette cut-out centered. Chunky Cooper Black title above 200-260px. Hand-drawn lime-wedge ornament. Warrior logo. Small-caps support. No arrows.",
    ],
    "typography_first": [
        "DICHO WALLPAPER AZ. Pink or chile-red pastel-saturated ground 8% gradient. Spanish phrase repeats as wallpaper pattern — Cooper Black caps 85-110px tight leading 1.05 zigzag offset. Center: KNOCKOUT WINDOW cream field at 65% × 30%. Inside: small italic serif translation at 42-50px, hairline rule, small-caps 'EL AZTECA · DELAWARE · REHOBOTH'. Halftone texture.",
        "HAND-PAINTED BRUSH WORDMARK. Warm cream #F8F2DF 10% gradient. Single word as HAND-PAINTED BRUSH STROKE in chile-red #E63946 or turquoise #1FB5B0 — visible brush texture, splatters. Small italic support line below. Hairline rule + small-caps bilingual dateline. Warrior logo corner subtle.",
        "CHUNKY CAPS ON PASTEL. Pastel-saturated ground. Full-canvas chunky Cooper Black caps headline 280-340px stacked 2-3 lines tight tracking. Hand-drawn underline or accent ornament. Small-caps support. Warrior logo corner. Halftone background.",
    ],
    "flyer": [
        "LOUD POSTER CHILE-RED. Chile-red ground #E63946 12% gradient. Top 25%: chunky Cooper Black caps event name cream 220-280px stacked. Middle 45%: hand-drawn cream illustration (taco, margarita, papel-picado fringe, heart, guitar for cumbia night). Lower 25%: small-caps cream info 30-36px tracked wide stacked 2-3 lines hairline rules. Bottom: warrior logo + hairline rule + small-caps address + tiny italic CTA. Halftone texture.",
        "PINK MAXIMALIST POSTER. Pink #FF5BA7 ground 12% gradient. Top masthead chunky caps chile-red outlined white 220-280px stacked. Middle: hand-drawn white illustration. Lower small-caps white info + hairline rules. Warrior logo + address + CTA bottom. Halftone + papel-picado accent corner.",
        "TURQUOISE POSTER. Turquoise #1FB5B0 ground 12% gradient. Cream Cooper Black masthead stacked. Hand-drawn cream illustration. Small-caps cream info + hairline rules. Warrior logo + address + CTA. Halftone.",
    ],
    "carousel_masthead": [
        "PASTEL MASTHEAD. Pink or chile-red pastel ground 8% gradient. Full-canvas chunky Cooper Black caps title 260-320px stacked 2 lines. Hand-drawn small accent corner. Warrior logo bottom. Small-caps support + 'DESLIZA →' bilingual swipe hint. Halftone.",
        "CREAM MASTHEAD. Cream ground 5% gradient. Chile-red chunky Cooper Black caps title stacked 260-320px. Hand-painted brush accent in turquoise or pink. Warrior logo corner. Small-caps bilingual support + swipe hint. Halftone.",
        "COBALT MASTHEAD. Cobalt #1A3FA8 10% gradient. Marigold chunky Cooper Black caps title stacked. Marigold small-caps support + swipe hint. Warrior logo corner. Halftone texture.",
    ],
    "utility": [
        "PASTEL UTILITY POSTER. Pastel-saturated ground (pink or turquoise) 8% gradient. Chunky Cooper Black caps title 200-260px stacked. Hand-drawn ornament accent. Small-caps bilingual body. Warrior logo corner. Address + italic CTA at bottom. Halftone.",
        "CREAM UTILITY. Cream #F8F2DF 5% gradient. Chile-red chunky Cooper Black caps title 200-260px stacked. Small-caps charcoal bilingual body + hairline rule + address + CTA. Warrior logo corner. Halftone.",
        "COBALT UTILITY. Cobalt #1A3FA8 10% gradient. Marigold chunky Cooper Black title. Marigold small-caps bilingual body + address + CTA. Warrior logo corner. Halftone.",
    ],
    "multi_dish_showcase": [
        "PASTEL DISH LIST. Pink or chile-red pastel ground 8% gradient. Top 15%: chunky Cooper Black title cream 160-210px. Middle 60%: list of 4-5 dish names in cream Cooper Black italic caps stacked each 70-90px, hairline cream rules between. Warrior logo bottom + address + bilingual swipe hint. Halftone.",
        "CREAM DISH LIST. Cream ground 5% gradient. Chile-red chunky caps title top. Charcoal dish name list stacked with hairline rules. Warrior logo + address + bilingual dateline bottom.",
        "COBALT TICKER. Cobalt #1A3FA8 10% gradient. Marigold masthead title top. Horizontal marigold dish-name banner middle separated by dots. Warrior logo + address bottom.",
    ],
    "cultural": [
        "PASTEL CULTURAL POST. Pink or cream pastel ground 8% gradient. Top 18%: chunky Cooper Black caps headline 160-210px. Middle 50%: hand-drawn family-warm illustration (hands on tortilla press, abuela at stove, papel picado overhead, warrior shield) in cream or chile-red. Body paragraph 3-4 lines in charcoal 30-34px centered. Warrior logo bottom + address. Halftone texture.",
        "CREAM CULTURAL. Cream #F8F2DF 5% gradient. Chile-red chunky caps headline 200-260px. Charcoal body paragraph centered. Hand-drawn chile or corn ornament. Warrior logo + address + hairline bottom. Papel-picado corner accent optional.",
        "COBALT CULTURAL. Cobalt #1A3FA8 ground 10% gradient. Marigold chunky caps headline. Marigold body paragraph. Hand-drawn white illustration. Warrior logo + address bottom. Halftone.",
    ],
    "location_map": [
        "LOTERIA CARD RISO MAP. Cream ground 8% paper-grain. Full-canvas riso-print illustrated stylized map of Delaware + Rehoboth showing both El Azteca locations as colorful hand-drawn landmarks. Pink, turquoise, chile-red, marigold inks. Warrior icon + chile icon + corn icon as decorative waypoints. Handwritten '¡Estamos aquí!' callouts pointing at the two locations. Halftone texture riso misregistration. Top masthead 'EL AZTECA' chunky caps. Bottom compass rose + address lines 'Delaware · Rehoboth'. Loteria-card aesthetic NOT clean vector.",
        "CARTOON 3D DIORAMA. Stylized 3D cartoon aerial render of Delaware showing El Azteca locations as playful landmarks with glowing signage. Volumetric warm-sun lighting. Pastel-saturated buildings. Small stylized warrior icon at each location. Top small-caps 'EL AZTECA · DELAWARE · REHOBOTH'. Bottom small-caps address + bilingual CTA. Halftone overlay. NOT photoreal.",
    ],
    "menu_highlight_text": [
        "PASTEL MENU LIST. Pink or turquoise pastel ground 8% gradient. Top: chunky Cooper Black caps title cream 160-210px. Middle: 5 dish names in cream Cooper Black italic caps stacked, hairline cream rules between. Warrior logo bottom + address + bilingual dateline. Halftone.",
        "CREAM MENU CARD. Cream ground 5% gradient. Chile-red chunky caps title. Charcoal dish list stacked hairline rules. Warrior logo + address + bilingual CTA. Halftone corner.",
        "COBALT MENU CARD. Cobalt #1A3FA8 ground 10% gradient. Marigold chunky caps title. Marigold serif caps dish list stacked hairline rules. Warrior logo + address + bilingual CTA. Halftone.",
    ],
    "campaign_masthead": [
        "PASTEL MASTHEAD LOUD. Pink or chile-red pastel ground 10% gradient. Full-canvas chunky Cooper Black caps headline 280-340px stacked 2 lines. Cream support + warrior logo + address + bilingual CTA bottom. Halftone + papel-picado corner accent.",
        "CREAM MASTHEAD. Cream ground 8% gradient. Chile-red chunky Cooper Black caps headline 260-340px stacked. Charcoal small-caps support + warrior logo + address + bilingual CTA. Halftone corner accent.",
        "COBALT MASTHEAD. Cobalt #1A3FA8 10% gradient. Marigold chunky Cooper Black caps headline stacked. Marigold support + warrior logo + address + bilingual CTA. Halftone.",
    ],
}


# ============================================================
# CONTENT-TYPE PLANS PER BRAND
# ============================================================

BRAND_PLANS = {
    "blue_mezcal": {
        "stem_default": "blue_mezcal_playful",
        "stem_nocturnal": "blue_mezcal_nocturnal",
        "stem_editorial": "blue_mezcal_editorial",
        "assets": {
            "food_hero": BM_FOOD_IMAGES,
            "cocktail_hero": BM_COCKTAIL_IMAGES,
            "typography_first": BM_DICHOS,
            "flyer": BM_FLYERS,
            "carousel_masthead": BM_CAMPAIGN_MASTHEADS + [(t, s) for (t, s) in BM_DICHOS[:2]],
            "utility": BM_UTILITY,
            "multi_dish_showcase": BM_MENU_HIGHLIGHTS + [("On the Menu.", "Chef's Tasting · Agave Flights · Mezcal Negroni · HOMBRE Old Fashioned · Seafood Parillada")],
            "cultural": BM_CULTURAL,
            "location_map": BM_LOCATION,
            "menu_highlight_text": BM_MENU_HIGHLIGHTS,
            "campaign_masthead": BM_CAMPAIGN_MASTHEADS,
        },
        "mix": [
            ("food_hero", 25, "photo"),
            ("cocktail_hero", 25, "photo"),
            ("typography_first", 15, "no_photo"),
            ("flyer", 10, "no_photo"),
            ("carousel_masthead", 6, "no_photo"),
            ("utility", 5, "no_photo"),
            ("multi_dish_showcase", 5, "no_photo"),
            ("cultural", 5, "no_photo"),
            ("location_map", 2, "no_photo"),
            ("menu_highlight_text", 2, "no_photo"),
        ],
        "angles": ANGLES_BM,
    },
    "jackson_house": {
        "stem_default": "jackson_house_tavern",
        "assets": {
            "food_hero": JH_FOOD_IMAGES,
            "cocktail_selena": JH_COCKTAILS_NO_PHOTO,
            "typography_first": JH_DICHOS,
            "flyer": JH_FLYERS,
            "carousel_masthead": JH_CAMPAIGN_MASTHEADS[:6],
            "utility": JH_UTILITY,
            "multi_dish_showcase": JH_MENU_HIGHLIGHTS,
            "cultural": JH_CULTURAL,
            "location_map": JH_LOCATION,
            "menu_highlight_text": JH_MENU_HIGHLIGHTS,
            "campaign_masthead": JH_CAMPAIGN_MASTHEADS,
        },
        "mix": [
            ("food_hero", 22, "photo"),
            ("cocktail_selena", 20, "no_photo"),
            ("typography_first", 10, "no_photo"),
            ("flyer", 8, "no_photo"),
            ("carousel_masthead", 6, "no_photo"),
            ("utility", 5, "no_photo"),
            ("multi_dish_showcase", 5, "no_photo"),
            ("cultural", 8, "no_photo"),
            ("location_map", 2, "no_photo"),
            ("menu_highlight_text", 4, "no_photo"),
            ("campaign_masthead", 10, "no_photo"),
        ],
        "angles": ANGLES_JH,
    },
    "azteca": {
        "stem_default": "azteca_playful",
        "assets": {
            "food_hero": AZ_FOOD_IMAGES,
            "drink_hero": AZ_DRINKS,
            "typography_first": AZ_DICHOS,
            "flyer": AZ_FLYERS,
            "carousel_masthead": AZ_CAMPAIGN_MASTHEADS,
            "utility": AZ_UTILITY,
            "multi_dish_showcase": AZ_MENU_HIGHLIGHTS,
            "cultural": AZ_CULTURAL,
            "location_map": AZ_LOCATION,
            "menu_highlight_text": AZ_MENU_HIGHLIGHTS,
            "campaign_masthead": AZ_CAMPAIGN_MASTHEADS,
        },
        "mix": [
            ("food_hero", 25, "photo"),
            ("drink_hero", 10, "photo"),
            ("typography_first", 8, "no_photo"),
            ("flyer", 15, "no_photo"),
            ("carousel_masthead", 6, "no_photo"),
            ("utility", 5, "no_photo"),
            ("multi_dish_showcase", 8, "no_photo"),
            ("cultural", 8, "no_photo"),
            ("location_map", 5, "no_photo"),
            ("menu_highlight_text", 5, "no_photo"),
            ("campaign_masthead", 5, "no_photo"),
        ],
        "angles": ANGLES_AZ,
    },
}


# ============================================================
# POST CONFIG GENERATION
# ============================================================

def build_post_configs(brand: str, target_count: int) -> list[dict]:
    """Generate target_count post configs for brand, rotating assets + angles."""
    plan = BRAND_PLANS[brand]
    assets = plan["assets"]
    angles = plan["angles"]
    mix = plan["mix"]

    # Scale mix to target_count
    total_pct = sum(c for _, c, _ in mix)
    configs = []
    post_idx = 1

    for ct_name, ct_count, mode in mix:
        scaled = max(1, int(round(ct_count * target_count / total_pct)))
        asset_pool = assets.get(ct_name, [])
        angle_pool = angles.get(ct_name, ["Clean editorial layout. Brand palette. Typographic hierarchy."])
        if not asset_pool:
            continue
        for i in range(scaled):
            asset = asset_pool[i % len(asset_pool)]
            angle = angle_pool[i % len(angle_pool)]
            if mode == "photo":
                image_key, subject, support = asset
            else:
                subject, support = asset
                image_key = None
            # Stem selection: BM cocktails go nocturnal if the drink is HOMBRE or Spicy; else default
            stem = plan["stem_default"]
            if brand == "blue_mezcal" and ct_name == "cocktail_hero":
                if "Spicy" in subject or "HOMBRE" in subject or "Negroni" in subject:
                    stem = plan["stem_nocturnal"]
            elif brand == "blue_mezcal" and ct_name in ("flyer", "utility") and "Mezcal Monday" in subject:
                stem = plan["stem_nocturnal"]

            fmt = "hero_dish_editorial" if mode == "photo" else (
                "operational_notice" if ct_name == "utility" else
                "event_announcement" if ct_name == "flyer" else
                "quote_post" if ct_name == "typography_first" else
                "typographic_poster"
            )

            post_id = f"BULK-{post_idx:03d}"
            configs.append({
                "brand": brand,
                "post_id": post_id,
                "format": fmt,
                "stem": stem,
                "image_key": image_key,
                "subject": subject,
                "support": support,
                "angle": angle,
                "content_type": ct_name,
            })
            post_idx += 1
            if post_idx > target_count:
                return configs
    return configs


# ============================================================
# DISPATCHER
# ============================================================

def run_one(cfg: dict) -> tuple[str, bool, str]:
    """Call nano_banana_runner as a subprocess."""
    cmd = [
        "python3", str(RUNNER),
        "--brand", cfg["brand"],
        "--post-id", cfg["post_id"],
        "--format", cfg["format"],
        "--stem", cfg["stem"],
        "--subject", cfg["subject"],
        "--support", cfg["support"],
        "--angle", cfg["angle"],
        "--count", "1",
        "--parallel", "1",
        "--aspect", "4:5",
        "--backend", "openai",
    ]
    if cfg.get("image_key"):
        cmd += ["--image-key", cfg["image_key"]]
    else:
        cmd += ["--no-logo"]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=180,
            cwd=str(ROOT),
        )
        ok = result.returncode == 0 and "✓" in result.stdout
        tail = result.stdout.strip().splitlines()[-2:] if result.stdout else []
        return cfg["post_id"], ok, "\n".join(tail)
    except subprocess.TimeoutExpired:
        return cfg["post_id"], False, "TIMEOUT"
    except Exception as e:
        return cfg["post_id"], False, f"{type(e).__name__}: {e}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True, choices=list(BRAND_PLANS.keys()) + ["all"])
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--parallel", type=int, default=8, help="Concurrent OpenAI calls")
    parser.add_argument("--dry-run", action="store_true", help="Print configs, do not call API")
    args = parser.parse_args()

    brands = list(BRAND_PLANS.keys()) if args.brand == "all" else [args.brand]

    all_configs = []
    for b in brands:
        configs = build_post_configs(b, args.count)
        print(f"[{b}] {len(configs)} configs planned")
        all_configs.extend(configs)

    if args.dry_run:
        for c in all_configs[:5]:
            print(c)
        print(f"... total: {len(all_configs)}")
        return

    print(f"\n[dispatch] {len(all_configs)} total posts, {args.parallel} concurrent\n")
    start = time.time()
    completed = 0
    failed = []

    with cf.ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futures = {ex.submit(run_one, c): c for c in all_configs}
        for fut in cf.as_completed(futures):
            post_id, ok, tail = fut.result()
            completed += 1
            status = "✓" if ok else "✗"
            print(f"[{completed}/{len(all_configs)}] {status} {post_id}  {tail[:80] if tail else ''}")
            if not ok:
                failed.append(post_id)

    elapsed = time.time() - start
    print(f"\n[done] {completed} posts in {elapsed/60:.1f}m. Failed: {len(failed)}")
    if failed:
        print(f"  Failed IDs: {failed}")


if __name__ == "__main__":
    main()
