# Теоретические пределы контейнеров данных (Theoretical Limits of Data Containers)

Этот конспект предназначен для интеграции в раздел **Discussion** или **Future Work** диссертации. Он объясняет физическую причину парадокса раздувания файлов BPC и предлагает теоретически оптимальные пути решения.

## 1. Проблема: Избыточность 24-битного Truecolor
В эмпирическом исследовании BPC-варианты сохранялись в стандартный 24-битный формат PNG (Truecolor). Это значит, что на каждый пиксель всегда выделялось 3 байта, даже если реальное количество уникальных цветов в изображении составляло всего 64 (вариант `b2`) или 8 (вариант `b1`). Из-за того, что классические пространственные фильтры PNG не справляются с резкими "ступеньками" (постеризацией) при квантовании, алгоритм DEFLATE не смог эффективно сжать эти данные, что привело к раздуванию размера файлов.

## 2. Теоретическое решение 1: Indexed PNG (Палитровые форматы)
Формат PNG поддерживает индексированные режимы (Color Type 3) с глубиной цвета 1, 2, 4 и 8 бит.
* Для варианта **b1** (8 цветов) можно использовать 4-битный индексированный режим. Это позволяет упаковать 2 пикселя в 1 байт на уровне контейнера. Сырой объем данных сокращается в **6 раз** еще до сжатия.
* Использование палитры позволяет пространственным фильтрам PNG работать с плотными цепочками битов, что потенциально может сжать датасет `b1` до теоретического энтропийного минимума (около 30-50 МБ).

## 3. Теоретическое решение 2: Bit-Packing и словарные алгоритмы (LZMA)
Классические графические форматы (JPEG, PNG) создавались для человеческого зрения. Для задач машинного зрения (Machine-Centric Vision) более перспективным является создание кастомных бинарных контейнеров:
* **Bit-Packing (Побитовая упаковка):** Упаковка битов вплотную. Например, вариант `b4` (12 бит на пиксель) можно упаковывать в памяти без пустых нулей, полностью используя каждый байт. 
* **LZMA Сжатие:** Если сжать такой плотный бинарный поток мощным словарным 1D-алгоритмом (например, LZMA), архиватор легко найдет повторяющиеся паттерны в ступенчатых градиентах, с которыми не справился PNG.

## 4. Готовый блок текста для статьи (на английском)
*Этот текст можно вставить в `article.tex` в раздел 5 (Discussion) или 6.3 (Future Work).*

### 5.X. Theoretical Limits of Data Containers and Bit-Packing
The empirical storage paradox observed in the bit-depth reduction (BPC) branch highlights a fundamental limitation of human-centric data containers. In this study, all BPC variants were encoded using the 24-bit Truecolor PNG standard. Consequently, heavily quantized variants such as $b1$ (which contains a maximum of $2^3 = 8$ unique colors) still allocated 3 bytes per pixel, relying entirely on spatial prediction filters and DEFLATE entropy coding to eliminate the redundancy. However, the artificial color banding induced by BPC behaves as high-frequency spatial noise, causing the PNG spatial filters to fail and inflating the final file size.

From a theoretical perspective, this inefficiency can be resolved by transitioning to machine-centric container architectures. For extreme quantization ($b \le 2$), utilizing indexed paletted formats (e.g., 4-bit or 8-bit Indexed PNG) would instantly reduce the raw uncompressed data footprint by a factor of 3 to 6. Furthermore, future machine vision pipelines operating on edge devices could abandon classical image formats entirely in favor of raw bit-packing. By packing the exact number of bits per channel (e.g., packing a $b4$ pixel strictly into 12 bits) and compressing the resulting binary stream with a robust 1D dictionary coder like LZMA, systems could bypass the structural overhead of 2D spatial filtering. This underscores a critical architectural conclusion: for deep learning pipelines, the physical data container format is just as deterministic to storage efficiency as the quantization algorithm itself.
