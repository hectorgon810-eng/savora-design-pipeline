# MASTER BUILD FILE — Blue Mezcal Management Group
# Updated April 14, 2026 — ALL QUESTIONS RESOLVED
# Drop this file into Claude Code to build Vista Social CSVs
# This is the SINGLE SOURCE OF TRUTH. Supersedes all prior handoff files.

---

## PROJECT OVERVIEW

Three restaurants, all in Delaware. Building Vista Social CSVs for Instagram bulk scheduling.
Posting schedule: Monday + Friday at 11:30 AM for all three.
All images hosted on Cloudinary (uploaded and live as of April 14, 2026).

---

## RESTAURANTS

1. JACKSON HOUSE (@jacksonhousede)
   - Elevated comfort food + cocktails
   - 17 Wood St, Middletown, DE 19709
   - CTA: Reserve your table | link in bio 📍
   - Caption format: [Dish Name]. [emoji] → punchy line → 📍 address → CTA

2. BLUE MEZCAL (@bluemezcalrestaurant)
   - Mexican restaurant, new menu launching May 5, 2026
   - 826 Kohl Ave, Middletown, DE 19709
   - CTA: Visit us | link in bio 📍
   - Caption format: [Dish Name]. [emoji] → punchy line → 📍 address → CTA

3. AZTECA (@aztecadelaware + @aztecarestaurantrehoboth)
   - Mexican, sister to Blue Mezcal
   - @aztecadelaware covers: 859 N. DuPont Hwy, Dover, DE 19901 + 511 S. Red Haven Ln, Camden/Dover, DE 19901
   - @aztecarestaurantrehoboth: 20672 Coastal Highway, Rehoboth Beach, DE 19971
   - CTA: Find your nearest location | link in bio 📍
   - Same Mon/Fri posting days as other restaurants. No stagger.

---

## CROSS-POSTING RULES

- Azteca food content CAN go on Blue Mezcal
- Azteca cocktails CAN go on Blue Mezcal (CONFIRMED)
- Blue Mezcal NEW menu food (B-44+) is EXCLUSIVE to Blue Mezcal — NEVER on Azteca
- Blue Mezcal cocktails (B-series, no Azteca logo) = Blue Mezcal only
- Millionaire Margarita El Azteca logo (B-21–29) = Blue Mezcal only
- Millionaire Margarita Azteca logo (B-30–32) = ALL THREE accounts
- Table spreads with cocktails (AZ-20, AZ-46, AZ-72) = Azteca + Blue Mezcal

---

## IMAGE HOSTING — CLOUDINARY (LIVE)

Cloud name: dkp42tunc
All images compressed and uploaded as of April 14, 2026.

Cloudinary folders + URL pattern:
- jackson-house/ → https://res.cloudinary.com/dkp42tunc/image/upload/jackson-house/{FILENAME}.jpg
- blue-mezcal/ → https://res.cloudinary.com/dkp42tunc/image/upload/blue-mezcal/{FILENAME}.jpg
- azteca/ → https://res.cloudinary.com/dkp42tunc/image/upload/azteca/{FILENAME}.jpg

Examples:
- https://res.cloudinary.com/dkp42tunc/image/upload/jackson-house/Savora-50.jpg
- https://res.cloudinary.com/dkp42tunc/image/upload/blue-mezcal/B-3.jpg
- https://res.cloudinary.com/dkp42tunc/image/upload/azteca/AZ-1.jpg

NOTE: Filenames are case-sensitive. Use exact names as listed in post tables below.
NOTE: Jackson House T-series images (T-1 through T-108) are in the jackson-house/ Cloudinary folder.
NOTE: B-30, B-31, B-32 (Millionaire Margarita Azteca logo) are in the blue-mezcal/ folder but post to all 3 accounts.

---

## VISTA SOCIAL CSV FORMAT

```
Date,Time,Message,Images,instagram_publish_as
MM/DD/YYYY,11:30 AM,"Caption text","image_url_1,image_url_2",POST
```

Rules:
- For carousels: comma-separate image URLs in the Images column
- Emojis: use Google Sheets (not Excel)
- Max 200 rows per CSV, recommend 100
- One CSV per Instagram account (5 total: jacksonhousede, bluemezcalrestaurant, aztecadelaware, aztecarestaurantrehoboth, plus cross-posts)
- All posts at 11:30 AM
- Posting days: Monday + Friday only

---

## IMAGE ORIENTATION TAGS

Code MUST enforce: no carousel mixes H (horizontal) and V (vertical) images.
Lead image sets the ratio. All slides must match orientation.

