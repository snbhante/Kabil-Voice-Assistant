import os
import itertools
import random

subjects = [
    {"en": "I", "bn": "আমি", "bn_t": "Ami", "ck_b": "মুই", "ck_t": "Mui", "ck_s": "𑄟𑄪𑄃𑄨", "pa_r": "Ahaṃ", "pa_b": "অহং", "pa_c": "𑄃𑄦𑄁"},
    {"en": "You", "bn": "তুমি", "bn_t": "Tumi", "ck_b": "তুই", "ck_t": "Tui", "ck_s": "𑄖𑄪𑄃𑄨", "pa_r": "Tvaṃ", "pa_b": "ত্বং", "pa_c": "𑄖𑄴𑄤𑄁"},
    {"en": "He", "bn": "সে", "bn_t": "Se", "ck_b": "তে", "ck_t": "Te", "ck_s": "𑄖𑄬", "pa_r": "So", "pa_b": "সো", "pa_c": "𑄥𑄮"},
    {"en": "They", "bn": "তারা", "bn_t": "Tara", "ck_b": "তারা", "ck_t": "Tara", "ck_s": "𑄖𑄢", "pa_r": "Te", "pa_b": "তে", "pa_c": "𑄖𑄬"},
    {"en": "We", "bn": "আমরা", "bn_t": "Amra", "ck_b": "আমি", "ck_t": "Ami", "ck_s": "𑄃𑄟𑄨", "pa_r": "Mayaṃ", "pa_b": "ময়ং", "pa_c": "𑄟𑄠𑄁"}
]

verbs = [
    {"en": "eat rice", "bn": "ভাত খাই", "bn_t": "bhat khai", "ck_b": "ভাত খাং", "ck_t": "bhat khang", "ck_s": "𑄞𑄧𑄖𑄴 𑄈𑄋𑄴", "pa_r": "odanaṃ bhuñjāmi", "pa_b": "ওদনং ভুঞ্জামি", "pa_c": "𑄃𑄮𑄘𑄚𑄁 𑄞𑄪𑄐𑄴𑄎𑄧𑄟𑄨"},
    {"en": "drink water", "bn": "পানি পান করি", "bn_t": "pani pan kori", "ck_b": "পানি খাং", "ck_t": "pani khang", "ck_s": "𑄛𑄚𑄨 𑄈𑄋𑄴", "pa_r": "jalaṃ pivāmi", "pa_b": "জলং পিবামি", "pa_c": "𑄎𑄣𑄁 𑄛𑄨𑄝𑄧𑄟𑄨"},
    {"en": "go to school", "bn": "স্কুলে যাই", "bn_t": "skoole jai", "ck_b": "ইস্কুলত যেবোং", "ck_t": "iskulot jebong", "ck_s": "𑄃𑄨𑄌𑄴𑄇𑄪𑄣𑄧𑄖𑄴 𑄠𑄬𑄝𑄮𑄁", "pa_r": "pāṭhasālaṃ gacchāmi", "pa_b": "পাঠসালং গচ্ছামি", "pa_c": "𑄛𑄧𑄒𑄥𑄧𑄣𑄁 𑄉𑄌𑄴𑄍𑄧𑄟𑄨"},
    {"en": "do work", "bn": "কাজ করি", "bn_t": "kaj kori", "ck_b": "কাম গরং", "ck_t": "kam gorong", "ck_s": "𑄇𑄟𑄴 𑄉𑄧𑄢𑄧𑄁", "pa_r": "kammaṃ karomi", "pa_b": "কম্মং করোমি", "pa_c": "𑄇𑄟𑄴𑄟𑄁 𑄇𑄢𑄮𑄟𑄨"},
    {"en": "read a book", "bn": "বই পড়ি", "bn_t": "boi pori", "ck_b": "বই পড়ুং", "ck_t": "boi porung", "ck_s": "𑄝𑄃𑄨 𑄛𑄧𑄢𑄪𑄁", "pa_r": "potthakaṃ paṭhāmi", "pa_b": "পোত্থকং পঠামি", "pa_c": "𑄛𑄮𑄖𑄴𑄗𑄇𑄁 𑄛𑄒𑄧𑄟𑄨"},
    {"en": "see the moon", "bn": "চাঁদ দেখি", "bn_t": "chad dekhi", "ck_b": "চান দেঘং", "ck_t": "chan deghong", "ck_s": "𑄌𑄚𑄴 𑄘𑄬𑄊𑄧𑄁", "pa_r": "candaṃ passāmi", "pa_b": "চন্দং পস্সামি", "pa_c": "𑄌𑄚𑄴𑄘𑄁 𑄛𑄥𑄴𑄥𑄧𑄟𑄨"}
]

