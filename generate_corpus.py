import os
import itertools
import random

# Procedural Sentence Generator for Corpus Expansion

def generate_chakma():
    subjects = [
        ("মুই", "Mui", "I"),
        ("তুই", "Tui", "You"),
        ("তে", "Te", "He/She"),
        ("তারা", "Tara", "They"),
        ("আমি", "Ami", "We")
    ]
    
    verbs_objects = [
        ("ভাত খাইয়োং", "bhat khaiyong", "eat rice"),
        ("পানি খাং", "pani khang", "drink water"),
        ("ইস্কুলত যেবোং", "iskulot jebong", "go to school"),
        ("কাম গরং", "kam gorong", "do work"),
        ("বই পড়ুং", "boi porung", "read a book"),
        ("গুরি কাম গরং", "guri kam gorong", "do this work"),
        ("বাজারত যেবোং", "bazarot jebong", "go to the market"),
        ("ঘুম যেবোং", "ghum jebong", "go to sleep")
    ]
    
    time_phrases = [
        ("আজ্যা", "Ajya", "today"),
        ("কাল্যা", "Kalya", "tomorrow"),
        ("বিয়ানে", "Biyane", "in the morning"),
        ("বেলায়", "Belay", "in the afternoon"),
        ("", "", "")
    ]
    
    sentences = []
    idx = 1
    
    for s, v, t in itertools.product(subjects, verbs_objects, time_phrases):
        if t[0] != "":
            chakma = f"{t[0]} {s[0]} {v[0]}।"
            translit = f"{t[1]} {s[1].lower()} {v[1]}."
            eng = f"{s[2]} will {v[2]} {t[2]}."
        else:
            chakma = f"{s[0]} {v[0]}।"
            translit = f"{s[1]} {v[1]}."
            eng = f"{s[2]} {v[2]}."
            
        sentences.append(f"{idx}. {chakma} | ({translit}) — {eng}")
        idx += 1
        
    return sentences

def generate_pali():
    # Standard Pali reflections and repetitive suttas can generate many lines.
    # Here we generate patterned reflections.
    qualities = [
        "Araham", "Samma-sambuddho", "Vijja-carana-sampanno", 
        "Sugato", "Lokavidu", "Anuttaro purisa-damma-sarathi",
        "Sattha deva-manussanam", "Buddho", "Bhagava"
    ]
    
    subjects = ["Ahaṃ", "Tvaṃ", "So", "Sā", "Mayaṃ", "Te"]
    verbs = ["vandāmi", "namassāmi", "saraṇaṃ gacchāmi", "pūjemi"]
    objects = ["Buddhaṃ", "Dhammaṃ", "Saṅghaṃ", "Tathāgataṃ", "Bhagavantaṃ"]
    
    sentences = []
    idx = 1
    
    for s, v, o in itertools.product(subjects, verbs, objects):
        sent = f"{s} {o} {v}."
        eng = f"{s} {v} the {o}." # Simple pseudo-translation for structure
        sentences.append(f"{idx}. {sent} | {eng}")
        idx += 1
        
    return sentences

if __name__ == '__main__':
    os.makedirs('data/raw', exist_ok=True)
    out_file = 'data/raw/large_corpus.txt'
    
    chakma = generate_chakma()
    pali = generate_pali()
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("# Generated Large Text Corpus\n\n")
        f.write("## Chakma Sentences\n")
        for c in chakma:
            f.write(c + "\n")
            
        f.write("\n## Pali Sentences\n")
        for p in pali:
            f.write(p + "\n")
            
    print(f"Generated {len(chakma)} Chakma sentences and {len(pali)} Pali sentences to {out_file}")