### AZTECA ORIENTATIONS
AZ-1:H, AZ-2:V, AZ-3:H, AZ-4:H, AZ-5:V, AZ-6:V, AZ-7:V, AZ-8:H, AZ-9:H, AZ-10:H
AZ-11:H, AZ-12:H, AZ-13:H, AZ-14:V, AZ-15:H, AZ-16:H, AZ-17:V, AZ-18:V, AZ-19:V, AZ-20:H
AZ-21:H, AZ-22:H, AZ-23:H, AZ-24:H, AZ-25:H, AZ-26:H, AZ-27:H, AZ-28:H, AZ-29:H, AZ-30:V
AZ-31:V, AZ-32:H, AZ-33:H, AZ-34:H, AZ-35:H, AZ-36:H, AZ-37:H, AZ-38:H, AZ-39:H, AZ-40:H
AZ-41:H, AZ-42:V, AZ-43:V, AZ-44:V, AZ-45:H, AZ-46:H, AZ-47:H, AZ-48:H, AZ-49:H, AZ-50:H
AZ-51:H, AZ-52:H, AZ-53:V, AZ-54:V, AZ-55:H, AZ-56:H, AZ-57:H, AZ-58:H, AZ-59:H, AZ-60:H
AZ-61:H, AZ-62:H, AZ-63:H, AZ-64:H, AZ-65:V, AZ-66:V, AZ-67:V, AZ-68:H, AZ-69:H, AZ-70:H
AZ-71:H, AZ-72:H, AZ-73:H, AZ-74:V, AZ-75:H, AZ-76:H, AZ-77:V, AZ-78:V, AZ-79:V, AZ-80:H
AZ-81:H, AZ-82:H, AZ-83:H, AZ-84:H, AZ-85:H, AZ-86:H, AZ-87:H, AZ-88:H, AZ-89:V, AZ-90:V
AZ-91:V, AZ-92:V, AZ-93:H, AZ-94:H, AZ-95:H, AZ-96:H, AZ-97:H, AZ-98:H, AZ-99:H, AZ-100:H
AZ-101:V, AZ-102:V, AZ-103:V, AZ-104:H, AZ-105:H

### BLUE MEZCAL ORIENTATIONS
B-1:H, B-2:V, B-3:H, B-4:V, B-5:V, B-6:V, B-7:V, B-8:V, B-9:H, B-10:H
B-11:H, B-12:H, B-13:H, B-14:V, B-15:V, B-16:V, B-17:V, B-18:V, B-19:V, B-20:H
B-21:V, B-22:V, B-23:H, B-24:H, B-25:V, B-26:V, B-27:V, B-28:V, B-29:V, B-30:V
B-31:V, B-32:H, B-33:H, B-34:H, B-35:H, B-36:H, B-37:H, B-38:H, B-39:H, B-40:H
B-41:H, B-42:V, B-43:V, B-44:H, B-45:H, B-46:H, B-47:H, B-48:H, B-49:H, B-50:H
B-51:H, B-52:H, B-53:V, B-54:V, B-55:V, B-56:H, B-57:H, B-58:H, B-59:H, B-60:H
B-61:H, B-62:H, B-63:H, B-64:H, B-65:V, B-66:V, B-67:V, B-68:H, B-69:H, B-70:H
B-71:V, B-72:H, B-73:H, B-74:H, B-75:V, B-76:V, B-77:V, B-78:H, B-79:H, B-80:H
B-81:H, B-82:H, B-83:H, B-84:H, B-85:H, B-86:H, B-87:H, B-88:H, B-89:H, B-90:V
B-91:V, B-92:H, B-93:H, B-94:H

### JACKSON HOUSE / SAVORA ORIENTATIONS
Savora-31:H, Savora-32:H, Savora-33:H, Savora-34:H, Savora-35:H, Savora-36:H
Savora-37:H, Savora-38:H, Savora-39:H, Savora-40:H, Savora-41:V, Savora-42:H
Savora-43:H, Savora-44:H, Savora-45:H, Savora-46:H, Savora-47:H, Savora-48:H
Savora-49:H, Savora-50:H, Savora-51:H, Savora-52:H, Savora-53:H, Savora-54:H
Savora-55:H, Savora-56:H, Savora-57:H, Savora-58:H, Savora-59:H, Savora-60:H
Savora-61:H, Savora-62:H, Savora-63:H, Savora-64:V, Savora-65:H, Savora-66:H
Savora-67:V, Savora-68:H, Savora-69:H, Savora-70:V, Savora-71:H, Savora-72:H
Savora-73:H, Savora-74:H, Savora-75:H

### JACKSON HOUSE / T-SERIES ORIENTATIONS
(All T-series images are solo posts or same-orientation carousels — no conflicts flagged)
T-series orientation data not individually logged. Assume H unless image is clearly portrait.
Code should verify orientation at build time if possible.

---

## COMPLETE POST TABLES — READY TO SCHEDULE

Each table below = one Instagram post. Code builds one CSV row per post.
Orientation conflicts have been PRE-RESOLVED. All carousels below are orientation-safe.

=============================================================
## JACKSON HOUSE — @jacksonhousede
=============================================================

