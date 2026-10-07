# Chakma Phoneme Mapping (Grapheme-to-Phoneme / G2P)

The Chakma script is an abugida where consonants have an inherent vowel `ā` (/a:/), unlike Bengali where the inherent vowel is `o` or `ɔ`. This document provides a complete Grapheme-to-Phoneme mapping for building text-to-speech (TTS) and acoustic models.

## 1. Independent Vowels (Svara)
These vowels occur at the beginning of words or independently.

| Grapheme | Unicode Name | IPA Phoneme | Description / English Approx |
| :---: | :--- | :---: | :--- |
| 𑄃 | CHAKMA LETTER A | /a/ or /a:/ | Like 'a' in 'f**a**ther' |
| 𑄄 | CHAKMA LETTER I | /i/ | Like 'ee' in 's**ee**' |
| 𑄅 | CHAKMA LETTER U | /u/ | Like 'oo' in 'f**oo**d' |
| 𑄆 | CHAKMA LETTER E | /e/ | Like 'e' in 'b**e**d' or 'ay' in 's**ay**' |

*Note: In Chakma orthography, most other independent vowels are formed by applying dependent vowel signs to the independent letter 𑄃 (A).*

## 2. Dependent Vowel Signs (Matras)
These modifiers are attached to consonants to override the inherent `ā`.
*(Using 𑄇 /ka:/ as the base consonant for demonstration)*

| Grapheme | Base + Matra | Unicode Name | IPA Phoneme | Output Pronunciation |
| :---: | :---: | :--- | :---: | :--- |
| (None) | 𑄇 | INHERENT A | /a:/ | /ka:/ |
| 𑄧 | 𑄇𑄧 | CHAKMA VOWEL SIGN AA | /ɔ/ or /o/ | /kɔ/ (short 'o') |
| 𑄨 | 𑄇𑄨 | CHAKMA VOWEL SIGN I | /i/ | /ki/ |
| 𑄩 | 𑄇𑄩 | CHAKMA VOWEL SIGN II | /i:/ | /ki:/ (long 'i') |
| 𑄪 | 𑄇𑄪 | CHAKMA VOWEL SIGN U | /u/ | /ku/ |
| 𑄫 | 𑄇𑄫 | CHAKMA VOWEL SIGN UU | /u:/ | /ku:/ (long 'u') |
| 𑄬 | 𑄇𑄬 | CHAKMA VOWEL SIGN E | /e/ | /ke/ |
| 𑄭 | 𑄇𑄭 | CHAKMA VOWEL SIGN AI | /ai/ | /kai/ (diphthong) |
| 𑄮 | 𑄇𑄮 | CHAKMA VOWEL SIGN O | /o/ | /ko/ |
| 𑄯 | 𑄇𑄯 | CHAKMA VOWEL SIGN AU | /au/ | /kau/ (diphthong) |

## 3. Consonants (Vyanjana)
Remember: Unlike standard Indic scripts, the base consonant carries an **inherent long `ā` (/a:/)**, not a short `a/o`.

### Velar
| Grapheme | Unicode Name | IPA Phoneme (with inherent ā) |
| :---: | :--- | :---: |
| 𑄇 | CHAKMA LETTER KAA | /ka:/ |
| 𑄈 | CHAKMA LETTER KHAA | /kʰa:/ |
| 𑄉 | CHAKMA LETTER GAA | /ga:/ |
| 𑄊 | CHAKMA LETTER GHAA | /gʰa:/ |
| 𑄋 | CHAKMA LETTER NGAA | /ŋa:/ |

### Palatal
| Grapheme | Unicode Name | IPA Phoneme (with inherent ā) |
| :---: | :--- | :---: |
| 𑄌 | CHAKMA LETTER CA | /ca:/ or /tʃa:/ |
| 𑄍 | CHAKMA LETTER CHA | /cʰa:/ or /tʃʰa:/ |
| 𑄎 | CHAKMA LETTER JAA | /ɟa:/ or /dʒa:/ |
| 𑄏 | CHAKMA LETTER JHAA | /ɟʰa:/ or /dʒʰa:/ |
| 𑄐 | CHAKMA LETTER NYAA | /ɲa:/ |

