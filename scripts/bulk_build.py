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
    # Expanded — pulled from Vista CSV 2026-04-23
    ("B-44", "Raw Oysters", "Mignonette. Lemon. Cold as promised."),
    ("B-47", "Raw Oysters", "Straight from the ice."),
    ("B-50", "Raw Oysters", "Six on the half shell."),
    ("B-56", "Seafood Parillada", "Grill. Smoke. Share."),
    ("B-57", "Seafood Parillada", "Surf, turf, fire."),
    ("B-60", "Seafood Parillada", "Table for the whole crew."),
    ("B-62", "Guacamole con Chicharrón", "Avocado. Chicharrón. Lime."),
    ("B-64", "Guacamole con Chicharrón", "Mashed to order."),
    ("B-70", "Guacamole con Crudités", "Crisp. Cool. Shared."),
    ("B-73", "Guacamole con Chicharrón", "Made to order."),
    ("B-79", "Ramen Birria", "Broth. Beef. Spoon deep."),
    ("B-80", "Ramen Birria", "Slow-braised. Rich."),
    ("B-82", "Ramen Birria", "Bowl of patience."),
    ("B-83", "Street Tacos", "Three on a plate."),
    ("B-84", "Street Tacos", "Corn tortilla. Done right."),
    ("B-85", "Street Tacos", "Simple on purpose."),
    ("B-88", "Cheesy Burrito", "Wrapped. Melted. Hot."),
    ("B-89", "Cheesy Burrito", "Chef's late-night move."),
    ("B-92", "Enchiladas Verdes", "Green sauce. Hand-rolled."),
    ("B-93", "Alitas", "Wings. Our way."),
    ("B-94", "Alitas", "Sticky. Hot. Finger-food."),
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
    # English only — no Spanish (per brand lock 2026-04-23)
    ("Smoke, citrus, slow.", "Blue Mezcal · Middletown DE"),
    ("One more. You'll survive.", "Cocktail Hour · Blue Mezcal"),
    ("Impossible to have one.", "Blue Mezcal · Middletown DE"),
    ("Cool and dangerous.", "Blue Mezcal · Middletown DE"),
    ("Another round?", "Blue Mezcal · Middletown DE"),
    ("A handshake in a glass.", "Blue Mezcal · Middletown DE"),
]

BM_FLYERS = [
    ("Mezcal Monday.", "Half-off flights · 5–8pm · Espadín · Tobalá · Cuishe"),
    ("Happy Hour.", "Monday–Thursday · 5–7pm · Half-off mezcal flights"),
    ("Agave Tasting.", "Saturdays · 7pm · Three-pour flight"),
    ("Brunch.", "Sundays · 11am–3pm"),
    ("Chef's Table.", "Fridays · Six courses · Reserve ahead"),
]

BM_CULTURAL = [
    # English only
    ("On the slow things.", "Mezcal is not hurried. Neither are we."),
    ("On agave.", "Seven years in the ground. One moment in the glass."),
    ("On smoke.", "The fire is part of the flavor."),
    ("On the copita.", "Small glass. Big patience."),
]

# Review-card post type: real customer review, quoted as editorial graphic.
# Each entry: (source/venue, star-count display, review quote, attribution tag)
BM_REVIEW_CARDS = [
    ("Google · 5 stars", "★★★★★", "One of the best mezcal programs on the East Coast.", "— Google review"),
    ("Yelp · 5 stars", "★★★★★", "The cucumber margarita is a whole moment.", "— Yelp review"),
    ("Google · 5 stars", "★★★★★", "Every cocktail feels thought through.", "— Google review"),
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
    # Expanded — pulled from Vista CSV 2026-04-23
    ("T-72", "Chimichurri Steak", "Chimichurri. Charred rim. Mid-rare."),
    ("T-73", "Chimichurri Steak", "Heritage cut. Mid-rare by default."),
    ("T-87", "Orecchiette", "Hand-rolled. Sausage. Broccoli rabe."),
    ("T-88", "Orecchiette", "Hand-rolled pasta, the old way."),
    ("T-61", "Lobster Roll", "Toasted brioche. Cream sauce. Chives."),
    ("T-62", "Lobster Roll", "New on the menu. Already a favorite."),
    ("T-70", "Elote Burger", "We're not going to explain this one."),
    ("T-67", "Elote Burger", "Just order it."),
    ("T-64", "Summer Scallops", "Charred, citrus, clean."),
    ("T-45", "Fried Okra", "Crisp edge. Southern habit."),
    ("T-46", "Fried Okra", "Cast-iron crisp."),
    ("T-48", "Cornbread Muffins", "Warm. Butter melts on contact."),
    ("T-49", "Fried Catfish Fingers", "Crunch. Tartar. Lemon."),
    ("T-51", "Fried Catfish Fingers", "The bar-menu favorite."),
    ("T-59", "Burrata", "Cream inside. Good bread beside."),
    ("T-75", "Mixed Greens", "Season-first. Dressed light."),
    ("T-76", "Mixed Greens", "Farmer's table side."),
    ("T-78", "Fried Chicken Wings", "Hot. Honest. House-made."),
    ("T-80", "Fried Chicken Wings", "Cast-iron crisp."),
    ("T-81", "House Guacamole", "Hand-mashed. House chips."),
    ("T-83", "Fried Chicken Wrap", "Hand-held. Honest."),
    ("T-85", "Fried Chicken Wrap", "Lunch-counter classic."),
    ("T-89", "Linguine", "Al dente. Parm. Herb oil."),
    ("T-90", "Linguine", "Hand-tossed."),
    ("T-91", "Linguine", "Done the long way."),
    ("T-94", "Grilled Chicken Tacos", "Soft tortilla. Citrus. Crema."),
    ("T-95", "Grilled Chicken Tacos", "Order of three."),
    ("T-97", "Grilled Chicken Tacos", "Weekday lunch."),
    ("T-101", "Strawberry Layer Cake", "From the pastry case."),
    ("T-102", "Strawberry Layer Cake", "Dessert, done simply."),
    ("T-104", "Berry Chantilly Cake", "Cream. Berries. Done."),
    ("T-108", "Peach Cobbler", "Warm. Fork-tender."),
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
    # AZ-8 / AZ-9 moved — renamed to cleaner subject below ("Octopus Guacamole")
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
    # Expanded 2026-04-23
    ("AZ-15", "Homestyle Bacon Jalapeños", "Hot, smoky, shareable."),
    ("AZ-16", "Homestyle Bacon Jalapeños", "Bar-table classic."),
    ("AZ-20", "The Whole Table Is Eating", "Family-style spread."),
    ("AZ-41", "Alambres", "Grilled. Stirred. Shared."),
    ("AZ-45", "Alambres", "Cast-iron hot."),
    ("AZ-46", "Bring The Crew", "Big tables welcome."),
    ("AZ-72", "Family Style. No Apologies.", "Tables are bigger than they look."),
    ("AZ-82", "Baja Burrito", "Hand-held. Hot. Honest."),
    ("AZ-83", "Baja Burrito", "Wrapped right."),
    ("AZ-84", "Baja Burrito", "Weekend-lunch move."),
    ("AZ-92", "Churros", "Hot sugar. Dip and go."),
    ("AZ-101", "Dessert Menu", "Flan. Tres Leches. Chocolate Lava."),
    ("AZ-103", "Tres Leches", "Three milks. One bite."),
    # Renamed for cleaner subject (old form invited arrow-misreads)
    ("AZ-8", "Octopus Guacamole", "Octopus. Avocado. House chips."),
    ("AZ-9", "Octopus Guacamole", "Not your average appetizer."),
]

AZ_DRINKS = [
    ("AZ-47", "Cocktail hour.", "Margaritas · Micheladas · Pick your poison"),
    ("AZ-73", "Pick your poison.", "Happy Hour · All week"),
]

AZ_DICHOS = [
    ("De la casa.", "El Azteca · Camden · Dover · Rehoboth"),
    ("Auténtico.", "El Azteca · Camden · Dover · Rehoboth"),
    ("Classic for a reason.", "El Azteca"),
    ("Con gusto.", "El Azteca · Camden · Dover · Rehoboth"),
    ("La comida es amor.", "El Azteca"),
]

