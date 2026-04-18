import streamlit as st
import pandas as pd
from cortex import conn

def seed_cortex():
    # The "Top 50" Starter Nodes
    data = {
        "Topic": [
            "Bambu Lab A1 mini", "3D Printing Clogs", "PLA vs PETG", "Stringing Fix", 
            "Mars Colony", "James Webb Telescope", "Quantum Computing", "Black Holes",
            "Android Development", "Jetpack Compose", "Kotlin", "RAM vs SSD", 
            "Great Wall of China", "Ocean Depth", "SpaceX Starship", "Artificial Intelligence",
            "Voyager 1", "Nuclear Fusion", "Photosynthesis", "The Internet",
            "Mount Everest", "Amazon Rainforest", "Pyramids of Giza", "DNA",
            "Bitcoin", "Cybersecurity", "Electric Vehicles", "Mars Rover",
            "3D Print Warping", "Nozzle Temp", "First 3D Printer", "Slicer Software",
            "Superconductivity", "Turing Test", "Moore's Law", "Dark Matter",
            "Exoplanets", "The Moon", "International Space Station", "Renewable Energy",
            "Smartphones", "Bluetooth", "Wifi 6", "Augmented Reality",
            "Growth Mindset", "Stoicism", "Deep Sea Creatures", "Bioluminescence",
            "Antarctica", "Sahara Desert"
        ],
        "Meaning": [
            "A high-speed cantilever 3D printer known for its 'plug-and-play' setup and active flow rate compensation.",
            "Usually caused by heat creep or debris; cleared by a cold pull or heating the nozzle to 250°C.",
            "PLA is easy to print and stiff; PETG is more durable and heat-resistant but prone to stringing.",
            "Reduced by increasing retraction speed or lowering the printing temperature by 5-10°C.",
            "The goal of establishing a self-sustaining human presence on Mars, primarily led by SpaceX's Starship project.",
            "An infrared space observatory that views the universe's first stars and the formation of galaxies.",
            "Computing that uses qubits to perform calculations at speeds impossible for classical computers.",
            "A region of spacetime where gravity is so strong that nothing, not even light, can escape.",
            "The process of creating apps for the Android OS, primarily using Kotlin and Android Studio.",
            "Android’s modern toolkit for building native UI, replacing XML with a declarative Kotlin API.",
            "A modern, cross-platform language that is the preferred choice for Android development.",
            "RAM is short-term memory for active tasks; SSD is long-term storage for files and apps.",
            "A series of fortifications built across northern China to protect against nomadic invasions.",
            "The Challenger Deep in the Mariana Trench is the deepest point at roughly 10,935 meters.",
            "A fully reusable heavy-lift launch vehicle designed to carry humans to the Moon and Mars.",
            "Systems capable of performing tasks that usually require human intelligence, like synthesis.",
            "The furthest man-made object from Earth, currently traveling through interstellar space.",
            "The process of combining atomic nuclei to create energy, mimicking the power of the sun.",
            "The process used by plants to convert light energy into chemical energy (glucose).",
            "A global network of interconnected computers communicating via standardized protocols.",
            "The highest point above sea level on Earth, standing at 8,848 meters.",
            "The world's largest tropical rainforest, producing roughly 20% of the Earth's oxygen.",
            "Ancient masonry structures in Egypt; the Great Pyramid was the tallest man-made structure for 3,800 years.",
            "Deoxyribonucleic acid, the molecule that carries genetic instructions for all living organisms.",
            "The first decentralized cryptocurrency, created in 2009 by the anonymous Satoshi Nakamoto.",
            "The practice of protecting systems and networks from digital attacks and data theft.",
            "Vehicles powered by one or more electric motors, using energy stored in rechargeable batteries.",
            "Perseverance and Curiosity are currently searching for signs of ancient life on the Martian surface.",
            "Commonly caused by a cold print bed or poor bed adhesion; solved by using a brim or glue.",
            "The temperature required to melt filament; usually 200-220°C for PLA and 230-250°C for PETG.",
            "Invented by Chuck Hull in 1984, using a process called stereolithography (SLA).",
            "Programs like Bambu Studio or OrcaSlicer that convert 3D models into G-code for the printer.",
            "A state of zero electrical resistance occurring in certain materials when cooled below a critical temp.",
            "A test of a machine's ability to exhibit intelligent behavior equivalent to that of a human.",
            "The observation that the number of transistors on a microchip doubles every two years.",
            "An invisible form of matter that makes up about 85% of the matter in the universe.",
            "Planets located outside of our solar system, often orbiting other stars.",
            "Earth's only natural satellite, formed roughly 4.5 billion years ago after a massive collision.",
            "A modular space station in low Earth orbit, a collaborative project between five space agencies.",
            "Energy from sources that are naturally replenished, such as sunlight, wind, and water.",
            "Handheld computers that integrate mobile phone functions with advanced computing capabilities.",
            "A short-range wireless technology standard used for exchanging data over short distances.",
            "The latest generation of Wi-Fi, offering faster speeds and better performance in crowded areas.",
            "An interactive experience where computer-generated content is overlaid on the real world.",
            "The belief that abilities can be developed through dedication and hard work.",
            "An ancient philosophy focused on self-control and fortitude as a means to overcome emotions.",
            "Organisms like the Anglerfish that have adapted to live in extreme pressure and darkness.",
            "The production and emission of light by a living organism, common in deep-sea creatures.",
            "The southernmost continent, containing the geographic South Pole and covered by ice.",
            "The largest hot desert in the world, covering much of North Africa."
        ]
    }
    
    df = pd.DataFrame(data)
    
    try:
        # Get existing data
        current_ctx = conn.read(worksheet="Context", ttl="1s")
        # Combine and remove duplicates
        updated_ctx = pd.concat([current_ctx, df]).drop_duplicates(subset=['Topic'], keep='last')
        conn.update(worksheet="Context", data=updated_ctx)
        st.success(f"Cortex Infused! {len(df)} new tracks added.")
    except Exception as e:
        st.error(f"Infusion Failed: {e}")

st.title("🧪 Cortex Seeder")
if st.button("START NEURAL INFUSION"):
    seed_cortex()