### JH-1 | Dilly Dally Dirty Martini
Images: T-13 (lead), T-14, T-15
Caption:
Dilly Dally Dirty Martini. 🍸

You already know.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-2 | Burrata
Images: Savora-31 (solo)
Caption:
Burrata. 🍅

Heirloom tomatoes, fresh burrata, basil, balsamic.
Some things don't need to be complicated.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-3 | Fried Okra
Images: T-46 (solo)
Caption:
Fried Okra. 🌿

Crispy, golden, and gone before you know it.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-4 | Cornbread Muffins
Images: T-48 (solo)
Caption:
Cornbread Muffins. 🧈

Warm out of the oven. Butter melts on contact.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-5 | Fried Catfish Fingers
Images: T-49 (solo)
Caption:
Fried Catfish Fingers. 🐟

Crispy, golden, mustard dipping sauce.
Southern comfort, Jackson House style.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-6 | House Guacamole
Images: T-81 (lead), T-82
Caption:
House Guacamole. 🥑

Fresh, seasonal, made to order.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-7 | Fried Chicken Wings
Images: T-78 (lead), T-79
Caption:
Fried Chicken Wings. 🍗

Chili-soy dipping sauce. Dark, crispy, built for sharing.
(Nobody actually shares though.)

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-8 | Lobster & Shrimp Orzo
Images: Savora-48 (lead), Savora-49
Caption:
Lobster & Shrimp Orzo. 🦞

Shaved parm. Herb bread roll. This one has regulars.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-9 | Lobster Roll
Images: T-61 (solo)
Caption:
Lobster Roll. 🦞

Toasted brioche. Cream sauce. Chives. Charred lemon.
New on the menu. Already a favorite.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-10 | Summer Scallops
Images: T-64 (lead), T-65
Caption:
Summer Scallops. 🌊

Seared scallops, creamy corn, crab, and an edible flower.
Summer never looked this good.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-11 | Elote Burger
Images: T-70 (lead), T-67
Caption:
Elote Burger. 🍔🌽

We're not going to explain this one.
Just order it.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-12 | Chimichurri Steak
Images: T-72 (lead), T-74
Caption:
Chimichurri Steak. 🥩

Sliced, sauced, and plated like it means it.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-13 | Fried Chicken Wrap
Images: T-83 (solo)
Caption:
Fried Chicken Wrap. 🌯

Cut in half so you can see exactly what's inside.
Spoiler: it's everything.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-14 | Orecchiette
Images: T-87 (solo)
Caption:
Orecchiette. 🍝

Spicy sausage, rapini, white beans, poached egg, edible flower.
Pasta night, elevated.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-15 | Linguine
Images: T-89 (lead), T-91
Caption:
Linguine. 🍝

Cream sauce, shaved parm, cherry tomatoes, red edible flower.
Simple. Stunning. Yours.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-16 | Grilled Chicken Tacos
Images: T-94 (lead), T-96
Caption:
Grilled Chicken Tacos. 🌮

Pineapple mango salsa. Pickled jalapeños. Chips on the side.
The taco you didn't know you needed.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-17 | Mixed Greens Salad
Images: T-75 (lead), T-77
Caption:
Mixed Greens. 🫐

Blueberries, cucumber, candied walnuts, goat cheese, balsamic.
The salad that makes salad people out of non-salad people.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-18 | Berry Chantilly Cake
Images: T-104 (lead), T-98
Caption:
Berry Chantilly Cake. 🍰

Layered cream cake, mixed berry crown, fresh mint.
Save room. You'll want to save room.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-19 | Strawberry Layer Cake
Images: T-101 (solo)
Caption:
Strawberry Layer Cake. 🍓

Tall, layered, and draped in strawberry glaze.
This one photographs itself.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-20 | Peach Cobbler
Images: T-108 (lead), T-107
Caption:
Peach Cobbler. 🍑

Caramelized peach compote, graham cracker crumble, whipped cream.
Warm, sweet, and worth every bite.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-21 | Heard's The Last Word
Images: T-9 (solo)
Caption:
Heard's The Last Word. 🍹

Chili rim. Charred lime. Bold from the first sip.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-22 | La Ultima
Images: T-16 (solo)
Caption:
La Ultima. 🍸

Green olives. Purple velvet vibes.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-23 | Toast Of The Town (Brunch)
Images: T-17 (solo)
Caption:
Toast Of The Town. 🍷

Berry, dried citrus, blue velvet background.
Pretty enough to stop the scroll.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-24 | Nada De Mango (Mocktail)
Images: T-24 (solo)
Caption:
Nada De Mango. 🍈

Umbrella, lime, warm neon glow.
The weekend starts here.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-25 | Spritz From Switz (Brunch)
Images: T-28 (solo)
Caption:
Spritz From Switz. 🫧

Globe glass. Orange and purple. Lounge chair energy.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-26 | One In A Melon (Mocktail)
Images: T-33 (solo)
Caption:
One In A Melon. 🍈