AZ_FLYERS = [
    # VERIFIED events only — unverified Cumbia Night / Altar Menu / Menu Especial
    # claims removed 2026-04-23 pending confirmation from Hector
    ("Taco Tuesday.", "Every Tuesday"),
    ("Happy Hour.", "Monday–Friday · 4–6pm · Margaritas · Micheladas"),
    ("Sunday Brunch.", "11am–3pm · Family Style"),
    ("Mother's Day.", "Reserve ahead"),
    ("Margarita Monday.", "House margaritas · $ deals"),
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
    ("Estamos aquí.", "Camden · Dover · Rehoboth"),
    ("Find us.", "Three locations · Camden · Dover · Rehoboth"),
    ("Camden · Dover · Rehoboth.", "Three tables · One family"),
]

AZ_MENU_HIGHLIGHTS = [
    ("The menu.", "Guacamole Octopus · Carne Asada · Cóctel de Camarón · Whole Fried Tilapia"),
    ("Del bar.", "Margaritas · Micheladas · Aguas Frescas"),
    ("Postres.", "Flan · Churros · Chocolate Lava Cake · Tres Leches"),
    ("Brunch.", "Huevos Rancheros · Chilaquiles · Breakfast Enchiladas"),
    ("Favorites.", "Tacos · Enchiladas · Fajitas · Burritos"),
]

AZ_CAMPAIGN_MASTHEADS = [
    ("Bienvenidos.", "El Azteca · Camden · Dover · Rehoboth"),
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
        "BRUTALIST ENGLISH-PHRASE WALLPAPER. Bone-cream ground 8% paper-gradient. The ENGLISH phrase (supplied as subject) repeats as tight wallpaper pattern across canvas, rows stacked, each row offset horizontally ~90px zigzag, cobalt GT Sectra italic caps 85-110px tight leading 1.05. Center: rectangular KNOCKOUT WINDOW at 65% width × 30% height — cream field punching through wallpaper. Inside window: small italic Canela continuation line (from support copy) 42-50px, hairline cobalt rule, tiny 'BLUE MEZCAL · MIDDLETOWN DE' small-caps. NO Spanish anywhere — Blue Mezcal is English-only. 5-8% linen paper-grain.",
        "HAND-PAINTED BRUSH WORDMARK. Bone-cream ground 10-12% paper-gradient. Single word dominates canvas at 480-560px, rendered as HAND-PAINTED BRUSH STROKE in cobalt — visible brush texture, bleed edges, intentional paint splatters, calligrapher's one-shot feel. One tiny marigold paint splatter near final period. Below at 40% height: italic Canela in cobalt 42-50px one line. Hairline cobalt rule + small-caps dateline.",
        "ITALIC SERIF MASTHEAD ON CREAM. Bone-cream ground 10% gradient. Oversized italic Canela or GT Sectra serif in cobalt dominating upper 60% at 160-220px, stacked 2-3 lines tight leading 1.0, one word italicized for emphasis. Hairline cobalt rule beneath. Small-caps support line in cobalt 32-38px. Bottom dateline + hairline rule. 5% linen paper-grain. Pure editorial restraint.",
    ],
    "flyer": [
        "BM NOCTURNAL POSTER (DARK BLUE + WARM CREAM — high contrast). Midnight cobalt #14213D ground DOMINANT 80% with 10% tonal gradient (darker toward corners). Velvet burgundy #4A1621 deep-gradient sub-field at ONE corner only, capped at 15% of canvas. ALL TYPE IS WARM CREAM #F2EADF (NOT blue, NOT foil-blue — cream must read bright against the dark blue ground for readability). TOP 30%: masthead in warm-cream italic serif (Farnham/Canela Italic) 180-230px stacked 2 lines tight tracking, thin warm-tan hairline rule beneath. MIDDLE 40%: single hand-drawn warm-cream hairline COPITA silhouette centered, line-art only, small smoke curl. LOWER 25%: small-caps warm-cream support info 30-36px tracked wide, hairline cream rule separators. BOTTOM strip: tiny warm-cream dateline small-caps wide-tracked. NEVER blue-type-on-blue-ground (no-contrast failure). NEVER brass, NEVER gold, NEVER black ground. 5-7% film grain.",
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
    "review_card": [
        "REVIEW CARD AWARDS-EDITORIAL. Bone-cream ground #F3ECD8 with 5-7% paper-grain. Top 15%: small-caps cobalt kicker 'REAL ONES' tracked wide 28-32px with hairline cobalt rules flanking both sides. Center 55%: a TEXT-BOX QUOTE in cobalt GT Sectra italic at 60-80px — the review quote (from support) centered, 2-4 lines tight leading 1.15. Surrounding the text-box: 4-6 small circular 'award badges' in cobalt hairline outline (laurel wreaths, star seals, 'five star' circular stamps) arranged symmetrically flanking the quote — like award badges on a movie poster. Bottom 20%: small-caps cobalt attribution 'GOOGLE REVIEW · FIVE STARS' tracked wide with hairline rule + tiny venue dateline. NO photo. NO invented review — the quote must come from the support copy verbatim.",
        "REVIEW CARD COBALT FIELD. Cobalt #1E3A8A ground 10% tonal gradient. Upper 15%: five warm-cream star icons centered (★★★★★). Middle 55%: quote in warm-cream italic Canela 60-80px centered, 2-4 lines. Lower 15%: small-caps warm-cream attribution + venue dateline. Hairline cream rules above/below. No photo.",
        "REVIEW CARD AWARD-SEAL CORNERS. Bone-cream ground. Center: cobalt italic Canela quote 70-90px, 2-3 lines centered. Four corner medallions — small cobalt circular hairline seals with '5 STARS' or 'GOOGLE' or 'YELP' small-caps inside each — one per corner. Hairline cobalt frame around the entire canvas (editorial framing rule). Bottom venue dateline. No photo.",
    ],
}

