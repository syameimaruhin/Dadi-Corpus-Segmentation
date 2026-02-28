# Annotation Guidelines for Dadi Corpus Word Segmentation Gold Standard

This document outlines the standard guidelines used for the manual word segmentation of ancient Chinese and *Kanbun* (Sino-Japanese) texts sampled from the "Dadi Corpus". These rules ensure consistency, reliability, and academic rigor in constructing the gold standard dataset for evaluating algorithmic segmentation models.

## 1. Basic Principles

* **Definition of a Segmentation Unit**: The delineation of a segmentation unit is based on "semantic completeness" and "syntactic independence". A valid unit must possess an independent semantic meaning and be capable of serving as an independent component within a syntactic structure.
* **Granularity Standards**: 
    * **Coarse-grained (Merge)**: Applied to proper nouns to maintain their structural integrity as single units.
    * **Fine-grained (Split)**: Applied to loose grammatical combinations (e.g., verb-complement structures like "吃饱" [eat to fullness], "写完" [finish writing]), which should be split into smaller components.
* **Priority of Consistency**: In ambiguous cases, prioritizing the consistent treatment of similar structural types across the dataset is mandatory. If annotators are completely uncertain during the independent annotation phase, the boundary is temporarily marked with a question mark (`?`) for subsequent panel adjudication.

## 2. Specific Rules

### 2.1 Handling of Multi-syllabic Words and Phrases
* **Four Syllables and Above**: As a general rule, combinations of four or more syllables (excluding proper nouns and complete idioms) should be segmented and are not considered a single unit.
* **Exceptions**: Four-character idioms ( *Chengyu* ) or fixed phrases that have undergone lexicalization, possess strong structural cohesion, and carry specific derived/transferred meanings must be kept intact and not segmented.

### 2.2 Proper Nouns
* **Personal Names**: When a surname and given name are used together, they are treated as a single entity and are not segmented (e.g., "李白" [Li Bai], "藤原定家" [Fujiwara no Teika]). Furthermore, when a name is combined with a courtesy name, alias, honorific title, or posthumous title, and functions as a fixed reference in the text, it is also treated as a whole (e.g., "李太白" [Li Taibai], "白乐天" [Bai Letian], "藤原朝臣万里" [Fujiwara no Ason Banri]).
* **Places and Institutions**: Proper nouns representing countries, ethnic groups, and geographic locations are treated as whole units.
* **Time Words**: Time-related terms with indivisible semantics, such as month names and era names ( *Nianhao* ), are treated as single units.

### 2.3 Function Words and Affix Structures
* **Verb + Dynamic Particle**: Loose structures with a low degree of fixation, such as a verb followed by a particle (e.g., "看着" [looking], "叫着" [calling], "走着" [walking]), should be segmented.
* **Other Function Words**: Sentence-final modal particles and conjunctions should generally be segmented independently.

### 2.4 Fixed Collocations
* **"子曰" (The Master said)**: Given the exceptionally high frequency of "子曰" in ancient texts and its special function as a discourse marker, it is treated as a single, inseparable unit.
* **General "曰" (said)**: For other "[Subject] + 曰" structures (e.g., "靖曰" [Jing said], "孟德曰" [Mengde said]), they are treated as standard subject-predicate structures and must be segmented (e.g., "靖 / 曰").

### 2.5 Transliterations and Loanwords
* **Complete Transliterations**: Semantically complete transliterated loanwords—especially Buddhist terminology and Sanskrit transliterations—are treated as whole units and not segmented (e.g., "涅槃" [Nirvana], "波罗蜜" [Paramita]).
* **Incomplete Transliterations**: Fragments of transliterated words caused by text corruption or excerpting (which lack complete semantic meaning) should be treated as noise data or segmented into single characters.

## 3. Dictionaries and Reference Tools

During the manual annotation and adjudication process, annotators are required to consult the following authoritative dictionaries and platforms to resolve lexical ambiguities:

* **HanDian (汉典)**: [https://www.zdic.net/](https://www.zdic.net/)
* **Grand Chinese Dictionary (汉语大词典)**: [https://www.hanyucidian.org/?lang=zh_jt](https://www.hanyucidian.org/?lang=zh_jt)
* **Chinese Text Project (中國哲學書電子化計劃)**: [https://ctext.org/zhs](https://ctext.org/zhs)
* **Zi.tools (字統网)**: [https://zi.tools/](https://zi.tools/)

*Note: In actual practice, annotators should also cross-reference the original source literature, published scholarly editions, and their corresponding annotations to guide correct punctuation and boundary identification.*