Orange-red gradient, pineapple, umbrella. Golden bar light.
Vacation in a glass.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-27 | Grapefruitty Tuti (Mocktail) — TOP PICK
Images: T-36 (solo)
Caption:
Grapefruitty Tuti. 🌸

Purple edible flower. Blue velvet background.
This one doesn't need a caption.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-28 | Full Cocktail Lineup
Images: T-39 (solo)
Caption:
New cocktail menu. 🍹

Every single one, in one shot.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-29 | Guest Holding Spritz Glasses
Images: T-56 (solo)
Caption:
Good drinks, better company. 🥂

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-30 | Full Team Shot
Images: T-40 (solo)
Caption:
The team behind the table. 🌿

Named Best New Restaurant in Delaware — Delaware Today 2025.
We're just getting started.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-31 | Training Carousel (BTS)
Images: T-41 (lead), T-44, T-43
Caption:
Behind the bar. 👀

Every great cocktail starts with a team that cares.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-32 | Shrimp & Lobster Scampi (NEW — Savora batch)
Images: Savora-50 (solo)
Caption:
Shrimp & Lobster Scampi. 🦞

Butter. Garlic. Lobster. Shrimp.
Some dishes don't need a long description.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-33 | Blueberry Balsamic Salad (NEW — Savora batch)
Images: Savora-54 (lead), Savora-51
All H orientation ✅
Caption:
Blueberry Balsamic Salad. 🫐

Mixed greens, grilled shrimp, blueberries, balsamic drizzle.
Light, bright, and worth every bite.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-34 | Wings (NEW — Savora batch)
Images: Savora-63 (lead), Savora-58
All H orientation ✅
Caption:
Wings. 🍗

Crispy, sauced, and gone before you blink.
Ask your server about the flavors.

📍 17 Wood St, Middletown, DE 19709
Reserve your table | link in bio 📍

---

### JH-HOLD-1 | Bone-in Ribeye — DO NOT SCHEDULE
Savora-40 + Savora-36 — Bison Ribeye posted Apr 8. Don't re-post solo.

### JH-HOLD-2 | Table Spread — DO NOT SCHEDULE YET
Savora-64–68 — Contains Bison Ribeye. Hold for future carousel.

### JH-HOLD-3 | Passionfruit Salmon — DO NOT SCHEDULE
Savora-69 — Already posted Mar 25.

---

=============================================================
## BLUE MEZCAL — @bluemezcalrestaurant
=============================================================

### COCKTAILS

### BM-1 | Cucumber Margarita
Images: B-3 (lead), B-1
⚠️ ORIENTATION: B-3:H, B-1:H ✅
Caption:
Cucumber Margarita. 🥒

Black salt rim. Cucumber crown. Cool and dangerous.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-2 | Spicy Margarita
Images: B-7 (lead), B-8
⚠️ ORIENTATION FIX: Original had B-11 (H) as slide with B-7 (V) lead. FIXED: Use B-8 (V) instead of B-11.
B-7:V, B-8:V ✅
Caption:
Spicy Margarita. 🌶️

Chili-Tajín rim. Pineapple leaf. Built for heat seekers.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-3 | Espresso Martini
Images: B-19 (lead), B-14
⚠️ ORIENTATION FIX: Original had B-20 (H) as slide. FIXED: Drop B-20, use B-14 (V) only.
B-19:V, B-14:V ✅
Caption:
Espresso Martini. ☕

Foam so good it has its own fan club.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-4 | Millionaire Margarita (El Azteca Logo — BM ONLY)
Images: B-22 (lead), B-21
B-22:V, B-21:V ✅
Caption:
Millionaire Margarita. 💰

Gold rim. Zero apologies.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-5 | Millionaire Margarita (Azteca Logo — CROSS-POST ALL 3)
Images: B-30 (lead), B-31
⚠️ ORIENTATION FIX: Original had B-32 (H) as slide. FIXED: Drop B-32, keep B-31 (V).
B-30:V, B-31:V ✅
POST TO: @bluemezcalrestaurant + @aztecadelaware + @aztecarestaurantrehoboth
Caption for Blue Mezcal:
Millionaire Margarita. 💰

Gold rim. Zero apologies.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

Caption for Azteca accounts:
Millionaire Margarita. 💰

Gold rim. Dehydrated orange. Pure Azteca.

Find your nearest location | link in bio 📍

---

### BM-6 | HOMBRE Old Fashioned
Images: B-35 (lead), B-36, B-33
B-35:H, B-36:H, B-33:H ✅
Caption:
HOMBRE Old Fashioned. 🥃

Branded ice cube. Bourbon underneath.
This is the one you order when you mean it.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-7 | BAD HOMBRE Frozen Tray
Images: B-41 (lead), B-40, B-38
B-41:H, B-40:H, B-38:H ✅
Caption:
BAD HOMBRE Tray. 🥶