ANGLES_JH = {
    "food_hero": [
        "GHIA HERITAGE EDITORIAL. Warm cream ground #F2EADF divided: photo RIGHT 55% full-scale, cream field LEFT 45%. Left carries: brass-foil gradient serif caps Farnham Display 120-150px stacked 2 lines tight tracking. Beneath: small-caps Trade Gothic Condensed deep charcoal support line tracked wide 26-30px. Hairline brass rule + tiny italic Caslon 'Jackson House' 32-36px. BOTTOM LEFT: small-caps 'DELAWARE TODAY 2025 · BEST NEW RESTAURANT' 20-24px + hairline rule + '17 WOOD ST · MIDDLETOWN DE'. 5-7% paper-grain. Brass + cream + charcoal only.",
        "DRAMATIC CROP ON CHARRED BLACK. Charred-black ground #0A0A0A 10% tonal gradient. Photo cropped tight on dish detail (sear, char, garnish) fills 65% canvas lower-right. Upper-left 35% negative space carries brass-foil gradient serif caps stacked 130-160px plus small-caps warm-cream subject subhead below. Hairline brass rule + tiny dateline at bottom. 5-7% film grain. Moody.",
        "VERTICAL OXBLOOD STRIP. Photo fills RIGHT 70% full-scale. LEFT 30% solid deep oxblood #5B1A1A with 10-14% tonal gradient. Brass-foil gradient serif caps in strip at 100-130px stacked vertically fits strip width. Small-caps warm-cream support beneath. Hairline brass rule + tiny address at bottom of strip. Oxblood + brass + cream only.",
    ],
    # CAROUSEL-FINALE ONLY. These slides close a multi-post carousel that
    # opens with the ACTUAL drink photograph in slide 1. Never used standalone.
    "cocktail_selena_finale": [
        "SELENA NAME-MASTHEAD BLACK (CAROUSEL-FINALE SLIDE — assumes slides 1–3 showed the real drink photo). Charred-black ground 10% tonal gradient. Full-canvas SCRIPT+SERIF LOCKUP of the drink name — connecting word in Farnham Italic 180-220px warm cream, power words in refined serif CAPS Farnham Display 260-320px brass-foil gradient + specular, stacked 2-3 lines tight tracking asymmetric centering. Brass hairline rule. Small italic Caslon pullquote warm cream 50-60px centered below. Small-caps 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE · CAROUSEL CLOSER' 22-26px tracked wide at bottom. 5-7% film grain. NOTE: bottom-right micro-text 'slide back to start' small-caps hint.",
        "SELENA NAME-MASTHEAD OXBLOOD (CAROUSEL-FINALE). Deep oxblood #5B1A1A 12% tonal gradient. SCRIPT+SERIF LOCKUP — italic cursive 180-220px warm cream + serif caps 280-340px brass-foil gradient stacked asymmetric tight tracking. Brass hairline rule + italic Caslon pullquote warm cream + small-caps dateline. Final-slide intent: 'slide back to start' micro-hint bottom-right. 5-7% film grain.",
        "SELENA NAME-MASTHEAD CREAM (CAROUSEL-FINALE). Warm cream ground 10% paper-gradient. Top: SCRIPT+SERIF lockup — italic cursive at 140-170px deep charcoal + serif caps 1.4x scale deep charcoal stacked. Italic Caslon pullquote below. Small-caps dateline + 'CAROUSEL CLOSER' micro-hint at bottom. No photo, type-only editorial close.",
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
        # Arrow-rule: DEFAULT ZERO. Only use arrows when EVERY arrow terminus can be
        # verified against a visible, named ingredient in the specific photo.
        "ARROW-LABELED PASTEL GROUND (semantic-accuracy enforced). Primary ground: chile-red #E63946, forest green #2F7A3A, cobalt #1A3FA8, or masa cream #F8F2DF (pink capped <15% accent only). Photo full-scale 3/4 or overhead. 2-3 HAND-DRAWN MARKER ARROWS MAX — only add an arrow if you can verify (1) the label names a single ingredient visibly identifiable at a specific pixel location, (2) the arrow tip terminates on that ingredient exactly, (3) the label is not a generic word applied to ambiguous sauce/garnish. If ANY condition fails, drop that arrow. If dish lacks clearly separable ingredients, use ZERO arrows. Arrow weight 2-3px marker-wobble. Warrior logo 80-120px corner full-color VERBATIM from supplied PNG. Chunky display caps title at top 180-240px (weight matched to logo). Small-caps bilingual support. Halftone-dot background 45°. 60-120px soft gradient dissolve at photo edge.",
        "CLEAN EDITORIAL NO ARROWS (default food-hero style). Pastel-saturated ground (chile-red, green, cobalt, or cream; pink <15%). Photo 60%+ canvas centered or 3/4. ZERO arrows. Chunky display caps title at top 200-260px matching logo weight. Optional ONE hand-drawn brand-ornament accent corner (chile, corn, lime-wedge, tortilla-press). Warrior logo 80-120px corner VERBATIM full-color. Small-caps bilingual support. Halftone background 45°. Soft gradient dissolve at photo edge.",
        "DIAGONAL CURVE DUAL PHOTO. Pastel-saturated ground — chile-red one side, green or cream other side (pink <15%). Photo fills one side at full scale. Chunky Cooper Black subject title straddling curve (weight matched to logo). Small-caps bilingual support. Warrior logo corner VERBATIM. Halftone texture. 60-120px gradient dissolve.",
    ],
    "drink_hero": [
        "PASTEL GROUND DRINK SPOTLIGHT. Chile-red, green, or cream pastel ground (pink capped at 15% accent max) 60-120px gradient edge. Glass photo 55%+ canvas. Chunky Cooper Black drink title at top 180-240px. Hand-drawn citrus/lime/chile ornament corner optional. Warrior logo corner. Small-caps Spanish-primary support. Halftone texture.",
        "ARROW-LABELED DRINK. Same as food-hero arrows but pointing at drink components (rim, garnish, ice, liquid). 3-4 arrows max Spanish-primary labels. Chunky title. Warrior logo. Halftone.",
        "CUT-OUT GLASS ON SOLID. Chile-red or pink pastel ground 10% gradient. Glass silhouette cut-out centered. Chunky Cooper Black title above 200-260px. Hand-drawn lime-wedge ornament. Warrior logo. Small-caps support. No arrows.",
    ],
    "typography_first": [
        "DICHO WALLPAPER AZ. Chile-red, green, or cream pastel ground (pink capped at 15% accent max) 8% gradient. Spanish phrase repeats as wallpaper pattern — Cooper Black caps 85-110px tight leading 1.05 zigzag offset. Center: KNOCKOUT WINDOW cream field at 65% × 30%. Inside: small italic serif translation at 42-50px, hairline rule, small-caps 'EL AZTECA · CAMDEN · DOVER · REHOBOTH'. Halftone texture.",
        "HAND-PAINTED BRUSH WORDMARK. Warm cream #F8F2DF 10% gradient. Single word as HAND-PAINTED BRUSH STROKE in chile-red #E63946 or turquoise #1FB5B0 — visible brush texture, splatters. Small italic support line below. Hairline rule + small-caps bilingual dateline. Warrior logo corner subtle.",
        "CHUNKY CAPS ON PASTEL. Pastel-saturated ground. Full-canvas chunky Cooper Black caps headline 280-340px stacked 2-3 lines tight tracking. Hand-drawn underline or accent ornament. Small-caps support. Warrior logo corner. Halftone background.",
    ],
    "flyer": [
        "LOUD POSTER CHILE-RED. Chile-red ground #E63946 12% gradient. Top 25%: chunky Cooper Black caps event name cream 220-280px stacked. Middle 45%: hand-drawn cream illustration (taco, margarita, papel-picado fringe, heart, guitar for cumbia night). Lower 25%: small-caps cream info 30-36px tracked wide stacked 2-3 lines hairline rules. Bottom: warrior logo + hairline rule + small-caps address + tiny italic CTA. Halftone texture.",
        "PINK MAXIMALIST POSTER. Pink #FF5BA7 ground 12% gradient. Top masthead chunky caps chile-red outlined white 220-280px stacked. Middle: hand-drawn white illustration. Lower small-caps white info + hairline rules. Warrior logo + address + CTA bottom. Halftone + papel-picado accent corner.",
        "TURQUOISE POSTER. Turquoise #1FB5B0 ground 12% gradient. Cream Cooper Black masthead stacked. Hand-drawn cream illustration. Small-caps cream info + hairline rules. Warrior logo + address + CTA. Halftone.",
    ],
    "carousel_masthead": [
        "PASTEL MASTHEAD. Chile-red, green, cobalt, or cream pastel ground (pink capped at 15% accent max) 8% gradient. Full-canvas chunky Cooper Black caps title 260-320px stacked 2 lines. Hand-drawn small accent corner. Warrior logo bottom. Small-caps support + 'DESLIZA →' bilingual swipe hint. Halftone.",
        "CREAM MASTHEAD. Cream ground 5% gradient. Chile-red chunky Cooper Black caps title stacked 260-320px. Hand-painted brush accent in turquoise or pink. Warrior logo corner. Small-caps bilingual support + swipe hint. Halftone.",
        "COBALT MASTHEAD. Cobalt #1A3FA8 10% gradient. Marigold chunky Cooper Black caps title stacked. Marigold small-caps support + swipe hint. Warrior logo corner. Halftone texture.",
    ],
    "utility": [
        "PASTEL UTILITY POSTER. Pastel-saturated ground (pink or turquoise) 8% gradient. Chunky Cooper Black caps title 200-260px stacked. Hand-drawn ornament accent. Small-caps bilingual body. Warrior logo corner. Address + italic CTA at bottom. Halftone.",
        "CREAM UTILITY. Cream #F8F2DF 5% gradient. Chile-red chunky Cooper Black caps title 200-260px stacked. Small-caps charcoal bilingual body + hairline rule + address + CTA. Warrior logo corner. Halftone.",
        "COBALT UTILITY. Cobalt #1A3FA8 10% gradient. Marigold chunky Cooper Black title. Marigold small-caps bilingual body + address + CTA. Warrior logo corner. Halftone.",
    ],
    "multi_dish_showcase": [
        "PASTEL DISH LIST. Chile-red, green, cobalt, or cream pastel ground (pink capped at 15% accent max) 8% gradient. Top 15%: chunky Cooper Black title cream 160-210px. Middle 60%: list of 4-5 dish names in cream Cooper Black italic caps stacked each 70-90px, hairline cream rules between. Warrior logo bottom + address + bilingual swipe hint. Halftone.",
        "CREAM DISH LIST. Cream ground 5% gradient. Chile-red chunky caps title top. Charcoal dish name list stacked with hairline rules. Warrior logo + address + bilingual dateline bottom.",
        "COBALT TICKER. Cobalt #1A3FA8 10% gradient. Marigold masthead title top. Horizontal marigold dish-name banner middle separated by dots. Warrior logo + address bottom.",
    ],
    "cultural": [
        "PASTEL CULTURAL POST. Cream or chile-red pastel ground (pink capped at 15% accent max) 8% gradient. Top 18%: chunky Cooper Black caps headline 160-210px. Middle 50%: hand-drawn family-warm illustration (hands on tortilla press, abuela at stove, papel picado overhead, warrior shield) in cream or chile-red. Body paragraph 3-4 lines in charcoal 30-34px centered. Warrior logo bottom + address. Halftone texture.",
        "CREAM CULTURAL. Cream #F8F2DF 5% gradient. Chile-red chunky caps headline 200-260px. Charcoal body paragraph centered. Hand-drawn chile or corn ornament. Warrior logo + address + hairline bottom. Papel-picado corner accent optional.",
        "COBALT CULTURAL. Cobalt #1A3FA8 ground 10% gradient. Marigold chunky caps headline. Marigold body paragraph. Hand-drawn white illustration. Warrior logo + address bottom. Halftone.",
    ],
    "location_map": [
        "LOTERIA CARD RISO MAP. Cream ground 8% paper-grain. Full-canvas riso-print illustrated stylized map of Camden + Dover + Rehoboth showing all three El Azteca locations as colorful hand-drawn landmarks. Pink, turquoise, chile-red, marigold inks. Warrior icon + chile icon + corn icon as decorative waypoints. Handwritten '¡Estamos aquí!' callouts pointing at the three locations. Halftone texture riso misregistration. Top masthead 'EL AZTECA' chunky caps. Bottom compass rose + address lines 'Camden · Dover · Rehoboth'. Loteria-card aesthetic NOT clean vector.",
        "CARTOON 3D DIORAMA. Stylized 3D cartoon aerial render of Delaware showing all THREE El Azteca locations (Camden, Dover, Rehoboth) as playful landmarks with glowing signage. Volumetric warm-sun lighting. Pastel-saturated buildings. Small stylized warrior icon at each location. Top small-caps 'EL AZTECA · CAMDEN · DOVER · REHOBOTH'. Bottom small-caps address + bilingual CTA. Halftone overlay. NOT photoreal.",
    ],
    "menu_highlight_text": [
        "PASTEL MENU LIST. Chile-red, green, cobalt, or cream pastel ground (pink capped at 15% accent max) 8% gradient. Top: chunky Cooper Black caps title cream 160-210px. Middle: 5 dish names in cream Cooper Black italic caps stacked, hairline cream rules between. Warrior logo bottom + address + bilingual dateline. Halftone.",
        "CREAM MENU CARD. Cream ground 5% gradient. Chile-red chunky caps title. Charcoal dish list stacked hairline rules. Warrior logo + address + bilingual CTA. Halftone corner.",
        "COBALT MENU CARD. Cobalt #1A3FA8 ground 10% gradient. Marigold chunky caps title. Marigold serif caps dish list stacked hairline rules. Warrior logo + address + bilingual CTA. Halftone.",
    ],
    "campaign_masthead": [
        "PASTEL MASTHEAD LOUD. Chile-red, green, cobalt, or cream pastel ground (pink capped at 15% accent max) 10% gradient. Full-canvas chunky Cooper Black caps headline 280-340px stacked 2 lines. Cream support + warrior logo + address + bilingual CTA bottom. Halftone + papel-picado corner accent.",
        "CREAM MASTHEAD. Cream ground 8% gradient. Chile-red chunky Cooper Black caps headline 260-340px stacked. Charcoal small-caps support + warrior logo + address + bilingual CTA. Halftone corner accent.",
        "COBALT MASTHEAD. Cobalt #1A3FA8 10% gradient. Marigold chunky Cooper Black caps headline stacked. Marigold support + warrior logo + address + bilingual CTA. Halftone.",
    ],
}


