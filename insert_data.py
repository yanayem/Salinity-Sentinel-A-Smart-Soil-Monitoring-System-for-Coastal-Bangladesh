import os
import django
import random

# ---------------- Django setup ----------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soilcore.settings")
django.setup()

from soilcore.models import SoilType  

# ---------------- Helper Data ----------------
soil_names = ["Sandy Soil", "Clay Soil", "Loamy Soil", "Peaty Soil", "Chalky Soil", "Silty Soil",
              "Alluvial Soil", "Red Soil", "Black Soil", "Laterite Soil", "Mountain Soil",
              "Volcanic Soil", "Saline Soil", "Desert Soil", "Floodplain Soil", "Podzol Soil",
              "Regosol", "Ferrallitic Soil", "Brown Earth", "Forest Soil", "Wetland Soil",
              "Urban Soil", "Tropical Soil", "Subtropical Soil", "Temperate Soil", "Alpine Soil",
              "Marsh Soil", "Clay Loam", "Silty Clay", "Peaty Loam", "Loamy Sand", "Sand Loam",
              "Organic Soil", "Calcareous Soil", "Acid Soil", "Basic Soil", "Iron-rich Soil",
              "Manganese-rich Soil", "Gravelly Soil", "Stony Soil", "Waterlogged Soil",
              "Aerated Soil", "Compact Soil", "Nutritious Soil", "Poor Soil", "Humus-rich Soil",
              "Mineral Soil", "Rocky Soil", "Loess Soil", "Mixed Soil", "Artificial Soil"]

descriptions = ["Light and drains water quickly, ideal for root crops.",
                "Heavy soil, retains moisture, challenging to plow.",
                "Fertile and well-balanced for most crops.",
                "Acidic soil, rich in organic matter, supports forest growth.",
                "Alkaline soil, low in nutrients, needs fertilization.",
                "Smooth and fine-textured soil, excellent for vegetables.",
                "Rich in minerals and nutrients, ideal for agriculture.",
                "Red soil, low fertility, suitable for drought-resistant crops.",
                "Dark soil with high moisture retention, good for rice and sugarcane.",
                "High iron content, slightly acidic.",
                "Loamy soil, balanced texture for horticulture.",
                "Silty soil, retains water but drains slowly.",
                "Peaty soil, high organic matter, acidic.",
                "Saline soil, requires treatment before planting.",
                "Volcanic soil, very fertile, supports tropical crops.",
                "Mountain soil, shallow and rocky, good for pasture.",
                "Floodplain soil, fertile but seasonally flooded.",
                "Podzol soil, acidic, supports conifer forests.",
                "Urban soil, mixed with construction debris, disturbed.",
                "Wetland soil, waterlogged, suitable for aquatic plants."]

crops = ["Rice","Wheat","Maize","Barley","Oats","Potato","Carrot","Tomato","Onion",
         "Pepper","Cabbage","Spinach","Lettuce","Sugarcane","Cotton","Soybean","Peanut",
         "Millet","Coffee","Cocoa","Tea","Banana","Pineapple","Apple","Orange","Mango",
         "Papaya","Guava","Avocado","Cherry","Plum","Peach","Olive","Date Palm","Coconut",
         "Rubber Tree","Eucalyptus","Teak","Mahogany","Bamboo","Maple","Oak","Pine","Fir",
         "Spruce","Chestnut","Walnut","Almond","Cashew","Lychee","Jackfruit","Durian"]

locations = ["Rural areas", "Riverbanks", "Hilly regions", "Coastal areas", "Plains", "Valleys",
             "Desert edges", "Forest clearings", "Urban farms", "Wetlands", "Floodplains",
             "Mountain slopes", "Plateaus", "Volcanic regions", "River deltas", "Mangrove areas",
             "Grasslands", "Agricultural belts", "Tea estates", "Plantation areas", "Orchards",
             "Botanical gardens", "Community farms", "Reclaimed land", "National parks"]

# ---------------- Insert 1000 rows ----------------
for _ in range(1000):
    SoilType.objects.create(
        name=random.choice(soil_names),
        description=random.choice(descriptions),
        suitable_crops=", ".join(random.sample(crops, 3)),
        location=random.choice(locations),
        ph_min=round(random.uniform(4.5, 6.5), 1),
        ph_max=round(random.uniform(6.6, 8.5), 1)
    )

print("SoilType records inserted successfully!")