Four frozen drinks. One tray. Bring the crew.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-8 | Full Bar Lineup (New Menu Announcement)
Images: B-43 (solo)
B-43:V
Caption:
New menu. New era. 🍹

Every cocktail, in one shot. May 5 — mark it.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### FOOD — BLUE MEZCAL EXCLUSIVE (DO NOT CROSS-POST TO AZTECA)

### BM-9 | Raw Oysters
Images: B-47 (lead), B-50, B-44
B-47:H, B-50:H, B-44:H ✅
Caption:
Raw Oysters. 🦪

Six count. Mexican style. Tajín, Chamoy Chipotle sauce, lime.
This is the move.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-10 | Seafood Parillada
Images: B-57 (lead), B-56, B-60, B-61
⚠️ ORIENTATION FIX: Original had B-55 (V) as slide. FIXED: Drop B-55.
B-57:H, B-56:H, B-60:H, B-61:H ✅
Caption:
Seafood Parillada. 🥩🦐🦪

Steak. Shrimp. Baked oysters with chorizo. Grilled poblano.
All on one board. All for you.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-11 | Guacamole with Chicharrón
Images: B-64 (lead), B-62
B-64:H, B-62:H ✅
Caption:
Made to Order Guacamole. 🥑

With chicharrón, cotija, and cilantro.
The upgrade you didn't know you needed.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-12 | Guacamole with Crudités
Images: B-70 (lead), B-68
⚠️ ORIENTATION FIX: Original had B-66 (V) as slide. FIXED: Drop B-66.
B-70:H, B-68:H ✅
NOTE: B-67 confirmed as duplicate of B-70. Dropped.
Caption:
Made to Order Guacamole. 🥑

Fresh, customizable, and now with crudités.
Dip accordingly.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-13 | Full Table Spread (May 5 Launch)
Images: B-72 (lead), B-74
B-72:H, B-74:H ✅
Caption:
May 5. New menu. New Blue Mezcal. 🌵

Everything you see — launching soon.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-14 | Ramen Birria
Images: B-79 (lead), B-81
⚠️ Lead swapped to B-79 per Q13 resolution. Was B-81.
B-79:H, B-81:H ✅
Caption:
Ramen Birria. 🍲

Rich birria broth. Noodles. Lime, cilantro, onion on the side.
Soul in a bowl.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-15 | Street Tacos
Images: B-85 (lead), B-84, B-83
B-85:H, B-84:H, B-83:H ✅
Caption:
Street Tacos. 🌮

Six on a plate. Salsa roja in the center.
The classic, done the Blue Mezcal way.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-16 | Cheesy Burrito
Images: B-89 (lead), B-88
B-89:H, B-88:H ✅
Caption:
Cheesy Burrito. 🌯

Smothered in white queso, topped with pico, rice and beans on the side.
New menu. New obsession.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-17 | Enchiladas Verdes
Images: B-92 (solo)
⚠️ ORIENTATION FIX: Original had B-91 (V) as slide with B-92 (H) lead. FIXED: Post B-92 solo.
B-92:H ✅
Caption:
Enchiladas Verdes. 🌿

Green tomatillo sauce. Shredded cotija. Rice on the side.
Clean, bright, and everything right.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-18 | Alitas
Images: B-94 (lead), B-93
B-94:H, B-93:H ✅
Caption:
Alitas. 🍗

Glazed, cotija-dusted, chipotle dipping sauce on the side.
Come try the new bar bite.

📍 826 Kohl Ave, Middletown, DE 19709
Visit us | link in bio 📍

---

### BM-HOLD | B-16, B-17 — Espresso Martini alternate glass
RESOLVED: Same drink, different glass. Can schedule whenever. Low priority.

---

=============================================================
## AZTECA — @aztecadelaware + @aztecarestaurantrehoboth
## (Both accounts get identical content unless noted)
=============================================================

### AZ-POST-1 | Appetizer Sampler
Images: AZ-1 (lead), AZ-2, AZ-12
⚠️ ORIENTATION: AZ-1:H, AZ-2:V, AZ-12:H — CONFLICT
FIX: Drop AZ-2 (V). Use AZ-1 (H lead) → AZ-12 (H) only.
Caption:
Appetizer Sampler. 🔥

A little bit of everything, and all of it hits.

Find your nearest location | link in bio 📍

---

### AZ-POST-2 | Guacamole with Queso Fresco
Images: AZ-3 (lead), AZ-11, AZ-6
⚠️ ORIENTATION: AZ-3:H, AZ-11:H, AZ-6:V — CONFLICT
FIX: Drop AZ-6 (V). Use AZ-3 (H lead) → AZ-11 (H) only.
Caption:
Made to Order Guacamole. 🥑

Fresh avocado, queso fresco, and zero shortcuts.

Find your nearest location | link in bio 📍

---