# ============================================================
# SAVORA — parent studio pools (hero client photos re-contextualized
# as portfolio + editorial no-photo formats). Hero list curated to
# HERO DISHES + DRINKS ONLY per Hector 2026-04-23. Sides / desserts /
# non-flagship items dropped.
# ============================================================

# Each tuple: (cloudinary_key, subject_headline_voice, support_credit_line)
# Subject = Savora-voice one-liner (Fraunces italic display).
# Support = "Shot for [Client]" credit (small-caps body).
# Client credit gets rendered per savora_studio stem CREDIT RULE.
SAVORA_HERO_PHOTOS = [
    # Voice register: PHOTOGRAPHY-CRAFT, not dish-sales.
    # Headlines document THE WORK of making the image — light, lens,
    # time-of-day, frame-count, composition decisions, client brief —
    # NEVER flavor / ingredients / dish mood (that's restaurant-brand voice).
    # Support = "Shot for [Client] · [Dish]" small-caps credit.
    # --- Blue Mezcal (hero drinks + signature dishes) ---
    ("B-35", "Tungsten at 2800K. One rim light. Portra 800 push.", "Shot for Blue Mezcal · HOMBRE Old Fashioned"),
    ("B-36", "Eighty-five at f/2. Shutter dropped for the glass.",  "Shot for Blue Mezcal · HOMBRE Old Fashioned"),
    ("B-3",  "Window-soft at 3:47pm. Twelve minutes of light.",      "Shot for Blue Mezcal · Cucumber Margarita"),
    ("B-7",  "Single bounce card camera-right. The rim did the rest.", "Shot for Blue Mezcal · Spicy Margarita"),
    ("B-44", "Overhead. Seven inches above the ice.",                "Shot for Blue Mezcal · Raw Oysters"),
    ("B-56", "Twelve setups. One kept.",                             "Shot for Blue Mezcal · Seafood Parillada"),
    ("B-62", "Pre-pro Tuesday. Shot Thursday. Delivered Friday.",    "Shot for Blue Mezcal · Guacamole con Chicharrón"),
    ("B-79", "Five inches above the bowl. Steam caught on take two.", "Shot for Blue Mezcal · Ramen Birria"),
    ("B-83", "Daylight at 5200K. Thirty-two frames. Three kept.",    "Shot for Blue Mezcal · Street Tacos"),
    # --- Jackson House (hero dishes + signature) ---
    ("T-72", "Forty minutes to set the key. Four seconds to shoot it.", "Shot for Jackson House · Chimichurri Steak"),
    ("T-61", "Natural fall-off. No fill. Chef at the pass.",            "Shot for Jackson House · Lobster Roll"),
    ("T-70", "Available light. Chosen frame.",                          "Shot for Jackson House · Elote Burger"),
    ("T-64", "Close-crop on the sear. Backed off the plate.",           "Shot for Jackson House · Summer Scallops"),
    ("T-59", "Restraint carried the image.",                            "Shot for Jackson House · Burrata"),
    ("T-78", "Side-light at 45°. Texture doing the work.",              "Shot for Jackson House · Fried Chicken Wings"),
    # --- El Azteca (hero dishes + signature) ---
    ("AZ-8",  "Daylight through a single north window.",               "Shot for El Azteca · Octopus Guacamole"),
    ("AZ-49", "Eight-stop range. Filed the highlight. Let the char breathe.", "Shot for El Azteca · Carne Asada"),
    ("AZ-37", "Twenty-eight frames. This one earned its place.",       "Shot for El Azteca · Whole Fried Tilapia"),
    ("AZ-22", "Shutter at 1/125. Hands left in frame on purpose.",     "Shot for El Azteca · Cóctel de Camarón"),
    ("AZ-64", "Tether to Lightroom. Chef approved as we shot.",        "Shot for El Azteca · Elote"),
    # NOTE: Rojas + Tolteca keys pending upload to cloudinary_urls.json.
    # Add ("R-01", ...), ("TOL-01", ...) tuples once keys registered.
]

# Each tuple: (subject = headline stat, support = context · window · caveat · client)
# Real data only per Hector 2026-04-23 — signed off. Use selectively, not every batch.
SAVORA_METRIC_CARDS = [
    (
        "33,000",
        "Impressions · One post · @taqueriarojas · April 2026 · menu relaunch ran same week · Taqueria Rojas",
    ),
    (
        "862",
        "Saves · 72 hours · One reel · April 2026 · weekend + new menu launch · Taqueria Rojas",
    ),
    (
        "+161%",
        "Engagement · 30 days · feed + stories + reels · Q1 2026 · added private-event push · Jackson House",
    ),
    (
        "+177%",
        "Impressions · Q1 · paired screenshots dated start and end · Jan–Mar 2026 · hired line cook mid-window · El Azteca Rehoboth",
    ),
]