### Retroflex (Alveolar shift in modern speech)
| Grapheme | Unicode Name | IPA Phoneme (with inherent ā) |
| :---: | :--- | :---: |
| 𑄑 | CHAKMA LETTER TTAA | /ʈa:/ or /ta:/ |
| 𑄒 | CHAKMA LETTER TTHAA | /ʈʰa:/ or /tʰa:/ |
| 𑄓 | CHAKMA LETTER DDAA | /ɖa:/ or /da:/ |
| 𑄔 | CHAKMA LETTER DDHAA | /ɖʰa:/ or /dʰa:/ |
| 𑄕 | CHAKMA LETTER NNAA | /ɳa:/ or /na:/ |

### Dental
| Grapheme | Unicode Name | IPA Phoneme (with inherent ā) |
| :---: | :--- | :---: |
| 𑄖 | CHAKMA LETTER TAA | /t̪a:/ |
| 𑄗 | CHAKMA LETTER THAA | /t̪ʰa:/ |
| 𑄘 | CHAKMA LETTER DAA | /d̪a:/ |
| 𑄙 | CHAKMA LETTER DHAA | /d̪ʰa:/ |
| 𑄚 | CHAKMA LETTER NAA | /n̪a:/ |

### Labial
| Grapheme | Unicode Name | IPA Phoneme (with inherent ā) |
| :---: | :--- | :---: |
| 𑄛 | CHAKMA LETTER PAA | /pa:/ |
| 𑄜 | CHAKMA LETTER PHAA | /pʰa:/ or /fa:/ |
| 𑄝 | CHAKMA LETTER BAA | /ba:/ |
| 𑄞 | CHAKMA LETTER BHAA | /bʰa:/ or /va:/ |
| 𑄟 | CHAKMA LETTER MAA | /ma:/ |

### Approximants, Sibilants, and Fricatives
| Grapheme | Unicode Name | IPA Phoneme (with inherent ā) |
| :---: | :--- | :---: |
| 𑄠 | CHAKMA LETTER YYAA | /ja:/ |
| 𑄡 | CHAKMA LETTER YAA | /dʒa:/ or /ja:/ |
| 𑄢 | CHAKMA LETTER RAA | /ra:/ (alveolar trill/tap) |
| 𑄣 | CHAKMA LETTER LAA | /la:/ |
| 𑄤 | CHAKMA LETTER WAA | /wa:/ |
| 𑄥 | CHAKMA LETTER SAA | /sa:/ |
| 𑄦 | CHAKMA LETTER HAA | /ha:/ |

## 4. Modifiers and Diacritics
These marks alter the pronunciation of the syllable.

| Grapheme | Unicode Name | IPA Effect | Description |
| :---: | :--- | :--- | :--- |
| 𑄀 | CHAKMA SIGN CANDRABINDU | /◌̃/ | Nasalizes the preceding vowel (e.g., 𑄇𑄀 = /kã:/). |
| 𑄁 | CHAKMA SIGN ANUSVARA | /ŋ/ | Adds a velar nasal consonant coda (e.g., 𑄇𑄁 = /ka:ŋ/). |
| 𑄂 | CHAKMA SIGN VISARGA | /h/ | Adds a voiceless glottal fricative coda (often softens/lengthens vowel). |
| 𑄴 | CHAKMA SIGN VIRAMA | /Ø/ | Mutes the inherent vowel `ā`, creating a bare consonant or cluster (e.g., 𑄇𑄴 = /k/). |
| 𑄵 | CHAKMA SIGN MAAYYAA | /j/ | Post-consonantal semi-vowel 'y' (Ya-phala). |

## 5. Lexical Rules for G2P Engine
When building the TTS text-normalization frontend, implement these specific phonological rules:
1. **Inherent Vowel Muting (Schwa Deletion)**: Unlike Hindi, Chakma's inherent vowel is long `/a:/`. Muting usually occurs explicitly via the Virama (𑄴). Unmarked word-final consonants usually retain the `/a:/` sound in formal reading, though colloquial speech may shorten or drop it.
2. **Allophonic Shifts**: `/pʰa:/` (𑄜) is frequently realized as `/fa:/`. `/bʰa:/` (𑄞) is frequently realized as `/va:/`.
3. **Nasal Assimilation**: The Anusvara (𑄁) assimilates to the place of articulation of the following stop consonant (e.g., velar /ŋ/ before /k/, labial /m/ before /p/).
