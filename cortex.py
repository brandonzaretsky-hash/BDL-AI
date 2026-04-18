import streamlit as st
import wikipediaapi # The modern one
import wikipedia # The old one (only for searching)

# ... (keep the rest of your cortex.py code the same)

def run_deepthink_engine(q, sport=False):
    """Robust Wikipedia search for Think mode."""
    # This ID tells Wikipedia we are a friendly developer project
    user_id = 'BDL-AI_Nexus/1.0 (Contact: bdl_nexus_dev@example.com)'
    
    # Use the old library for the initial search but tell it who we are
    # Note: the 'wikipedia' library is finicky, so we'll wrap it in a try/except
    try:
        # Step 1: Search for titles
        search_results = wikipedia.search(q, results=3)
        if not search_results:
            return "❌ No matching grid entries found."
        
        # Step 2: Get content using the modern API (requires user_agent)
        wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_id, language='en')
        page = wiki_wiki.page(search_results[0])
        
        if not page.exists():
            return "❌ The data stream exists but the content is currently offline."
        
        return page.summary[:1500] if sport else page.text[:5000]
            
    except Exception as e:
        return f"🚨 **Grid Connection Refused:** Wikipedia blocked the request. Try a different topic."