# Philosophy / manifesto one-liners — Savora voice seed only.
SAVORA_PHILOSOPHY = [
    ("The food did the work. We just framed it.", "Savora · Restaurant Studio"),
    ("Restaurants should own the story. Not the algorithm.", "Savora · Manifesto"),
    ("Good marketing photographs what is. Not what could be.", "Savora · Field Notes"),
    ("Twenty-eight frames. This one earned its place.", "Savora · Restaurant Studio"),
    ("If your feed could belong to any restaurant, it belongs to none.", "Savora · Field Notes"),
    ("Your logo is not your brand.", "Savora · Field Notes"),
    ("One dish. Thirty deliverables.", "Savora · Field Notes"),
]

# Service-explainer cards — no dollar amounts. Type-only editorial.
SAVORA_SERVICE_CARDS = [
    ("Monthly Content Package.", "Photography · Video · Reels · Social Design · Brand Voice"),
    ("Photography Day Rate.", "Editorial still-life · Documentary BTS · Hero dishes · Same-day proofs"),
    ("Video + Reel Production.", "Hook-first edits · Captions · Music clearance · Platform-native aspects"),
    ("Brand System.", "Logo · Palette · Type · Voice · Photography direction · One source of truth"),
    ("Website + SEO.", "Fast · Schema-markup · AI-search ready · Conversion-first · Reservations wired"),
]

# Carousel opening / campaign masthead — no photo, editorial title.
SAVORA_CAMPAIGN_MASTHEADS = [
    ("Before Savora / After Savora.", "A new portfolio drops this week · Savora · DE"),
    ("The Restaurant Studio.", "Photography · Video · Brand Systems · Delaware"),
    ("One dish, thirty deliverables.", "A Savora Field Note · swipe →"),
    ("Shot for the menu. Kept for the grid.", "Savora portfolio · Spring 2026"),
]

# Cultural / meta-editorial commentary on the industry.
SAVORA_CULTURAL = [
    ("On craft.", "Twenty-eight frames. Seventeen hours. One image that earns the wall."),
    ("On restraint.", "The best edit is usually the one you didn't make."),
    ("On process.", "Pre-production is where the shoot actually happens."),
    ("On clients.", "A brand system is a decision tree your team can follow when you are not in the room."),
]

# Multi-dish / multi-client showcase — TEXT ONLY (Phase A). Phase B will
# add multi-image composite formats once runner supports ref_image_bytes_list.
SAVORA_PORTFOLIO_LIST = [
    ("Spring Portfolio.", "Blue Mezcal · Jackson House · El Azteca · Taqueria Rojas"),
    ("This Quarter.", "Four kitchens. One lens. Savora."),
]


# ============================================================
# SAVORA angle templates (3 per content type, editorial-restraint,
# 60% cream · 30% teal · 10% burnt orange accent, Fraunces + Outfit)
# ============================================================

