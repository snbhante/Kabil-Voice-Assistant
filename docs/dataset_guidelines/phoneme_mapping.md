# Chakma Phoneme Mapping (Grapheme-to-Phoneme)

To train our Text-to-Speech (TTS) models, the system needs to know how each character sounds. Since Chakma is frequently written using the Bengali script alongside the native Chakma script, we will map both to the **International Phonetic Alphabet (IPA)**.

*Note: This is a working document. As we discover phonetic nuances in spoken Chakma, we will refine these IPA mappings.*

## Vowels
| Bengali Script | Chakma Script | IPA Symbol | Example (Chakma) | English Approximation |
| :---: | :---: | :---: | :--- | :--- |
| অ | 𑄃 | /ɔ/ or /a/ | | 'o' in 'hot' or 'u' in 'hut' |
| আ | 𑄃𑄧 | /a/ | | 'a' in 'father' |
| ই / ি | 𑄄 | /i/ | | 'ee' in 'see' |
| উ / ু | 𑄅 | /u/ | | 'oo' in 'boot' |
| এ / ে | 𑄆 | /e/ or /ɛ/| | 'e' in 'bed' |
| ও / ো | 𑄃𑄮 | /o/ | | 'o' in 'go' |

## Consonants: Velar (Throat)
| Bengali Script | Chakma Script | IPA Symbol | Example (Chakma) | English Approximation |
| :---: | :---: | :---: | :--- | :--- |
| ক | 𑄇 | /k/ | | 'k' in 'kite' (unaspirated) |
| খ | 𑄈 | /kʰ/ | | 'k' with a puff of air |
| গ | 𑄉 | /g/ | | 'g' in 'go' |
| ঘ | 𑄊 | /gʱ/ | | 'g' + breathy sound |
| ঙ | 𑄋 | /ŋ/ | | 'ng' in 'sing' |

## Consonants: Dental vs. Retroflex
*This distinction is critical in Indo-Aryan languages. Dental sounds involve the tongue touching the back of the teeth, while retroflex sounds involve curling the tongue back.*

| Bengali Script | Chakma Script | IPA Symbol | Type | English Approximation |
| :---: | :---: | :---: | :--- | :--- |
| ত | 𑄖 | /t̪/ | Dental | Soft 't', tongue on teeth (e.g., Spanish 'taco') |
| থ | 𑄗 | /t̪ʰ/ | Dental | Aspirated soft 't' |
| ট | 𑄑 | /ʈ/ | Retroflex | Hard 't', tongue curled back (closer to English 'top')|
| ঠ | 𑄒 | /ʈʰ/ | Retroflex | Aspirated hard 't' |
| দ | 𑄘 | /d̪/ | Dental | Soft 'd', tongue on teeth |
| ড | 𑄓 | /ɖ/ | Retroflex | Hard 'd' |

## Special Chakma Nuances (To be defined)
*Use this space to document unique sounds in Chakma that might not perfectly align with standard Bengali pronunciation.*
1. **The "Tw" or "Mw" sounds:** (e.g., ত নাঙান কি? - Tw nangan ki?). How does this modifier sound phonetically?
2. **Nasalization:** Does Chakma use heavy nasalization (like the Bengali ঁ)? 
3. **Tone/Stress:** Are there specific syllables that carry a unique pitch or stress?