### AZ-POST-3 | Octopus Guacamole
Images: AZ-8 (lead), AZ-9
⚠️ ORIENTATION FIX: Original lead AZ-5 (V) with AZ-8 (H), AZ-9 (H). FIXED: Swap lead to AZ-8 (H).
AZ-8:H, AZ-9:H ✅
Caption:
Guacamole. But make it octopus. 🐙

Not your average appetizer.

Find your nearest location | link in bio 📍

---

### AZ-POST-4 | Bacon-Wrapped Jalapeño Poppers
Images: AZ-15 (lead), AZ-16
⚠️ ORIENTATION FIX: Original had AZ-7 (V). FIXED: Drop AZ-7. Keep AZ-16 (H).
AZ-15:H, AZ-16:H ✅
Caption:
Homestyle Bacon Jalapeños. 🌶️

Stuffed, wrapped, grilled. Drizzled in Drunk Sauce.

Find your nearest location | link in bio 📍

---

### AZ-POST-5 | Full Table Spread #1
Images: AZ-20 (solo)
AZ-20:H ✅
Caption:
The whole table is eating. 🍽️

Appetizers, mains, cocktails — this is how we do it.

Find your nearest location | link in bio 📍

---

### AZ-POST-6 | Shrimp Cocktail
Images: AZ-22 (lead), AZ-25, AZ-23
AZ-22:H, AZ-25:H, AZ-23:H ✅
Caption:
Cóctel de Camarón. 🍤

Twenty shrimp. Azteca sauce. Avocado. You're welcome.

Find your nearest location | link in bio 📍

---

### AZ-POST-7 | Seafood Fajitas
Images: AZ-27 (lead), AZ-28, AZ-29
AZ-27:H, AZ-28:H, AZ-29:H ✅
Caption:
Seafood Parillada. 🐟🦐

Tilapia, scallops, shrimp, and lobster — all on one skillet.

Find your nearest location | link in bio 📍

---

### AZ-POST-8 | Grilled Fish Plate
Images: AZ-32 (lead), AZ-33
⚠️ ORIENTATION FIX: Original lead AZ-31 (V) with AZ-32 (H), AZ-33 (H). FIXED: Swap lead to AZ-32.
AZ-32:H, AZ-33:H ✅
Caption:
Tilapia a la Mexicana. 🐟

Grilled with onions and tomatoes. Served with all the fixings.

Find your nearest location | link in bio 📍

---

### AZ-POST-9 | Whole Fried Fish
Images: AZ-37 (lead), AZ-39, AZ-38
AZ-37:H, AZ-39:H, AZ-38:H ✅
Caption:
Whole Fried Tilapia. 🐠

Crispy outside. Tender inside. Bone-in and proud of it.

Find your nearest location | link in bio 📍

---

### AZ-POST-10 | Mixed Grill Platter
Images: AZ-41 (lead), AZ-43, AZ-42
⚠️ ORIENTATION: AZ-41:H, AZ-43:V, AZ-42:V — CONFLICT
FIX: Drop AZ-43 and AZ-42. Use AZ-41 (H lead) → AZ-45 (H) only. OR post AZ-41 solo.
DECISION: Post AZ-41 solo (H). Save AZ-43 hero for standalone post or Reel.
Caption:
Alambres. 🥩🔥

Steak, chicken, scallop, shrimp — all on the skewer.

Find your nearest location | link in bio 📍

---

### AZ-POST-11 | Full Table Spread #2
Images: AZ-46 (solo)
AZ-46:H ✅
Caption:
Bring the crew. 🔥

When one dish isn't enough. (It never is.)

Find your nearest location | link in bio 📍

---

### AZ-POST-12 | Two Cocktails
Images: AZ-47 (lead), AZ-48
AZ-47:H, AZ-48:H ✅
ALSO POST TO: @bluemezcalrestaurant (confirmed cross-post OK)
Caption:
Cocktail hour. 🌺

Hibiscus and spice. Two glasses, two moods.
Which one are you?

Find your nearest location | link in bio 📍

---

### AZ-POST-13 | Carne Asada
Images: AZ-49 (lead), AZ-50, AZ-51
AZ-49:H, AZ-50:H, AZ-51:H ✅
Caption:
Carne Asada. 🥩

Thin cut, marinated, grilled right. The classic for a reason.

Find your nearest location | link in bio 📍

---

### AZ-POST-14 | Enchiladas Mexicanas
Images: AZ-52 (solo)
⚠️ ORIENTATION FIX: Original had AZ-53 (V). FIXED: Drop AZ-53. Post AZ-52 solo.
AZ-52:H ✅
Caption:
Enchiladas Mexicanas. 🌶️

Red sauce. Tender chicken. Cotija on top. Comfort in a bowl.

Find your nearest location | link in bio 📍

---