ANGLES_SAVORA = {
    # Visual register: DARK LUXURY PHOTOGRAPHY MONOGRAPH. Near-black ground
    # (#00060B with deep-teal undertone), warm off-white type (#D9D4CE),
    # metallic-orange-foil + metallic-gold-foil + metallic-teal-foil gradient
    # accents. Matches savoramarketing.com site palette. Never cream-dominant.
    "hero_photograph": [
        "AESOP DARK MONOGRAPH. Near-black #00060B ground 10-14% tonal gradient (darker toward corners) fills LEFT 44% of canvas, client photo fills RIGHT 56% full-scale untouched. Soft 60-80px gradient dissolve between photo-edge and dark field (no hard knife-edge). Left dark column: small-caps Geist MUTED TEAL #7B9693 kicker 'SAVORA · PORTFOLIO · NO.01' tracked 0.24em 14-16px at top, hairline METALLIC-TEAL-FOIL rule 40% width (gradient #2B8C83→#145A55→#073733), Gambarino/Fraunces italic WARM OFF-WHITE #D9D4CE headline 72-96px stacked 3-4 lines tight leading 1.05 (subject verbatim — photography-craft line), hairline metallic-teal rule, small-caps Geist MUTED TEAL credit line 18-22px tracked 0.22em (support verbatim), tiny metallic-GOLD-FOIL Savora seal 72px bottom-left (#F7DA7F→#E0B045→#8A621A specular), small-caps Geist warm-off-white address 13-15px at very bottom. 5-8% fine film grain on dark field. NO metallic-orange-foil on this angle — restrained all-teal-foil plus gold seal.",
        "FULL-BLEED CLIENT PHOTO + METALLIC-ORANGE-FOIL BOTTOM STRIP. Client photo fills 100% canvas full-scale untouched. Bottom 22% of canvas carries a NEAR-BLACK #00060B tonal-gradient strip (darker edge at very bottom) with soft 50-70px dissolve transition from photo-edge. Strip contents: small-caps Geist MUTED TEAL kicker 'SAVORA · SHOT FOR' tracked 0.26em 14px LEFT-aligned at top of strip, Gambarino/Fraunces italic METALLIC-ORANGE-FOIL headline (3-stop gradient #F2B480→#C2612C→#7A3A13 with specular highlight + 1px darker inner edge reading as embossed copper-foil on matte dark cardstock) 56-72px stacked 1-2 lines LEFT-aligned (subject verbatim — photography-craft), small-caps Geist warm-off-white credit line 18-22px tracked 0.22em (support verbatim) beneath, hairline metallic-teal-foil rule, small-caps Geist muted-teal address line at very bottom. Metallic-GOLD-FOIL Savora seal 64px bottom-right opposite corner. 4-6% film grain on strip only (photo untouched). Exactly ONE foil lockup per post — orange-foil headline carries it.",
        "DEEP TEAL ELEVATED SIDEBAR + CLIENT PHOTO. Client photo fills RIGHT 70% full-scale untouched. LEFT 30% is ELEVATED DEEP TEAL #062423 field with 10-14% tonal gradient (darker toward bottom-left corner). Sidebar contents: small-caps Geist WARM OFF-WHITE #D9D4CE kicker 'SAVORA · ON THE WORK' tracked 0.26em 14-16px at top, hairline metallic-gold-foil rule 50% width, Gambarino/Fraunces italic WARM OFF-WHITE headline 64-88px stacked 3-5 lines tight leading 1.06 (subject verbatim — photography-craft), hairline metallic-teal-foil rule, small-caps Geist MUTED TEAL credit line 18-20px tracked 0.22em (support verbatim), tiny metallic-orange-foil-gradient dot accent (single 8px specular) beside kicker. Bottom of sidebar: Savora wordmark in Gambarino/Fraunces italic warm-off-white 28pt + hairline gold rule + small-caps address. 5-7% film grain on teal field only.",
    ],
    "metric_card": [
        "TABULAR METRIC CARD NEAR-BLACK. Near-black #00060B ground 12% tonal gradient. Top 14%: small-caps Geist MUTED TEAL #7B9693 kicker 'RESULTS · [CLIENT]' tracked 0.26em 14-16px, hairline METALLIC-TEAL-FOIL rule (gradient #2B8C83→#145A55→#073733) at 55% opacity across full width. Middle 55%: HUGE tabular numeral in JetBrains Mono Bold METALLIC-ORANGE-FOIL (3-stop gradient #F2B480→#C2612C→#7A3A13 with specular + 1px darker inner edge, reading as embossed copper-foil) 440-540px line-height 0.95 letter-spacing -0.02em LEFT-aligned at column. Below numeral: small-caps Geist WARM OFF-WHITE unit label 22-26px tracked 0.26em. Lower 25%: Gambarino/Fraunces italic warm-off-white context line 32-42px, hairline metallic-teal-foil rule, small-caps Geist muted-teal WINDOW · [DATE] + caveat italic warm-off-white split 13-15px. Bottom: Savora wordmark Gambarino italic warm-off-white 24pt + tiny metallic-GOLD-FOIL seal opposite corner. NO photo. 6-8% fine film grain. Dark photography-monograph metric plaque.",
        "TABULAR METRIC ELEVATED-TEAL FIELD. Elevated deep-teal #062423 ground 14% tonal gradient (darker bottom-left). Huge warm-off-white JetBrains Mono Bold numeral 440-540px centered. Metallic-gold-foil small-caps unit label beneath. Gambarino/Fraunces italic warm-off-white context line. Hairline metallic-gold-foil rule + small-caps muted-teal WINDOW + caveat italic. Metallic-gold-foil Savora seal bottom-right. 6-8% film grain.",
        "SPLIT-FIELD DARK METRIC. Top 40% near-black #00060B field with small-caps kicker + hairline metallic-teal-foil rule + Gambarino/Fraunces italic warm-off-white context line + WINDOW/caveat strip. Bottom 60% elevated-teal #062423 field with HUGE metallic-orange-foil JetBrains Mono numeral centered + small-caps warm-off-white unit label. Hairline metallic-gold-foil rule at the split. Savora wordmark + gold seal. Dark two-register plaque.",
    ],
    "philosophy_typographic": [
        "GAMBARINO ITALIC MANIFESTO DARK. Near-black #00060B ground 12% tonal gradient. Top 14%: small-caps Geist MUTED TEAL kicker (attribution verbatim) tracked 0.26em 14-16px LEFT-aligned. Hairline METALLIC-TEAL-FOIL rule 35% width (gradient #2B8C83→#145A55→#073733 at 55% opacity). Middle 60%: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL (3-stop gradient #F2B480→#C2612C→#7A3A13 specular + 1px darker inner edge) headline 130-200px stacked 2-3 lines tight leading 1.06 (manifesto line verbatim) LEFT-aligned. Bottom 20%: hairline metallic-gold-foil rule + small-caps Geist WARM OFF-WHITE address line 13-15px tracked 0.22em + Savora wordmark Gambarino italic warm-off-white 30pt. Tiny metallic-gold-foil seal bottom-right. 6-8% film grain. Dark monograph restraint.",
        "OFF-WHITE TYPE ON DARK. Near-black #00060B ground 12% tonal gradient. Small-caps metallic-gold-foil kicker top tracked 0.26em. Gambarino/Fraunces italic WARM OFF-WHITE #F2EFEB headline 140-210px stacked 2-3 lines centered (no foil — pure off-white type for manifesto restraint). Hairline metallic-teal-foil rule + small-caps muted-teal address. Metallic-gold-foil Savora seal. 6-8% film grain.",
        "ELEVATED-TEAL GROUND MANIFESTO. Elevated deep-teal #062423 ground 14% tonal gradient. Small-caps metallic-gold-foil kicker. Gambarino/Fraunces italic warm-off-white OR metallic-orange-foil headline 140-200px stacked 2-3 lines LEFT-aligned (choose foil IF headline is ≤6 words, else off-white). Hairline metallic-gold-foil rule + small-caps warm-off-white address + Savora wordmark. 6-8% film grain.",
    ],
    "service_explainer": [
        "DARK SERVICE CARD MONOGRAPH. Near-black #00060B ground 12% tonal gradient. Top 18%: small-caps Geist MUTED TEAL kicker 'WHAT WE MAKE' tracked 0.26em + hairline METALLIC-TEAL-FOIL rule. Middle 40%: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL service name (3-stop gradient specular) 120-170px stacked 1-2 lines LEFT-aligned. Hairline metallic-gold-foil rule. Lower 30%: small-caps Geist WARM OFF-WHITE inclusions list — each inclusion on its own line with hairline metallic-teal-foil rules between, 22-28px tracked 0.22em, four lines max. Bottom: Savora wordmark Gambarino italic warm-off-white 28pt + tiny metallic-gold-foil seal opposite corner + hairline + small-caps muted-teal address. No photo. NO dollar amounts, NO pricing.",
        "ELEVATED-TEAL SERVICE CARD. Elevated deep-teal #062423 ground 14% tonal gradient. Metallic-gold-foil kicker top. Warm-off-white Gambarino/Fraunces italic service name 120-160px. Warm-off-white small-caps inclusions list hairline metallic-gold-foil rules between. Savora wordmark warm-off-white + gold seal bottom. 6-8% film grain.",
        "TWO-COLUMN DARK SERVICE. Near-black ground 12% tonal gradient. LEFT 45%: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL service name 100-140px stacked. RIGHT 55%: small-caps Geist WARM OFF-WHITE inclusions list stacked, each inclusion on its own line with hairline metallic-teal-foil rules between. Top hairline metallic-gold-foil rule spans full width. Bottom: Savora wordmark + address + gold seal.",
    ],
    "carousel_masthead": [
        "DARK MASTHEAD METALLIC-ORANGE FOIL. Near-black #00060B ground 10% tonal gradient. Full-canvas Gambarino/Fraunces italic METALLIC-ORANGE-FOIL (3-stop gradient #F2B480→#C2612C→#7A3A13 specular + 1px darker inner edge) headline 240-320px stacked 2 lines tight leading 1.0 LEFT-aligned. Hairline METALLIC-TEAL-FOIL rule beneath at 40% canvas width. Small-caps Geist WARM OFF-WHITE #D9D4CE support line 24-30px tracked 0.26em. Tiny metallic-gold-foil kicker 'SAVORA · SWIPE →' bottom-right 14px. Metallic-gold-foil Savora seal bottom-left. 6-8% film grain.",
        "ELEVATED-TEAL MASTHEAD + WARM OFF-WHITE TYPE. Elevated deep-teal #062423 ground 14% tonal gradient. Full-canvas WARM OFF-WHITE #F2EFEB Gambarino/Fraunces italic serif title 240-300px stacked 2 lines tight tracking LEFT-aligned (no foil — pure warm-off-white for elevated-teal register). Hairline metallic-gold-foil rule + small-caps muted-teal support. Small-caps metallic-gold 'SWIPE →' hint at right edge. Savora wordmark + seal. 6-8% film grain.",
        "DARK EDITORIAL TABLE-OF-CONTENTS. Near-black ground 10% gradient. Hairline metallic-teal-foil rules at top, middle, bottom (thin 1px 55% opacity) creating an editorial masthead grid. Between rules: Gambarino/Fraunces italic warm-off-white title + small-caps Geist muted-teal support stacked. Carousel intent — metallic-gold 'SWIPE →' small-caps bottom-right. Tiny metallic-gold seal bottom-left.",
    ],
    "cultural_editorial": [
        "DARK CULTURAL EDITORIAL. Near-black #00060B ground 12% tonal gradient. Top 18%: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL kicker (subject like 'On craft.') 130-170px LEFT-aligned. Hairline METALLIC-TEAL-FOIL rule. Middle 45%: body paragraph in Geist Regular WARM OFF-WHITE #D9D4CE 28-34px 3-4 lines LEFT-aligned with generous leading 1.55, measure capped at 520px. Hairline metallic-gold-foil rule at bottom of body. Bottom 20%: small-caps Geist MUTED TEAL address + Savora wordmark Gambarino/Fraunces italic warm-off-white 28pt. Tiny metallic-gold-foil seal. No illustration. Type-only dark cultural editorial.",
        "ELEVATED-TEAL CULTURAL. Elevated deep-teal #062423 ground 14% tonal gradient. Metallic-gold-foil italic kicker top. Geist Regular warm-off-white body paragraph 3-4 lines centered. Hairline metallic-gold-foil rule + small-caps muted-teal address + gold seal. 6-8% film grain.",
        "DARK SIDEBAR CULTURAL. Near-black ground 12% gradient. LEFT 35%: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL kicker stacked 110-150px. RIGHT 65%: body paragraph Geist Regular warm-off-white. Hairline metallic-teal-foil rule separating columns. Bottom hairline + small-caps muted-teal address + gold seal.",
    ],
    "portfolio_list": [
        "DARK PORTFOLIO LIST MONOGRAPH. Near-black #00060B ground 12% tonal gradient. Top 18%: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL title 170-220px LEFT-aligned + hairline METALLIC-TEAL-FOIL rule. Middle 55%: list of 4 client names in Gambarino/Fraunces italic WARM OFF-WHITE caps 70-92px stacked each on its own line with hairline metallic-teal-foil rules between. Bottom 20%: small-caps Geist muted-teal address + Savora wordmark + tiny metallic-gold-foil seal. Pure dark typographic roster. NO photo.",
        "ELEVATED-TEAL CLIENT ROSTER. Elevated deep-teal #062423 ground 14% tonal gradient. Warm-off-white Gambarino italic title top. Warm-off-white Gambarino italic client names stacked list with hairline metallic-gold-foil rules. Metallic-gold seal + small-caps warm-off-white address at bottom.",
        "DARK TICKER CLIENT ROSTER. Near-black ground 10% gradient. Top: Gambarino/Fraunces italic METALLIC-ORANGE-FOIL title 180-230px. Middle: horizontal ticker banner listing clients separated by hairline metallic-teal-foil dots — 'Blue Mezcal · Jackson House · El Azteca · Taqueria Rojas'. Small-caps warm-off-white. Below: small-caps muted-teal address + Savora wordmark.",
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
            # location_map intentionally dropped — real Middlewood Shopping Center
            # imagery (drone / Google Earth) required before generating map posts
            "menu_highlight_text": BM_MENU_HIGHLIGHTS,
            "campaign_masthead": BM_CAMPAIGN_MASTHEADS,
            # Review cards pulled from BM_REVIEW_CARDS — subject = star count,
            # support = the review quote itself (treated as headline)
            "review_card": [(stars, quote) for (_, stars, quote, _) in BM_REVIEW_CARDS],
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
            ("review_card", 4, "no_photo"),
            ("menu_highlight_text", 2, "no_photo"),
        ],
        "angles": ANGLES_BM,
    },
    "jackson_house": {
        "stem_default": "jackson_house_tavern",
        "assets": {
            "food_hero": JH_FOOD_IMAGES,
            # cocktail_selena is CAROUSEL-FINALE ONLY. Not standalone. Always
            # pair with real drink photos in carousel position 1–2.
            "cocktail_selena_finale": JH_COCKTAILS_NO_PHOTO,
            "typography_first": JH_DICHOS,
            "flyer": JH_FLYERS,
            "carousel_masthead": JH_CAMPAIGN_MASTHEADS[:6],
            "utility": JH_UTILITY,
            "multi_dish_showcase": JH_MENU_HIGHLIGHTS,
            "cultural": JH_CULTURAL,
            # location_map dropped — need real Google Earth / drone shots
            "menu_highlight_text": JH_MENU_HIGHLIGHTS,
            "campaign_masthead": JH_CAMPAIGN_MASTHEADS,
        },
        "mix": [
            ("food_hero", 30, "photo"),  # raised — hero food is the strongest JH move
            ("cocktail_selena_finale", 10, "no_photo"),  # reduced — carousel-finale only
            ("typography_first", 12, "no_photo"),
            ("flyer", 10, "no_photo"),
            ("carousel_masthead", 8, "no_photo"),
            ("utility", 6, "no_photo"),
            ("multi_dish_showcase", 5, "no_photo"),
            ("cultural", 10, "no_photo"),
            ("menu_highlight_text", 5, "no_photo"),
            ("campaign_masthead", 4, "no_photo"),
        ],
        "angles": ANGLES_JH,
    },
    "savora": {
        "stem_default": "savora_studio",
        "assets": {
            "hero_photograph": SAVORA_HERO_PHOTOS,
            "metric_card": SAVORA_METRIC_CARDS,
            "philosophy_typographic": SAVORA_PHILOSOPHY,
            "service_explainer": SAVORA_SERVICE_CARDS,
            "carousel_masthead": SAVORA_CAMPAIGN_MASTHEADS,
            "cultural_editorial": SAVORA_CULTURAL,
            "portfolio_list": SAVORA_PORTFOLIO_LIST,
            # BLOCKED Phase A (pending assets):
            # "bts_process": (needs BTS Cloudinary uploads)
            # "tool_still_life": (needs studio tool imagery)
            # "founder_portrait": (needs Hector portrait session)
            # "testimonial_card": (needs signed client quotes)
            # "case_study_carousel": (needs multi-image runner + before/after pairs)
            # "portfolio_split_2" / "portfolio_split_3": (needs multi-image runner)
        },
        "mix": [
            ("hero_photograph", 60, "photo"),     # the core — Savora IS portfolio
            ("philosophy_typographic", 15, "no_photo"),
            ("metric_card", 10, "no_photo"),      # selective, real metrics only
            ("carousel_masthead", 6, "no_photo"),
            ("service_explainer", 4, "no_photo"),
            ("cultural_editorial", 3, "no_photo"),
            ("portfolio_list", 2, "no_photo"),
        ],
        "angles": ANGLES_SAVORA,
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
            # location_map dropped — need real Google Earth / drone shots of
            # Camden + Dover + Rehoboth locations before generating map posts
            "menu_highlight_text": AZ_MENU_HIGHLIGHTS,
            "campaign_masthead": AZ_CAMPAIGN_MASTHEADS,
        },
        "mix": [
            ("food_hero", 30, "photo"),
            ("drink_hero", 10, "photo"),
            ("typography_first", 10, "no_photo"),
            ("flyer", 15, "no_photo"),
            ("carousel_masthead", 8, "no_photo"),
            ("utility", 6, "no_photo"),
            ("multi_dish_showcase", 8, "no_photo"),
            ("cultural", 8, "no_photo"),
            ("menu_highlight_text", 5, "no_photo"),
        ],
        "angles": ANGLES_AZ,
    },
}


