# Visual Analysis of Compression Distortion: JPEG vs BPC

This document provides a detailed description and scientific analysis of visual image degradation for two main experiments: **JPEG Recompression** and **Bit-Depth Reduction (BPC)**.

The analysis is performed using the sample image **`000000029596.jpg`** from the COCO val2017 dataset (resolution $640 \times 428$ pixels, full size).

---

## Source Scene Description

The image represents a typical indoor scene (home interior) with several objects of varying scales and textures:
* **Couch** in the left foreground — a large object with a distinct soft upholstery texture and smooth light-shadow transitions.
* **Dining Table** in the center — a wooden surface with medium reflectivity.
* **Chairs** — medium-sized objects with thin legs and backrests (high-frequency details).
* **TV** in the right background — a contrasting rectangular object positioned against a wall with a soft lighting gradient.

This scene is ideal for comparison, as it contains both **low-frequency regions** (smooth gradients on the walls and couch) and **high-frequency boundaries** (chair legs, corners of the TV and table).

---

## Figure 8: Degradation from JPEG Recompression

The $3 \times 2$ grid (`fig8_jpeg_visual_degradation_grid.png`) demonstrates the impact of reducing JPEG quality according to the following scheme:
```text
Original (Uncompressed) | q94 (Very Light) | q88 (Light)
q75 (Moderate)          | q50 (Heavy)      | q25 (Aggressive)
```

### Step-by-Step Distortion Changes:

1. **Original (Uncompressed)**
   * The baseline image with original sharpness. Object boundaries are clear, coding noise is absent, and YOLOv8n confidently detects the couch, TV, dining table, and chairs.
2. **q94 & q88 (Light Degradation)**
   * Visually indistinguishable from the original without high magnification. The Discrete Cosine Transform (DCT) algorithm compresses redundant high-frequency components. All boundaries and thin structures (chair legs) remain sharp.
   * **Impact on YOLO**: Practically zero. The detector maintains accuracy at the baseline level.
3. **q75 (Moderate Compression)**
   * Barely noticeable artifacts begin to appear on contrasting edges (e.g., around the TV frame and table edges) as slight blurring or "ringing artifacts". The microtexture on the couch is slightly smoothed out.
   * **Impact on YOLO**: Minor drop in metrics (less than 1-2% mAP50), as the object structures are still easily read.
4. **q50 (Heavy Compression)**
   * The block structure of JPEG ($8 \times 8$ pixel block grid) clearly emerges. Gradient transitions on the walls become stepped. Small details (chair legs in the background) begin to merge with the background.
   * **Impact on YOLO**: Noticeable drop in Recall. It becomes harder for the model to localize the boundaries of small and distant objects.
5. **q25 (Aggressive Compression)**
   * Severe pixelation and blurring. Object boundaries become jagged and stepped. High-frequency details are completely lost. Rough DCT artifact halos are observed around all contrasting elements.
   * **Impact on YOLO**: Critical drop in metrics (mAP50 falls from 0.518 to 0.407). The model loses the ability to detect the small chairs and confuses the table's boundaries.

---

## Figure 9: Degradation from Bit-Depth Reduction (BPC)

The $3 \times 2$ grid (`fig9_bpc_visual_degradation_grid.png`) demonstrates the impact of color quantization per channel according to the following scheme:
```text
Original (8 bit) | b7 (7 bit) | b4 (4 bit)
b3 (3 bit)       | b2 (2 bit) | b1 (1 bit)
```

### Step-by-Step Distortion Changes:

1. **Original (8 bit / 256 levels per channel)**
   * The initial color representation (24-bit RGB). Smooth color transitions in all areas.
2. **b7 (7 bit / 128 levels per channel)**
   * No visual differences. The quantization is too soft for the human eye or YOLO's convolutional layers to notice a difference. Detection metrics are identical to the original.
3. **b4 & b3 (Moderate Quantization / Posterization)**
   * **Visual Effect**: A pronounced **posterization (color banding)** effect appears. Smooth half-tones and shadows on the walls, couch, and table surface break into distinct, flat zones of uniform color with sharp boundaries (stepped gradient).
   * **Scientific difference from JPEG**: Unlike JPEG, which blurs the image, BPC preserves the mathematical sharpness of boundaries but completely alters the distribution of local contrast gradients. The chair legs are still geometrically sharp, but their colors are distorted.
   * **Impact on YOLO**: Moderate degradation. The neural network begins to lose textural features, but the geometric contours help retain the detection of medium-sized objects.
4. **b2 (2 bit / 4 levels per channel / 64 colors total)**
   * The image takes on a pronounced "retro-computer" appearance. Almost all textures are destroyed. Huge, monotone patches of basic colors remain on the couch and walls. The depth of the scene is lost.
   * **Impact on YOLO**: Catastrophic drop in accuracy (mAP50 falls to 0.291). The detector misses small objects and confuses classes due to the total loss of gradient information.
5. **b1 (1 bit / 2 levels per channel / 8 colors total)**
   * Extreme regime. Each pixel in an RGB channel can only take values of 0 or 255. The image disintegrates into crude, high-contrast, multi-colored silhouettes. Half of the objects in the scene visually merge into single black or colored spots.
   * **Impact on YOLO**: Complete failure of the detection system (mAP50 falls to 0.132). The local features (HOG/Convolutional brightness gradients) that the YOLO feature extractor trained on are entirely destroyed.

---

## Scientific Conclusion: Difference in Degradation Types

| Characteristic | JPEG Recompression | Bit-Depth Reduction (BPC) |
| :--- | :--- | :--- |
| **Main type of distortion** | High-frequency noise, DCT blocking, boundary blurring. | Posterization, stepped gradients (color banding), loss of half-tones. |
| **Boundary preservation** | Boundaries are smoothed, blurred, and covered with halos. | Geometric boundaries remain absolutely sharp but change color. |
| **Impact on file size** | **Efficient**: Significant weight reduction (up to 8x) with good metric retention. | **Inefficient (in PNG)**: The file size of b7 actually increases; savings only begin at critical destruction of the frame. |
| **YOLOv8 behavior** | Tolerant of moderate compression (down to q75/q50), as contours and context are preserved. | Extremely sensitive to quantization (below b4), as sharp artificial gradient steps confuse the convolutional filters. |