### AZ-POST-15 | Mixed Fajitas
Images: AZ-57 (lead), AZ-59, AZ-58
AZ-57:H, AZ-59:H, AZ-58:H ✅
NOTE: AZ-55/AZ-56 near-duplicate resolved — dropped one, saved for future.
Caption:
Texas Fajitas. 🔥

Steak, chicken, and shrimp on a sizzling skillet. Still going.

Find your nearest location | link in bio 📍

---

### AZ-POST-16 | Birria Tacos
Images: AZ-62 (lead), AZ-63, AZ-61
AZ-62:H, AZ-63:H, AZ-61:H ✅
Caption:
Birria Tacos. 🌮

Dipped in broth. Grilled with cheese. You know the move.

Find your nearest location | link in bio 📍

---

### AZ-POST-17 | Elote
Images: AZ-64 (solo)
⚠️ ORIENTATION FIX: Original had AZ-66 (V), AZ-65 (V) as slides with AZ-64 (H) lead. FIXED: Post AZ-64 solo.
AZ-64:H ✅
Caption:
Elote. 🌽

Crema. Cotija. Tajín. On a stick.
Street food done right.

Find your nearest location | link in bio 📍

---

### AZ-POST-18 | Loaded Baked Potato
Images: AZ-68 (lead), AZ-70, AZ-69
AZ-68:H, AZ-70:H, AZ-69:H ✅
Caption:
Fajita Baked Potato. 🥔🥩

Ribeye, bacon bits, cheese dip, and scallions loaded on top.
We don't do things halfway.

Find your nearest location | link in bio 📍

---

### AZ-POST-19 | Full Table Spread #3
Images: AZ-72 (solo)
AZ-72:H ✅
ALSO POST TO: @bluemezcalrestaurant (confirmed cross-post OK)
Caption:
Family style. No apologies. 🍽️

Pull up a chair. There's room for everyone.

Find your nearest location | link in bio 📍

---

### AZ-POST-20 | Three Cocktails
Images: AZ-73 (solo)
AZ-73:H ✅ (AZ-74 dropped per Q15 — same drinks, save for future carousel)
ALSO POST TO: @bluemezcalrestaurant (confirmed cross-post OK)
Caption:
Pick your poison. 🍹

Three handcrafted cocktails. One table. No wrong choice.

Find your nearest location | link in bio 📍

---

### AZ-POST-21 | Chicken Tacos
Images: AZ-75 (lead), AZ-76
⚠️ ORIENTATION FIX: Original had AZ-77 (V). FIXED: Drop AZ-77. Keep AZ-76 (H).
AZ-75:H, AZ-76:H ✅
Caption:
Street Tacos. 🌮

Grilled chicken. Cotija. Pico. Sauce on top.
Simple done right.

Find your nearest location | link in bio 📍

---

### AZ-POST-22 | Carne Asada + Enchilada Combo
Images: AZ-80 (lead), AZ-81
⚠️ ORIENTATION FIX: Original lead AZ-79 (V) with AZ-80 (H), AZ-81 (H). FIXED: Swap lead to AZ-80.
AZ-80:H, AZ-81:H ✅
Caption:
Steak and Enchilada Combo. 🍳🥩

Carne asada, red enchilada, and a fried egg holding it all together.
This is the one.

Find your nearest location | link in bio 📍

---

### AZ-POST-23 | Baja Burrito
Images: AZ-82 (lead), AZ-83, AZ-84
AZ-82:H, AZ-83:H, AZ-84:H ✅
Caption:
Baja Burrito. 🌯

Stuffed with rice, lettuce, pico, cheese, avocado, and Baja Sauce.
Plus fries, because why not.

Find your nearest location | link in bio 📍

---

### AZ-POST-24 | Huevos Rancheros
Images: AZ-86 (lead), AZ-88, AZ-87
AZ-86:H, AZ-88:H, AZ-87:H ✅
Caption:
Huevos Rancheros. 🍳

Eggs over easy, red ranchero sauce, rice and beans.
The breakfast that means business.

Find your nearest location | link in bio 📍

---

### AZ-POST-25 | Chocolate Lava Cake
Images: AZ-89 (solo)
⚠️ ORIENTATION: AZ-89:V. Solo post, no conflict.
Caption:
Chocolate Lava Cake. 🍫

Warm. Gooey. Vanilla ice cream on top.
Finish strong.

Find your nearest location | link in bio 📍

---

### AZ-POST-26 | Churros
Images: AZ-91 (lead), AZ-92
⚠️ ORIENTATION FIX: Original had AZ-93 (H). FIXED: Drop AZ-93. Keep AZ-92 (V).
AZ-91:V, AZ-92:V ✅
Caption:
Churros. 🍩

Four sauces. No sharing required.

Find your nearest location | link in bio 📍

---

### AZ-POST-27 | Fried Ice Cream
Images: AZ-94 (lead), AZ-95, AZ-96
AZ-94:H, AZ-95:H, AZ-96:H ✅
Caption:
Fried Ice Cream. 🍦