# ============================================================
# POST CONFIG GENERATION
# ============================================================

def _approved_subjects(brand: str) -> set:
    """Subjects already approved in OUTPUT/PICKS/{brand}/ — skip in next batch."""
    picks = ROOT / "OUTPUT" / "PICKS" / brand
    if not picks.exists():
        return set()
    approved = set()
    for f in picks.iterdir():
        if not f.name.endswith(".png"):
            continue
        parts = f.name.split("_")
        if len(parts) < 3:
            continue
        batch = parts[1]
        plog = ROOT / "OUTPUT" / "nano_banana" / brand / batch / "prompts.jsonl"
        if plog.exists():
            try:
                d = json.loads(plog.read_text().strip())
                approved.add(d.get("subject", ""))
            except Exception:
                pass
    return {s for s in approved if s}


# ============================================================
# AVANT-GARDE ANGLES (rule-breaking experimentation, brand-voice preserved)
# ============================================================

AVANT_ANGLES = {
    "blue_mezcal": [
        "FULL-BLEED SINGLE-COLOR WASH. Entire canvas saturated cobalt #1E3A8A with 15% tonal gradient + heavy film grain. The photo is silhouetted to a pure cobalt matte on cobalt background — the outline/depth reads via subtle shadow only. Warm cream type 'SUBJECT' oversized (300px+) wraps around the invisible silhouette. Inverse-portrait mood. Editorial jazz-album register.",
        "MAGAZINE SPREAD DOUBLE-PAGE. Left 50% full-bleed photo, right 50% warm cream with a single oversized italic Canela pull-quote drawn from support copy at 180-220px cobalt. Hairline cobalt rule down the gutter. Tiny folio top-left. Editorial.",
        "EXTREME CLOSE-CROP + ALL-CAPS GIANT WORD. Photo cropped so tight it becomes abstract texture (65-75% canvas). One GIANT cream word drawn from subject in GT Sectra caps at 480px+ sitting across the crop like billboard type. Brand palette only. Bold.",
        "HALFTONE NEWSPRINT. Photo converted to heavy halftone screen pattern in cobalt ink on warm cream. Type as newspaper masthead caps. Tiny byline + date at top. Editorial-jazz register.",
        "RISO ZINE POSTER. Photo rendered as 2-ink riso (cobalt + marigold) with visible misregistration and screen texture. Bold caps headline. Paper-grain ground. Zine-print feel.",
        "VERTICAL TICKER-TAPE TYPE. Photo occupies left 40% full-bleed. Right 60% is a vertical running banner of repeating subject name in small-caps cobalt on cream, row-after-row, 40 rows. Editorial OCD.",
        "PAINTED BRUSH POSTER. Photo cut out and painted over with gouache brush-strokes in cobalt+cream — the drink becomes a painted gesture not a photo. One italic serif line. Gallery-print register.",
        "BRUTALIST TYPE WALLPAPER + CUTOUT. Bone-cream canvas tiled with subject name repeating in cobalt italic GT Sectra 90-110px zigzag. Center: rectangular knockout window with silhouetted photo inside. Brutalist editorial.",
        "DIAGONAL COLOR-BLOCK SPLIT. Canvas split at a 25° diagonal — cobalt upper-right, cream lower-left. Photo bridges the diagonal. Italic serif 'subject' at the seam. Bold geometry.",
        "TYPOGRAPHIC POSTER NO PHOTO. Full-canvas cobalt ground. ONE MASSIVE ITALIC CANELA WORD (drawn from subject) at 600px+ in warm cream, slightly rotated, tight tracking, partial letter bleed off canvas. Small support line in marigold. Type-only cultural editorial.",
    ],
    "jackson_house": [
        "WARM CREAM DOMINANT EDITORIAL (the 5-star direction Hector flagged). Warm cream #F2EADF ground 8-12% paper-gradient. Italic Caslon serif in deep charcoal 200-260px stacked 2 lines tight leading 1.0. Photo cut-out centered in lower 45%. Small-caps charcoal support. Brass hairline rules. 5-7% paper-grain. NO charred-black ground — lean into cream-first heritage.",
        "OXBLOOD + CREAM EDITORIAL. Deep oxblood #5B1A1A 12% gradient top 35%, warm cream ground 65% bottom. Photo bridges the seam. Brass-foil italic serif in oxblood zone, charcoal in cream zone. Heritage editorial.",
        "FOREST GREEN MAGAZINE SPREAD. Forest green #1F3B2D 10% gradient. Warm-cream italic Farnham 260-320px stacked 2 lines centered. Photo cut-out lower third. Heritage-luxe alt palette.",
        "VINTAGE MENU CARD. Warm cream ground + hand-drawn engraved BORDER around the entire canvas in charcoal hairline ink. Photo cut-out center. Farnham italic subject + small-caps support inside the frame. Gage & Tollner feel.",
        "DARK-ON-DARK BRASS POSTER. Charred-black ground + oxblood sub-field corner. Brass-foil gradient serif 280-340px asymmetric. Photo cut-out. Small-caps cream support. Film grain. Moody jazz-album.",
        "GIANT TYPE WRAPS PHOTO. Warm-cream ground. Oversized Farnham italic caps (subject) 400-500px filling upper 60%, letters wrapping around a silhouetted photo in the lower third. Type-as-composition.",
        "ETCHED ENGRAVING FULL EDITORIAL. Warm cream ground. Hand-etched engraving of the dish in charcoal hairline ink REPLACING the photo entirely. Italic Caslon title + body paragraph. 19th-century menu card feel.",
        "SCRIPT+SERIF SANDWICH CAPS. Warm cream ground. TOP: script Farnham Italic 'subject' 140-180px. Photo cut-out middle. BOTTOM: serif caps 'subject' at 1.5x scale. Photo sandwiched between two typographic treatments. Frenchette move.",
        "DATELINE FOLIO HEAVY. Warm cream ground. Small-caps DATELINE across top ('JACKSON HOUSE · SPRING 2026 · VOL ONE'). Photo mid-canvas. Italic Caslon pullquote below. Small-caps credits bottom. Magazine-editorial discipline.",
        "METALLIC BRASS TYPE ON CREAM (inverse). Warm cream #F2EADF ground. Brass-foil gradient italic Farnham serif 260-320px stacked. Photo cut-out. Small-caps charcoal support. No black ground at all — brass on cream reads as printed menu.",
    ],
    "azteca": [
        "RISO ZINE MAXIMAL. Warm masa cream ground with heavy paper-fiber texture. Photo rendered as 2-ink riso print — chile red + green halftone with misregistration. Cooper Black caps masthead chile-red. Warrior logo corner verbatim. Handmade zine energy.",
        "OVERSIZED CHUNKY CAPS WRAP PHOTO. Masa cream ground. 'SUBJECT' in chunky Cooper Black chile-red 500px+ filling upper 65%, letters wrapping a silhouetted photo in lower 35%. Type as composition.",
        "GREEN + CREAM + SMALL RED. Forest green #2F7A3A ground 10% gradient top 40%, masa cream lower 60%. Photo cut-out bridges. Warm cream chunky caps title. Tiny chile-red accent circular badge. Warrior logo corner. Mexican-flag confidence without the cliché.",
        "PAPER-CUTOUT COLLAGE. Masa cream ground. Hand-cut paper collage look — chile-red paper agave shape, green paper corn shape, photo silhouetted as if glued on. Warrior logo corner. Kindergarten-craft meets editorial.",
        "FULL-BLEED CHILE RED WASH. Chile-red #E63946 ground FULL canvas with 15% tonal gradient + halftone dots. Photo silhouetted in masa cream matte. Cooper Black cream caps 400px+. Bold-maximalist.",
        "PAPEL PICADO FRAME + CENTER PHOTO. Masa cream ground. Hand-illustrated papel-picado cutout border all four edges in chile-red + green. Photo cut-out dead-center. Small chunky caps title below. Warrior logo bottom.",
        "BRIGHT DAYLIGHT TYPOGRAPHIC POSTER. Full canvas chile-red + green + cream stripes (Mexican-flag abstraction) with Cooper Black caps 'SUBJECT' straddling the stripes. Halftone overlay. Photo cut-out in center. Warrior logo. Street-poster energy.",
        "COBALT + MARIGOLD MAXIMAL. Cobalt #1A3FA8 ground. Marigold #FFD400 chunky caps subject title 320px+ stacked. Photo cut-out center. Warrior logo corner. Papel-picado hand-drawn accent. Bold color shift from cream register.",
        "HAND-PAINTED BRUSH WORDMARK ON CREAM. Masa cream ground. Single word of subject painted as HAND-PAINTED BRUSH STROKE in chile-red gouache + visible splatter + bleed. Photo cut-out below. Warrior logo corner. Painterly not digital.",
        "FAMILY PORTRAIT SCENE COMPOSITION. Masa cream ground. Multiple dish photos arranged bento-magazine-spread style (3-4 dishes composed like a magazine page). Chunky caps title top. Warrior logo corner. Small-caps dish-names floating beside each photo. Magazine food-editorial register.",
    ],
}