times = [
    {"en": "", "bn": "", "bn_t": "", "ck_b": "", "ck_t": "", "ck_s": "", "pa_r": "", "pa_b": "", "pa_c": ""},
    {"en": "Today ", "bn": "আজ ", "bn_t": "aj ", "ck_b": "আজ্যা ", "ck_t": "ajya ", "ck_s": "𑄃𑄎𑄴𑄠𑄧 ", "pa_r": "Ajja ", "pa_b": "অজ্জ ", "pa_c": "𑄃𑄎𑄴𑄎 "},
    {"en": "Tomorrow ", "bn": "আগামীকাল ", "bn_t": "agamikal ", "ck_b": "কাল্যা ", "ck_t": "kalya ", "ck_s": "𑄇𑄣𑄴𑄠𑄧 ", "pa_r": "Suve ", "pa_b": "সুবে ", "pa_c": "𑄥𑄪𑄝𑄬 "},
    {"en": "In the morning ", "bn": "সকালে ", "bn_t": "sokale ", "ck_b": "বিয়ানে ", "ck_t": "biyane ", "ck_s": "𑄝𑄨𑄠𑄚𑄬 ", "pa_r": "Pāto ", "pa_b": "পাতো ", "pa_c": "𑄛𑄧𑄖𑄮 "},
    {"en": "At night ", "bn": "রাতে ", "bn_t": "rate ", "ck_b": "রেইত্তে ", "ck_t": "reitte ", "ck_s": "𑄢𑄬𑄃𑄨𑄖𑄴𑄖𑄬 ", "pa_r": "Rattiyaṃ ", "pa_b": "রত্তিয়ং ", "pa_c": "𑄢𑄖𑄴𑄖𑄨𑄠𑄁 "}
]

adjectives = [
    {"en": "", "bn": "", "bn_t": "", "ck_b": "", "ck_t": "", "ck_s": "", "pa_r": "", "pa_b": "", "pa_c": ""},
    {"en": "happily ", "bn": "আনন্দে ", "bn_t": "anonde ", "ck_b": "গমেগমে ", "ck_t": "gome-gome ", "ck_s": "𑄉𑄧𑄟𑄬𑄉𑄧𑄟𑄬 ", "pa_r": "sukhena ", "pa_b": "সুখেন ", "pa_c": "𑄥𑄪𑄈𑄬𑄚 "},
    {"en": "quickly ", "bn": "দ্রুত ", "bn_t": "druto ", "ck_b": "তারাতারি ", "ck_t": "taratari ", "ck_s": "𑄖𑄢𑄖𑄢𑄨 ", "pa_r": "sīghaṃ ", "pa_b": "সীঘং ", "pa_c": "𑄥𑄩𑄊𑄁 "}
]


os.makedirs('data/raw', exist_ok=True)

chakma_file = open('data/raw/chakma.txt', 'w', encoding='utf-8')
pali_file = open('data/raw/pali.txt', 'w', encoding='utf-8')
bangla_file = open('data/raw/bangla.txt', 'w', encoding='utf-8')
english_file = open('data/raw/english.txt', 'w', encoding='utf-8')

# Duplicate the iteration to generate a large amount of sentences (e.g. 5 * 6 * 5 * 3 * 10 = 4500 sentences)
idx = 1
for _ in range(3):
    for s, v, t, a in itertools.product(subjects, verbs, times, adjectives):
        en_str = f"{t['en']}{s['en']} {a['en']}{v['en']}."
        bn_str = f"{t['bn']}{s['bn']} {a['bn']}{v['bn']}।"
        bn_t_str = f"{t['bn_t']}{s['bn_t']} {a['bn_t']}{v['bn_t']}."
        
        ck_b_str = f"{t['ck_b']}{s['ck_b']} {a['ck_b']}{v['ck_b']}।"
        ck_t_str = f"{t['ck_t']}{s['ck_t']} {a['ck_t']}{v['ck_t']}."
        ck_s_str = f"{t['ck_s']}{s['ck_s']} {a['ck_s']}{v['ck_s']}।"
        
        pa_r_str = f"{t['pa_r']}{s['pa_r']} {a['pa_r']}{v['pa_r']}."
        pa_b_str = f"{t['pa_b']}{s['pa_b']} {a['pa_b']}{v['pa_b']}."
        pa_c_str = f"{t['pa_c']}{s['pa_c']} {a['pa_c']}{v['pa_c']}."

        # Chakma: ChakmaScript | (BanglaScript | ChakmaTranslit) — English
        chakma_line = f"{ck_s_str} | ({ck_b_str} | {ck_t_str}) — {en_str}\n"
        chakma_file.write(chakma_line)
        
        # Pali: PaliRoman | (PaliBanglaScript | PaliChakmaScript) — English
        pali_line = f"{pa_r_str} | ({pa_b_str} | {pa_c_str}) — {en_str}\n"
        pali_file.write(pali_line)
        
        # Bangla: BanglaScript | (BanglaTranslit) — English
        bangla_line = f"{bn_str} | ({bn_t_str}) — {en_str}\n"
        bangla_file.write(bangla_line)
        
        # English: English | (BanglaScript | ChakmaScript | PaliRoman)
        english_line = f"{en_str} | ({bn_str} | {ck_s_str} | {pa_r_str})\n"
        english_file.write(english_line)
        
        idx += 1

chakma_file.close()
pali_file.close()
bangla_file.close()
english_file.close()

print(f"Successfully generated {idx-1} sentences for each parallel corpus.")