Crispy tortilla bowl. Vanilla ice cream. Chocolate drizzle. Cherry on top.
Best way to end a meal.

Find your nearest location | link in bio 📍

---

### AZ-POST-28 | Flan
Images: AZ-97 (lead), AZ-98, AZ-100
AZ-97:H, AZ-98:H, AZ-100:H ✅
Caption:
Flan. 🍮

Caramel custard, unmolded and perfect.
The one dessert that needs no introduction.

Find your nearest location | link in bio 📍

---

### AZ-POST-29 | Fried Ice Cream with Buñuelo
Images: AZ-102 (solo)
AZ-102:V
Caption:
Fried Ice Cream. 🍦

Ice cream, chocolate, and a buñuelo on the side.
Old school. Still perfect.

Find your nearest location | link in bio 📍

---

### AZ-POST-30 | Tres Leches
Images: AZ-103 (solo)
⚠️ ORIENTATION FIX: Original had AZ-105 (H), AZ-104 (H) as slides with AZ-103 (V) lead. FIXED: Post AZ-103 solo (V).
AZ-103:V
Caption:
Tres Leches. 🍰

Soaked. Topped with cream. Finished with a dehydrated orange.
The sweetest ending.

Find your nearest location | link in bio 📍

---

### AZ-POST-31 | Full Dessert Spread
Images: AZ-101 (solo)
AZ-101:V
Caption:
Dessert menu. 🍮🍦🍫

Flan. Fried ice cream. Lava cake.
Just pick one. (Or don't.)

Find your nearest location | link in bio 📍

---

### AZ-HOLD-1 | Exterior shots AZ-35, AZ-36 — ON HOLD
Likely Rehoboth. Not priority. Do not schedule.

### AZ-HOLD-2 | AZ-55/AZ-56 near-duplicate fajita shots
One dropped, one saved for future carousel.

### AZ-HOLD-3 | AZ-74 — Three cocktails alternate
Same drinks as AZ-73, saved for future carousel.

---

=============================================================
## CROSS-POST SUMMARY
=============================================================

Posts that go on MULTIPLE accounts:

1. BM-5 / Millionaire Margarita Azteca Logo (B-30, B-31)
   → @bluemezcalrestaurant + @aztecadelaware + @aztecarestaurantrehoboth
   → Different caption per brand (see BM-5 above)

2. AZ-POST-12 / Two Cocktails (AZ-47, AZ-48)
   → @aztecadelaware + @aztecarestaurantrehoboth + @bluemezcalrestaurant
   → Same caption, swap CTA for Blue Mezcal version

3. AZ-POST-19 / Table Spread #3 (AZ-72)
   → @aztecadelaware + @aztecarestaurantrehoboth + @bluemezcalrestaurant
   → Same caption, swap CTA for Blue Mezcal version

4. AZ-POST-20 / Three Cocktails (AZ-73)
   → @aztecadelaware + @aztecarestaurantrehoboth + @bluemezcalrestaurant
   → Same caption, swap CTA for Blue Mezcal version

---

=============================================================
## POST COUNT SUMMARY
=============================================================

Jackson House (@jacksonhousede): 34 posts
Blue Mezcal (@bluemezcalrestaurant): 18 own + 3 Azteca cross-posts = 21 posts
Azteca Delaware (@aztecadelaware): 31 own + 1 BM cross-post = 32 posts
Azteca Rehoboth (@aztecarestaurantrehoboth): 31 own + 1 BM cross-post = 32 posts

At 2 posts/week (Mon + Fri), that's:
- Jackson House: ~17 weeks of content
- Blue Mezcal: ~10.5 weeks of content
- Azteca (each): ~16 weeks of content

---

=============================================================
## WHAT CODE NEEDS TO DO
=============================================================

1. Build 4 CSV files (one per Instagram account):
   - jacksonhousede.csv
   - bluemezcalrestaurant.csv
   - aztecadelaware.csv
   - aztecarestaurantrehoboth.csv

2. For each post row:
   - Assign dates starting from next available Monday or Friday after today (April 14, 2026 is a Tuesday, so first post date = Friday April 17, 2026)
   - Alternate Mon/Fri
   - Time: 11:30 AM for all
   - Build Cloudinary URLs from filenames using pattern above
   - For carousels: comma-separate URLs in Images column
   - instagram_publish_as = POST

3. For cross-posts:
   - Same post appears in multiple CSVs
   - Swap CTA line in caption to match the account
   - Schedule on SAME date across accounts (don't stagger cross-posts)

4. Blue Mezcal new menu food posts (BM-9 through BM-18):
   - Schedule on or after May 5, 2026 (menu launch date)
   - Cocktail posts (BM-1 through BM-8) can schedule immediately

5. Verify all carousel image orientations match (already pre-resolved above, but double-check)

6. Do NOT schedule any HOLD items

---

# END OF MASTER BUILD FILE
