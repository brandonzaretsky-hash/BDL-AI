import streamlit as st
import pandas as pd
from cortex import conn

def seed_cortex():
    """Injects 200 high-value data nodes into the Onion's brain."""
    data = {
        "Topic": [
            # 3D PRINTING & BAMBU LAB (40)
            "Bambu Lab A1 mini", "Bambu Studio", "OrcaSlicer", "PEI Build Plate", "Active Flow Compensation",
            "Filament Tangle Sensor", "Cold Pull Method", "3D Printing Clogs", "PLA vs PETG", "ABS Warping",
            "TPU Flexibility", "Hardened Steel Nozzle", "0.4mm Nozzle", "0.6mm Nozzle", "Layer Height",
            "Infill Density", "Gyroid Infill", "Tree Supports", "Z-Offset", "E-Steps",
            "Bed Leveling", "Brim vs Raft", "Stringing Fix", "Heat Creep", "Input Shaping",
            "Linear Advance", "Retraction Speed", "Enclosure", "Filament Dryer", "Humidity Sensor",
            "G-Code", "STL vs STEP", "CAD for 3D", "Fusion 360", "Overhangs",
            "Bridge Speed", "Cooling Fan", "Nozzle Temp", "Bed Temp", "First Layer Calibration",

            # AI & LLM TERMINOLOGY (40)
            "Large Language Model", "LLM Hallucination", "Context Window", "RAG Synthesis", "AI Tokenization",
            "Neural Network", "Transformer Architecture", "Attention Mechanism", "Deep Learning", "Machine Learning",
            "Supervised Learning", "Unsupervised Learning", "Reinforcement Learning", "Generative AI", "Zero-shot Learning",
            "Few-shot Learning", "Prompt Engineering", "Temperature Setting", "Top-P Sampling", "Fine-tuning",
            "Edge AI", "Computer Vision", "Natural Language Processing", "AI Bias", "Turing Test",
            "AGI Timeline", "AI Singularity", "Ethical AI", "Model Quantization", "GPU Acceleration",
            "TPU vs GPU", "Inference Speed", "Multimodal AI", "AI Safety", "Algorithm Transparency",
            "Neural Weights", "Backpropagation", "Gradient Descent", "Loss Function", "Training Data",

            # ANDROID & KOTLIN DEVELOPMENT (40)
            "Kotlin Null Safety", "Kotlin Coroutines", "Jetpack Compose", "Android Lifecycle", "ViewModel Pattern",
            "Dependency Injection", "Retrofit API", "Room Database", "Material 3 Design", "Android Studio",
            "Kotlin Val vs Var", "Kotlin Data Classes", "Lambda Expressions", "Higher-Order Functions", "Sealed Classes",
            "Compose State", "Composable Functions", "Modifier Pattern", "Scaffold Layout", "LazyColumn",
            "Android Permissions", "Manifest File", "Gradle Build", "Proguard & R8", "APK vs AAB",
            "Google Play Console", "Firebase Auth", "ADB Debugging", "Logcat", "Android Emulator",
            "SDK Version", "Native vs Cross-platform", "Dagger Hilt", "Koin Framework", "Compose Navigation",
            "MutableStateFlow", "SharedFlow", "Repository Pattern", "WorkManager", "Intent Filters",

            # PC HARDWARE & TECH (40)
            "DDR5 RAM", "NVMe Gen5 SSD", "RTX 5090", "Ryzen 9000", "LGA 1851",
            "Thermal Paste", "AIO Cooling", "Airflow Path", "Bottlenecking", "Overclocking",
            "BIOS Flash", "XMP Profiles", "PCIe Lanes", "Thunderbolt 5", "USB 4.0",
            "OLED vs IPS", "Refresh Rate", "DisplayPort 2.1", "PSU Efficiency", "80 Plus Gold",
            "Linux Kernel", "Windows 12", "MacOS Sequoia", "BIOS vs UEFI", "SATA SSD",
            "Mechanical Switches", "Optical Mouse", "Polling Rate", "Cat8 Ethernet", "Wi-Fi 7",
            "Bluetooth 5.4", "VR Headsets", "Steam Deck", "Raspberry Pi 5", "Single Board PC",
            "GPU VRAM", "CPU Cores", "Hyperthreading", "Clock Speed", "Case Latency",

            # SPACE, SCIENCE & WORLD (40)
            "Starship IFT-7", "Artemis III", "James Webb Telescope", "Europa Clipper", "Mars Oxygen",
            "Nuclear Fusion", "Quantum Entanglement", "Standard Model", "String Theory", "General Relativity",
            "Black Holes", "Event Horizon", "Time Dilation", "Dark Matter", "Entropy",
            "Photosynthesis", "CRISPR Editing", "mRNA Tech", "Global Warming", "Ocean Acid",
            "Renewable Grid", "Solid-State Battery", "Perovskite Solar", "Hydroponics", "Vertical Farming",
            "Voyager Message", "Hubble Constant", "Exoplanet", "SETI Search", "Dyson Sphere",
            "Toronto Tech Scene", "Canada Innovation", "E-commerce 2026", "Digital Marketing", "SEO for AI",
            "Crypto Trends", "Blockchain Logic", "Stoicism", "Growth Mindset", "Critical Thinking"
        ],
        "Meaning": [
            # 3D Printing
            "High-speed desktop 3D printer with a cantilever design.", "Official slicer for Bambu Lab printers.", "Advanced open-source slicer for high-speed custom tuning.", "Steel build plate with PEI coating for strong bed adhesion.", "Compensates for pressure to ensure smooth extrusion.",
            "Pauses the print if filament gets knotted or stuck.", "Clearing clogs by pulling filament out while semi-cool.", "Obstructions in the hotend preventing extrusion.", "PLA is for looks; PETG is for heat-resistance.", "High-strength plastic that shrinks without an enclosure.",
            "Flexible filament that requires slow, direct-drive extrusion.", "Nozzle capable of printing abrasive carbon fiber.", "Standard size for balanced speed and detail.", "Faster nozzle for large parts and abrasive filaments.", "The thickness of each individual layer of plastic.",
            "The amount of plastic inside the hollow parts of a print.", "A 3D infill pattern that is strong in all directions.", "Organic supports that are easy to remove and save material.", "The distance between the nozzle and the bed at start.", "Calibration to ensure the extruder pushes the right amount.",
            "Ensuring the build plate is flat relative to the nozzle.", "Extra layers at the base to prevent warping/lifting.", "Reducing blobs by pulling filament back during travel.", "When heat travels up the extruder and melts filament too early.", "Software technique to reduce vibrations at high speeds.",
            "Controls pressure to ensure clean corners and edges.", "How fast the filament is pulled back during travels.", "A box around the printer to keep heat in for ABS.", "A device to remove moisture from wet filament.", "Monitors the air moisture inside a filament drybox.",
            "The language used to tell the 3D printer where to move.", "STEP files are better for editing; STL is for slicing.", "Computer-Aided Design used to create 3D models.", "A professional-grade CAD software for engineers.", "Parts of a print that hang in the air without support.",
            "How fast the printer moves when crossing gaps.", "The fan that cools the plastic as it leaves the nozzle.", "Usually 200-220C for PLA and 240-260C for PETG.", "Usually 60C for PLA and 80C for PETG.", "The most important step for a successful 3D print.",

            # AI & LLM
            "AI trained on massive text to predict human language.", "When AI generates confident but incorrect information.", "The limit of how much data an AI can process at once.", "Retrieval-Augmented Generation: linking AI to data.", "Breaking text into chunks for the computer to read.",
            "Algorithms that mimic the human brain's structure.", "The math that allows AI to process sequences of text.", "Letting AI focus on the most important parts of a prompt.", "AI that uses many layers of math to learn patterns.", "Algorithms that improve automatically through experience.",
            "Training a model using data that is already labeled.", "Finding hidden patterns in data without labels.", "Learning through trial, error, and reward systems.", "AI that can create new text, images, or code.", "Doing a task without ever being specifically trained for it.",
            "Providing a few examples to help the AI understand.", "Crafting perfect inputs to get the best AI outputs.", "Controls how random or literal the AI's response is.", "Limiting AI choices to the most likely next words.", "Training an existing model on a specific new dataset.",
            "Running AI locally on a device rather than the cloud.", "AI's ability to see and understand images/video.", "The branch of AI focused on human languages.", "Prejudices in data that lead to unfair AI results.", "A test to see if a machine can act like a human.",
            "The future point when AI reaches human intelligence.", "When AI growth becomes uncontrollable and recursive.", "Building AI that is safe, fair, and helpful to humans.", "Making models smaller so they run on phones/PCs.", "Using powerful graphics chips to speed up AI math.",
            "TPUs are Google's custom chips specifically for AI.", "The time it takes for an AI to generate a response.", "AI that can process text, images, and audio at once.", "Systems built to prevent AI from causing harm.", "Making AI decision-making clear and understandable.",
            "The values in a neural network that store knowledge.", "The math used to teach a neural network from errors.", "The process of minimizing errors during AI training.", "The mathematical gap between AI's answer and the truth.", "The massive amount of info used to build an AI.",

            # Android & Kotlin
            "A feature that prevents apps from crashing due to nulls.", "A way to run tasks in the background without freezing.", "Android's modern way to build UI using only code.", "The stages an app goes through from open to close.", "A class that holds data even if the screen rotates.",
            "Providing objects to a class instead of creating them.", "The library used to connect an app to the internet.", "A local database for saving data on the phone.", "Google's latest design system for beautiful apps.", "The official software used to build Android apps.",
            "Val is for values that never change; Var can change.", "Simple classes used only for storing information.", "Short blocks of code that can be passed around.", "Functions that take other functions as parameters.", "Classes that have a strictly limited number of types.",
            "The data that tells the UI what to display right now.", "Functions marked @Composable that draw the UI.", "A tool used to change the look/feel of UI elements.", "A layout that provides slots for bars and buttons.", "The modern way to show a long, fast list of items.",
            "The system that asks users for camera or GPS access.", "The file that lists the app's name and settings.", "The engine that compiles your code into an app.", "Tools that make your app smaller and harder to hack.", "APK is for testing; AAB is for the Play Store.",
            "The website used to publish apps to the world.", "A secure way to let users log in with Google/Email.", "A tool to talk to your phone from your