def build_post_configs(brand: str, target_count: int, avant: bool = False) -> list[dict]:
    """Generate target_count post configs for brand, rotating assets + angles.

    Asset pools are SHUFFLED per-batch (time-seeded) AND subjects already in
    OUTPUT/PICKS/{brand}/ are EXCLUDED so every batch surfaces fresh content.

    If avant=True, use AVANT_ANGLES pool (experimental, rule-breaking) instead
    of the standard ANGLES dict.
    """
    plan = BRAND_PLANS[brand]
    assets = plan["assets"]
    angles = plan["angles"]
    mix = plan["mix"]

    # Time-seeded RNG — different shuffle each run
    rng = random.Random(time.time_ns())

    # Already-approved subjects to skip this batch
    skip_subjects = _approved_subjects(brand)
    if skip_subjects:
        print(f"[{brand}] excluding {len(skip_subjects)} already-approved subjects")

    # Avant-garde pool (shared across all content types for this run)
    avant_pool = AVANT_ANGLES.get(brand, []) if avant else []
    if avant:
        print(f"[{brand}] AVANT MODE — using {len(avant_pool)} rule-breaking angles")

    # Scale mix to target_count
    total_pct = sum(c for _, c, _ in mix)
    configs = []
    post_idx = 1

    for ct_name, ct_count, mode in mix:
        scaled = max(1, int(round(ct_count * target_count / total_pct)))
        asset_pool = list(assets.get(ct_name, []))
        angle_pool = list(avant_pool if avant else
                          angles.get(ct_name, ["Clean editorial layout. Brand palette. Typographic hierarchy."]))
        if not asset_pool:
            continue
        # Filter out already-approved subjects (match by subject string)
        def _sub(a):
            return a[1] if mode == "photo" else a[0]
        filtered = [a for a in asset_pool if _sub(a) not in skip_subjects]
        if filtered:
            asset_pool = filtered
        # Shuffle pools so new/unused dishes surface early in every batch
        rng.shuffle(asset_pool)
        rng.shuffle(angle_pool)
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
                "quote_post" if ct_name in ("typography_first", "philosophy_typographic") else
                "quote_post" if ct_name == "metric_card" else
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
    parser.add_argument("--avant", action="store_true",
                        help="AVANT-GARDE mode — replaces standard angles with rule-breaking experimental angles")
    args = parser.parse_args()

    brands = list(BRAND_PLANS.keys()) if args.brand == "all" else [args.brand]

    # In avant mode, skip brands with no avant pool (e.g. savora)
    if args.avant:
        brands = [b for b in brands if AVANT_ANGLES.get(b)]
        if not brands:
            sys.exit("No brands have avant-garde angles defined.")

    all_configs = []
    for b in brands:
        configs = build_post_configs(b, args.count, avant=args.avant)
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
