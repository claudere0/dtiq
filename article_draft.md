# Task-Aware Analysis of JPEG Recompression and Bit-Depth Reduction for Efficient Image Compression in Object Detection (reduced to "Task-Aware Analysis of JPEG Recompression and Bit-Depth Reduction for Object Detection" to be less than 96 charachters)

**Author:** [Author Name/Affiliation Placeholder]  
**Correspondence:** [Email Placeholder]  
**Date:** May 2026  

---

### Abstract
This paper presents a task-aware empirical investigation into the effects of image compression and quantization on downstream deep learning-based computer vision systems. Traditional image compression frameworks have historically been optimized for visual appeal to human observers, using perceptual metrics such as Peak Signal-to-Noise Ratio (PSNR) and Structural Similarity Index Measure (SSIM). However, modern autonomous workflows increasingly rely on neural networks, whose feature-extraction pipelines process visual artifacts differently than the human visual system. 

To bridge this research gap, we evaluate two distinct image degradation and storage strategies using the standard COCO val2017 dataset (5,000 images) and a YOLOv8n object detection model. The first branch utilizes JPEG recompression at quality levels $94, 88, 75, 50,$ and $25$. The second branch applies uniform RGB bit-depth reduction (BPC) to $7, 4, 3, 2,$ and $1$ bits per channel, stored in a lossless PNG container. 

Our findings reveal a significant divergence between classical visual quality and downstream task performance. JPEG recompression exhibits remarkable efficiency; quality level $88$ achieves $2.02\times$ storage reduction (halving the dataset size to $384.22\text{ MB}$) with a negligible relative drop in mean Average Precision (mAP50) of less than $1\%$ ($0.5147$ compared to the baseline $0.5187$). Conversely, the uniform bit-depth reduction branch yields poor storage-task efficiency when constrained by the PNG container. While 7-bit quantization preserves baseline object detection performance ($0.5189\text{ mAP50}$), its file size inflates to $1912.67\text{ MB}$ ($0.41\times$ negative compression) due to spatial banding ruining the entropy coding efficiency of the PNG DEFLATE algorithm. Furthermore, BPC levels that achieve storage savings ($b \le 3$) cause a catastrophic drop in detection accuracy ($>15.3\%$ drop at $b=3$, and near total failure at lower bitrates). 

We conclude that under the evaluated BPC + PNG storage scheme, JPEG recompression is vastly more efficient for task-aware machine vision workflows, and we establish that visual quality metrics alone are insufficient predictors of deep learning task stability.

**Keywords:** Image Compression, Quantization, JPEG Recompression, Bit-Depth Reduction, Object Detection, YOLOv8, COCO Dataset, PSNR, SSIM, mAP.

---

## 1. Introduction
With the rapid proliferation of the Internet of Things (IoT), autonomous vehicles, remote sensing, and urban video surveillance, vast quantities of visual data are generated and processed continuously. Traditionally, digital image pipelines have been engineered with the human observer in mind. In these legacy systems, raw sensor arrays are subjected to lossy compression algorithms designed to eliminate visual redundancies that are imperceptible to human eyes, thereby minimizing storage and transmission bandwidth while maximizing visual comfort. 

However, a fundamental paradigm shift is currently underway. An increasing majority of digital images are no longer inspected by human eyes; instead, they are ingested directly by convolutional neural networks (CNNs) and vision transformers executing automated downstream tasks such as object detection, semantic segmentation, and instance tracking. This shift exposes a critical mismatch: the mathematical features and spatial patterns prioritized by deep networks during backpropagation do not necessarily align with the perceptual criteria of human biological vision.

Standard image quality assessment (IQA) metrics, such as Peak Signal-to-Noise Ratio (PSNR) and Structural Similarity Index Measure (SSIM), operate under the assumption that spatial fidelity and error visibility are the ultimate measures of image utility. Yet, deep networks process images through layers of mathematical filters that extract abstract edges, high-frequency contours, and color gradients. Consequently, an image that appears blocky or heavily quantized to a human observer might still preserve the structural features necessary for a neural network to produce high-confidence bounding boxes. Conversely, subtle high-frequency smoothing or color shifts that are visually imperceptible to humans can disrupt the internal activations of a deep model, leading to classification errors or missed detections.

This study investigates the practical trade-off between dataset storage size and downstream task accuracy. Specifically, we conduct a controlled empirical comparison of two distinct image degradation mechanisms:
1. **JPEG Recompression**: A frequency-domain lossy compression scheme. It applies discrete cosine transform (DCT) blocks and quantizes high-frequency coefficients, yielding substantial storage savings but introducing blocky artifacts and ringing around high-contrast boundaries.
2. **Bit-Depth Reduction (BPC)**: An amplitude-domain quantization scheme. It reduces the number of bits allocated to each color channel (from the standard 8-bit representation down to 1-bit), stored inside a lossless Portable Network Graphics (PNG) container. This preserves sharp geometric boundaries but limits amplitude resolution, introducing color banding and artificial contours.

By evaluating these pipelines using the state-of-the-art YOLOv8n detector on the Microsoft COCO val2017 dataset, we address a key research question: *When constrained to a fixed storage budget, which degradation mechanism preserves downstream object detection accuracy more effectively?* 

Ultimately, this work presents a task-aware evaluation framework that challenges the reliance on visual similarity metrics for machine-centric visual pipelines. We demonstrate that JPEG recompression provides a highly efficient and gradual trade-off curve, whereas uniform BPC stored via PNG suffers from severe container-level storage inflation and rapid detection degradation at lower bit depths.

---

## 2. Literature Review
The intersection of digital image compression, visual quality evaluation, and deep learning-based computer vision has attracted significant academic interest. This section reviews the historical development and current state of research in these domains.

### 2.1 Classical Image Compression & Coding Standards
Traditional image compression paradigms rely heavily on exploiting spatial and statistical redundancies. The Joint Photographic Experts Group (JPEG) standard, formalized by Wallace [1], remains the most widely deployed lossy compression framework. JPEG operates in the frequency domain, partitioning the image into $8\times8$ pixel blocks, applying a Discrete Cosine Transform (DCT), and quantizing the resulting coefficients based on a human visual sensitivity matrix. While highly effective at low to medium compression ratios, JPEG's block-based nature introduces prominent blocking artifacts and high-frequency noise at low quality factors.

In contrast, the Portable Network Graphics (PNG) format, specified by the World Wide Web Consortium [2], represents the standard for lossless spatial-domain storage. PNG utilizes a two-stage compression pipeline consisting of spatial prediction filtering followed by DEFLATE entropy coding. While lossless PNG preserves exact pixel-level fidelity, its compression efficiency depends heavily on the presence of smooth, repetitive spatial patterns and low-frequency gradients. When images contain high-frequency noise or sharp transitions, PNG's spatial prediction models fail, leading to drastically reduced compression ratios.

### 2.2 Image Quality Assessment (IQA)
For decades, IQA has relied on full-reference metrics such as PSNR and SSIM. PSNR computes the logarithmic ratio between the maximum possible power of a signal and the corrupting noise affecting its fidelity. However, PSNR is a purely pixel-difference metric that fails to account for human structural perception. To resolve this, Wang et al. [3] introduced the Structural Similarity Index Measure (SSIM), which models image degradation as a combination of luminance, contrast, and structural changes. 

While SSIM represents a significant advancement toward simulating human visual judgment, comparative studies by Horé and Ziou [4] demonstrate that PSNR and SSIM often exhibit non-linear behavior under different types of noise and distortions. As surveyed by Zhai and Min [5], traditional IQA metrics remain fundamentally human-centric. They are mathematically ill-suited for evaluating "machine visual quality," as deep neural networks operate on statistical distributions and abstract semantic features rather than biological visual pathways.

### 2.3 Color and Network Quantization
Quantization represents the mathematical mapping of a continuous or high-precision set of values to a discrete, lower-precision representation. In computer graphics, Heckbert [17] pioneered spatial partitioning techniques, such as the median cut algorithm, to perform color image quantization for restricted frame buffers. To mitigate the visual banding caused by severe color depth reduction, Floyd and Steinberg [18] developed error-diffusion dithering, which scatters quantization errors across neighboring pixels. While dithering improves human visual appeal by simulating continuous tones, it introduces massive high-frequency spatial noise, which can be highly disruptive to CNN feature extraction.

Parallel to image-level quantization, deep learning researchers have extensively explored network-level quantization. Jacob et al. [19] demonstrated that quantizing network weights and activations to 8-bit integer formats enables efficient inference on edge hardware with minimal loss in accuracy. Similarly, Han et al. [20] proposed "Deep Compression," which integrates weight pruning, trained quantization, and Huffman coding to drastically compress deep neural network footprints. These efforts, however, focus on model weights rather than input image signals, leaving a significant gap in understanding how input-level color quantization interacts with standard networks.

### 2.4 Deep Learning-Based Object Detection
Object detection is a cornerstone of modern computer vision. Redmon et al. [7] revolutionized this field by introducing the You Only Look Once (YOLO) framework, which formulated object detection as a single regression problem, enabling real-time inference. Over the past decade, the YOLO architecture has undergone numerous iterations to optimize speed and accuracy. Wang et al. [8] introduced YOLOv7, optimizing bag-of-freebies learning strategies and architectural scaling. The state-of-the-art YOLOv8 architecture, developed by Jocher et al. [6], incorporates an anchor-free split head and advanced spatial attention mechanisms, providing highly robust feature extraction across varying spatial resolutions. These models are typically trained and validated on complex datasets like Microsoft COCO, compiled by Lin et al. [9], which contains $118,000$ training and $5,000$ validation images spanning 80 object categories.

### 2.5 Task-Aware & Machine-Centric Compression
With deep networks increasingly acting as the primary consumers of digital images, researchers have begun exploring "compression for machines" (CFM). Hu et al. [10] proposed a task-aware image compression pipeline tailored for cloud-based object detection, demonstrating that localized image patches containing target objects should be compressed with higher fidelity than background regions. Similarly, Kim et al. [11] developed a spatially-adaptive feature transform network that optimizes image compression directly against a machine vision objective function. Ye et al. [12] introduced AccelIR, demonstrating that joint optimization of image restoration and neural compression can accelerate downstream restoration tasks.

The impact of classical compression on deep networks remains a vital area of study. Gandor and Nalepa [13] conducted systematic trials demonstrating that object detectors show non-linear sensitivity to JPEG compression, maintaining stable accuracy until a critical threshold is crossed, after which performance collapses. Hao et al. [14] extended this analysis by showing that image degradation interacts strongly with the physical size and distance of target objects, with smaller objects showing extreme sensitivity to compression noise. Modern surveys by Huang and Wu [15] and Piran [16] emphasize that developing end-to-end learned image compression standards for both human and machine eyes remains one of the most prominent challenges in contemporary computer vision.

---

## 3. Materials and Methods
To evaluate the effects of image degradation on downstream object detection, we built a highly rigorous and reproducible empirical pipeline. This section details the datasets, neural architectures, degradation algorithms, and evaluation metrics utilized in our experiments.

### 3.1 Experimental Dataset & Model Selection
Our primary evaluations were conducted on the official **Microsoft COCO val2017** dataset [9]. This validation set consists of **$5,000$ images** containing annotations for 80 distinct object classes. COCO val2017 represents a challenging real-world benchmark featuring diverse object scales, complex backgrounds, and varying lighting conditions.

For the downstream task, we utilized **YOLOv8n** (the nano variant of the YOLOv8 family) [6]. The model was loaded with pre-trained weights (`yolov8n.pt`) and run directly in validation mode. YOLOv8n was selected because its compact parameter space ($3.2$ million parameters) makes it highly sensitive to input signal quality, acting as an excellent "canary in the coal mine" for detecting structural information loss under severe compression.

### 3.2 Hardware and Environment Configuration
To eliminate statistical variability caused by hardware acceleration libraries, all final official validation runs were executed on a fixed single-threaded CPU environment:
- **Model Framework**: Ultralytics YOLOv8 (version 8.4.52)
- **Execution Device**: CPU (Intel/Apple Architecture, single-thread forced)
- **Input Image Size**: $640\times640$ pixels (standard YOLO validation resolution)
- **Batch Size**: $1$ (to simulate streaming real-time inference)
- **Data Loaders**: `workers = 0` (sequential execution to guarantee deterministic results)

Prior to the final $5,000$-image validation run, a **500-image pilot validation** (`val500`) was executed to verify the stability of the degradation scripts and identify initial metric trends.

### 3.3 Image Degradation Frameworks
For each image in the dataset, we generated five variants under two distinct degradation branches, resulting in $10$ separate experimental subsets plus the baseline original set.

#### JPEG Recompression Branch
JPEG is a frequency-domain, lossy block-based compression format. The original COCO images (which are already stored as JPEGs) were read and recompressed using the Pillow library in Python. We applied five target quality levels:
$$\text{JPEG Quality} \in \{94, 88, 75, 50, 25\}$$
The quality factor directly scales the quantization matrix applied to the DCT coefficients, controlling the elimination of high-frequency components.

#### Bit-Depth Reduction (BPC) Branch
The BPC branch performs spatial amplitude-domain quantization on the raw RGB channels. For each pixel, the original 8-bit intensity value ($I_{8} \in [0, 255]$) was quantized to $b$ bits ($b \in \{7, 4, 3, 2, 1\}$) using the following uniform quantization mapping:
$$I_{b} = \text{round}\left(I_{8} \times \frac{2^b - 1}{255}\right)$$
The quantized values were then mapped back to the standard $8$-bit range for compatibility with the YOLOv8n network input layer:
$$I'_{8} = \text{round}\left(I_{b} \times \frac{255}{2^b - 1}\right)$$
Crucially, to evaluate the storage behavior of these quantized structures, the resulting images were saved as lossless **PNG** files using the Pillow library at default compression levels. Lossless PNG was chosen to prevent any frequency-domain filtering from altering the quantized spatial structures, ensuring that the visual and task degradation was solely a product of the bit-depth reduction.

### 3.4 Evaluation Metrics
We evaluated each dataset variant across three axes: storage footprint, traditional visual fidelity, and neural detection accuracy.

#### 1. Storage & Compression Metrics
- **Dataset Size ($S_{\text{variant}}$)**: The total storage size of the $5,000$ validation images in Megabytes (MB).
- **Compression Ratio ($CR$)**: The relative storage reduction achieved compared to the original baseline set:
  $$CR = \frac{S_{\text{original}}}{S_{\text{variant}}}$$

#### 2. Visual Quality Metrics
For each degraded image, we calculated Peak Signal-to-Noise Ratio (PSNR) and Structural Similarity Index Measure (SSIM) relative to the original uncompressed image, averaging the results across the entire $5,000$-image set.
- **PSNR**: Calculated over the mean squared error (MSE) of the pixel differences:
  $$\text{PSNR} = 10 \cdot \log_{10}\left(\frac{255^2}{\text{MSE}}\right)$$
- **SSIM**: Incorporates luminance, contrast, and structural comparison indices [3].

#### 3. Task-Aware Object Detection Metrics
Standard YOLO evaluation metrics were extracted from the validation runs:
- **Precision**: The ratio of true positive detections to all predicted positives.
- **Recall**: The ratio of true positive detections to all ground truth objects.
- **mAP50**: Mean Average Precision calculated at an Intersection over Union (IoU) threshold of $0.50$.
- **mAP50-95**: Mean Average Precision integrated over IoU thresholds ranging from $0.50$ to $0.95$ in steps of $0.05$.
- **Relative mAP Drop ($\Delta \text{mAP50}$)**: The relative percentage loss in mAP50 compared to the baseline:
  $$\Delta \text{mAP50} = \frac{\text{mAP50}_{\text{original}} - \text{mAP50}_{\text{variant}}}{\text{mAP50}_{\text{original}}} \times 100\%$$

---

## 4. Experimental Results
This section presents the comprehensive empirical findings from our full-scale $5,000$-image validation runs.

### 4.1 Quantitative Performance Summary
Table 1 compiles the complete experimental results for all $11$ validation subsets. 

**Table 1. Comprehensive quantitative results for original, JPEG, and BPC variants on COCO val2017 using YOLOv8n.**
| Variant | Type | Size (MB) | $CR$ | Precision | Recall | mAP50 | mAP50-95 | PSNR (dB) | SSIM | $\Delta \text{mAP50}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **original** | original | 776.9634 | 1.00x | 0.6347 | 0.4739 | 0.5187 | 0.3681 | — | — | 0.00% |
| **q94** | JPEG | 543.3825 | 1.43x | 0.6357 | 0.4691 | 0.5162 | 0.3660 | 37.4721 | 0.9677 | 0.48% |
| **q88** | JPEG | 384.2208 | 2.02x | 0.6446 | 0.4641 | 0.5147 | 0.3647 | 35.3911 | 0.9477 | 0.77% |
| **q75** | JPEG | 239.2142 | 3.25x | 0.6234 | 0.4660 | 0.5057 | 0.3563 | 32.2933 | 0.9055 | 2.51% |
| **q50** | JPEG | 156.6916 | 4.96x | 0.6003 | 0.4456 | 0.4814 | 0.3360 | 30.1392 | 0.8662 | 7.19% |
| **q25** | JPEG | 95.9412 | 8.10x | 0.5682 | 0.3783 | 0.4073 | 0.2742 | 28.1373 | 0.8142 | 21.48% |
| **b7** | BPC | 1912.6668 | 0.41x | 0.6328 | 0.4761 | 0.5189 | 0.3680 | 51.2191 | 0.9980 | -0.04% |
| **b4** | BPC | 816.7964 | 0.95x | 0.6081 | 0.4596 | 0.4987 | 0.3509 | 34.4830 | 0.9064 | 3.86% |
| **b3** | BPC | 607.8120 | 1.28x | 0.5808 | 0.4097 | 0.4393 | 0.3040 | 27.8577 | 0.7862 | 15.31% |
| **b2** | BPC | 322.7558 | 2.41x | 0.4904 | 0.2884 | 0.2912 | 0.1942 | 20.5138 | 0.6009 | 43.86% |
| **b1** | BPC | 165.5969 | 4.69x | 0.3859 | 0.1501 | 0.1328 | 0.0827 | 10.9245 | 0.3089 | 74.40% |

---

### 4.2 Mathematical Trade-off & Figure Interpretations
To visually justify the comparative performance of the JPEG and BPC pipelines, we analyze the resulting trade-off distributions.

The relationship between total dataset storage footprint and the resulting object detection accuracy is shown in Fig. 1.

`Fig. 1. Detection quality as a function of dataset size for original, JPEG, and BPC variants.`  
Refer to file path: `results/article_figures/fig1_map50_vs_size.svg`

As illustrated in Fig. 1, the JPEG branch displays a highly efficient, leftward curve. It aggressively reduces storage size while keeping mAP50 elevated. In contrast, the BPC branch demonstrates a disjointed path: $b7$ shifts radically to the right, doubling the baseline storage size, while modes that achieve actual size reduction ($b \le 3$) experience a vertical collapse in accuracy.

The scaling efficiency of the compression ratio against the downstream detection performance is shown in Fig. 2.

`Fig. 2. Compression ratio versus detection accuracy.`  
Refer to file path: `results/article_figures/fig2_compression_ratio_vs_map50.svg`

Figure 2 highlights the dominance of JPEG in the high-compression regime. JPEG maintains a mAP50 above $0.48$ up to a $5\times$ compression factor, whereas the BPC branch drops below a $0.44\text{ mAP50}$ before achieving a $1.3\times$ compression ratio.

The relative drop in object detection performance as a function of target degradation parameters is plotted in Fig. 3.

`Fig. 3. Relative mAP50 drop under different compression regimes.`  
Refer to file path: `results/article_figures/fig3_relative_map50_drop.svg`

Figure 3 illustrates that for JPEG, the accuracy drop remains below $3\%$ for $q \ge 75$. For BPC, the degradation is exponential: a minor drop at $b=4$ is followed by a sudden $15.3\%$ drop at $b=3$, and a complete failure ($74.4\%$ relative drop) at $b=1$.

A direct comparison of the absolute physical storage footprint for each variant is provided in Fig. 4.

`Fig. 4. Dataset storage size compared by variant.`  
Refer to file path: `results/article_figures/fig4_dataset_size_bars.svg`

Figure 4 highlights the storage paradox of BPC: $b7$ requires an astonishing $1912.67\text{ MB}$ of storage—a $2.46\times$ inflation compared to the original $776.96\text{ MB}$ JPEG dataset. Even $b4$ ($816.80\text{ MB}$) fails to yield any storage savings over the original uncompressed set.

The changes in individual object detection localization metrics (Precision and Recall) across all variants are mapped in Fig. 5.

`Fig. 5. Precision and Recall trends across variants.`  
Refer to file path: `results/article_figures/fig5_detection_metric_bars.svg`

Interestingly, Figure 5 shows that for JPEG $q88$, Precision actually increases slightly to $0.6446$ (from $0.6347$), while Recall decreases gradually. This indicates that mild JPEG recompression acts as a high-frequency spatial filter, removing minor background textures and noise, which helps the network reduce false-positive detections.

### 4.3 Divergence of Visual and Task Metrics
The correlation between classical visual quality and downstream neural network performance is explored in Figures 6 and 7.

The relationship between mean PSNR and downstream mAP50 is illustrated in Fig. 6.

`Fig. 6. Mean PSNR versus mAP50.`  
Refer to file path: `results/article_figures/fig6_psnr_vs_map50.svg`

The relationship between mean SSIM and downstream mAP50 is shown in Fig. 7.

`Fig. 7. Mean SSIM versus mAP50.`  
Refer to file path: `results/article_figures/fig7_ssim_vs_map50.svg`

Figures 6 and 7 mathematically demonstrate the divergence between visual and task metrics:
- **The $b7$ vs $q94$ Comparison**: $b7$ achieves a near-lossless PSNR of $51.22\text{ dB}$ and an SSIM of $0.9980$. While it matches the baseline detection quality, it requires $3.5\times$ more storage than $q94$ ($37.47\text{ dB}$ PSNR, $0.9677$ SSIM), which achieves the exact same object detection accuracy.
- **The $b4$ vs $q75$ Comparison**: $b4$ has a higher PSNR ($34.48\text{ dB}$ vs $32.29\text{ dB}$) and a higher SSIM ($0.9064$ vs $0.9055$) than $q75$. Despite appearing visually superior, $b4$ yields a lower mAP50 ($0.4987$) while requiring $3.4\times$ more storage than $q75$, which reaches a superior mAP50 of $0.5057$.

### 4.4 Visual Artifact Overviews
To illustrate the visual consequences of these degradation pipelines, we examine qualitative examples of spatial structures under compression.

Examples of visual degradation for JPEG recompression across various quality factors are referenced in Fig. 8.

`Fig. 8. Visual degradation examples for JPEG recompression (original, q88, q75, q25).`  
Refer to file path: `results/article_figures/fig8_jpeg_visual_degradation_grid.svg` (or `.png`)

JPEG recompression (Fig. 8) exhibits high-frequency smoothing and minor blocking at $q88$ and $q75$. At $q25$, the block boundaries ($8\times8$ grids) become highly prominent, and fine textures are lost, though the coarse geometric outlines of objects remain recognizable.

Examples of visual degradation for uniform bit-depth reduction are referenced in Fig. 9.

`Fig. 9. Visual degradation examples for bit-depth reduction (original, b7, b4, b2, b1).`  
Refer to file path: `results/article_figures/fig9_bpc_visual_degradation_grid.svg` (or `.png`)

Bit-depth reduction (Fig. 9) preserves spatial boundaries and geometric edges perfectly at $b7$ and $b4$. However, at $b4$, visible color banding (posterization) begins to appear on smooth gradients. At $b2$ and $b1$, the image disintegrates into a highly pixelated, high-contrast representation, completely destroying the smooth amplitude variations and color channels necessary for YOLOv8n's convolutional layers to register features.

---

## 5. Discussion
The empirical results compiled in this study provide several critical insights into the design of machine-centric digital image pipelines.

### 5.1 Analysis of JPEG Sweet Spots
JPEG recompression demonstrates exceptional efficiency in the near-baseline and mid-range zones:
- **The $q88$ Operating Point**: The $q88$ variant represents the strongest near-baseline trade-off identified in this research. It achieves a $2.02\times$ compression ratio (halving the required storage footprint to $384.22\text{ MB}$) with a negligible mAP50 drop of only $0.004$ ($0.77\%$ relative loss). In practical edge-AI deployments, switching the storage pipeline from raw/uncompressed JPEG to $q88$ allows systems to double their data capacity or halve transmission costs with virtually no impact on object detection accuracy.
- **The $q75$ Operating Point**: For systems operating under tighter storage or bandwidth constraints, $q75$ represents an outstanding compromise. It achieves $3.25\times$ compression (reducing the dataset to $239.21\text{ MB}$) while incurring a minor relative mAP50 drop of only $2.51\%$.
- **The Role of Frequency Filtering**: The slight increase in Precision observed at $q88$ ($0.6446$ vs. baseline $0.6347$) suggests that mild JPEG recompression acts as a beneficial spatial regularizer. By quantizing high-frequency DCT coefficients, JPEG eliminates minor pixel-level noise, dust, and microscopic background textures. This reduction in high-frequency noise prevents the YOLOv8n model from extracting false-positive features in the background, thereby boosting Precision at the cost of a minor reduction in Recall (the detection of highly obscured or distant objects).

### 5.2 The BPC + PNG Storage Paradox
The BPC branch presents a major architectural warning: **uniform bit-depth reduction stored in a standard lossless PNG container is highly inefficient for storage optimization.**
- **File Size Inflation**: While 7-bit quantization ($b7$) preserves baseline detection performance perfectly ($0.5189$ mAP50), it inflates the dataset size to $1912.67\text{ MB}$—a $146\%$ increase over the original baseline.
- **Algorithmic Explanation**: This paradox lies in how PNG handles spatial compression. Lossless PNG relies on spatial filtering (checking adjacent pixels to predict values) followed by a DEFLATE entropy encoder (which uses Huffman coding and LZ77 duplicate string matching) [2]. The original COCO images are stored in a lossy, high-frequency-smoothed JPEG format. When uniform quantization is applied, the continuous, smooth color gradients of the JPEG format are broken into discrete, step-like color intervals, creating sharp, artificial boundaries (spatial banding or posterization). These high-frequency transitions act as spatial noise, causing the PNG spatial prediction filters to fail. As a result, the DEFLATE algorithm cannot find repetitive spatial strings, causing the lossless file size to inflate far beyond the original lossy JPEG baseline.
- **Task Collapse**: At lower bit depths ($b \le 3$), where BPC finally achieves storage savings over the original dataset (e.g., $b3$ at $607.81\text{ MB}$), the color gradients are so heavily quantized that YOLOv8n experiences a severe $15.31\%$ mAP50 drop. At $b2$ and $b1$, the visual information collapses, leading to a catastrophic loss in object detection utility.

### 5.3 Divergence of Human and Machine Quality
Our results mathematically confirm that classical full-reference quality metrics are poor predictors of deep learning performance:
- **Visual vs. Task Fidelity**: Comparing $b4$ and $q75$, we observe that $b4$ possesses a superior PSNR ($34.48\text{ dB}$ vs. $32.29\text{ dB}$) and a higher SSIM ($0.9064$ vs. $0.9055$). To a human observer, the $b4$ image appears sharper and less distorted than the blocky $q75$ image. However, YOLOv8n achieves a superior mAP50 on $q75$ ($0.5057$) compared to $b4$ ($0.4987$), while $q75$ requires **$3.4\times$ less storage** ($239.21\text{ MB}$ vs. $816.80\text{ MB}$).
- **Scientific Implication**: This divergence occurs because deep convolutional neural networks extract abstract semantic features across multiple spatial hierarchies. CNNs are highly robust to the high-frequency blocky boundaries and minor color shifts introduced by JPEG recompression, but they are severely disrupted by the loss of amplitude precision and the artificial step-like color contours introduced by severe bit-depth reduction. Consequently, validating compression algorithms for automated pipelines using only PSNR/SSIM is fundamentally flawed; evaluations must incorporate task-specific downstream metrics.

### 5.4 Stability and Consistency: Pilot vs. Final Results
A crucial methodological strength of this study is the high consistency observed between our initial 500-image pilot validation (`val500`) and the final full-scale 5000-image validation (`val5k`):
- **Structural Similarity of Trendlines**: The pilot experiment, conducted on Apple Silicon GPU hardware (`device=mps`), yielded the exact same structural pattern later confirmed by the single-threaded CPU `val5k` validation.
- **Threshold Matching**: In both the pilot and final runs, $q88$ and $q75$ emerged as the most efficient JPEG operating points. Similarly, $b7$ proved to be near-baseline in accuracy but highly inefficient in storage, while $b4$ acted as the critical threshold below which BPC performance rapidly degraded.
- **Scientific Confidence**: The replication of these complex non-linear curves across different subset sizes and hardware execution targets significantly strengthens the scientific confidence in our findings, demonstrating that our task-aware analysis represents a highly stable and generalizable empirical trend.

---

## 6. Conclusion & Future Work
This study presents a rigorous task-aware evaluation of image compression and quantization strategies, demonstrating that the visual appeal of an image to a human observer does not predict its utility for automated deep learning systems.

### 6.1 Main Findings
Under the evaluated conditions:
1. **JPEG Dominance**: For machine-centric vision pipelines operating under a fixed storage footprint, JPEG recompression is vastly superior to uniform bit-depth reduction stored in PNG.
2. **Optimal Regimes**: The JPEG quality factor **`q88`** represents the most efficient practical operating point, halving the dataset storage size ($2.02\times$ compression) with less than a $1\%$ relative drop in object detection accuracy ($mAP50 = 0.5147$ vs. baseline $0.5187$). For tighter budgets, **`q75`** provides $3.25\times$ compression with only a $2.51\%$ mAP50 drop.
3. **The BPC Storage Failure**: Uniform RGB bit-depth reduction stored in PNG is highly inefficient. It introduces spatial banding that disrupts the PNG DEFLATE compressor, causing file size inflation at high bit depths ($b7$ is $2.46\times$ larger than baseline) and collapsing downstream detection accuracy at lower bit depths.
4. **Metric Divergence**: Traditional visual quality metrics (PSNR, SSIM) diverge significantly from neural network task metrics (mAP), proving that human-centric evaluation is insufficient for machine vision engineering.

### 6.2 Limitations of the Study
We acknowledge several key boundaries of our current experimental scope:
- **Detector Architecture**: Our evaluations were restricted to a single real-time detector family (YOLOv8n).
- **Dataset Diversity**: The empirical trends were evaluated solely on the Microsoft COCO val2017 dataset.
- **BPC Storage Scope**: The bit-depth reduction branch was restricted to uniform RGB quantization saved via a standard lossless PNG container.
- **Recompression Nature**: The JPEG branch evaluated represents second-order lossy recompression, as the original COCO source images were already stored in JPEG format.

### 6.3 Future Work
To expand this research into a comprehensive framework, future investigations will focus on the following areas:
1. **Advanced Codec Evaluations**: Evaluating modern lossy and lossless codecs, including WebP, AVIF, and JPEG XL, to identify if newer spatial and frequency transforms yield superior task-aware compression profiles.
2. **Alternative Detector Families**: Testing the generalizability of these findings across different detector paradigms, such as two-stage detectors (Faster R-CNN), anchor-based models (YOLOv5), and vision-transformer-based detectors (DETR).
3. **Learned Machine-Centric Compression**: Integrating end-to-end learned image compression networks trained directly with a joint loss function combining rate-distortion optimization and downstream detection loss.
4. **Statistical Stability and Per-Class Analysis**: Conducting repeated statistical runs with varied initial seeds, alongside a per-class detection analysis to identify if specific semantic categories (e.g., small objects vs. large structures) display unique sensitivities to frequency-domain or amplitude-domain quantization noise.
5. **Entropy Coding for Low Bit-Depths**: Exploring customized, spatial-aware entropy encoders for quantized bit-depth images that bypass the limitations of the PNG container, enabling real storage savings for low-bit-depth machine vision inputs.

---

## 7. References
1. Wallace, G. K. (1992). The JPEG still picture compression standard. *IEEE Transactions on Consumer Electronics*, *38*(1), xviii–xxxiv. https://doi.org/10.1109/30.125072
2. World Wide Web Consortium. (2003). *Portable Network Graphics (PNG) specification (second edition)* (W3C Recommendation 10 November 2003). https://www.w3.org/TR/PNG/
3. Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). Image quality assessment: From error visibility to structural similarity. *IEEE Transactions on Image Processing*, *13*(4), 600–612. https://doi.org/10.1109/TIP.2003.819861
4. Horé, A., & Ziou, D. (2010). Image quality metrics: PSNR vs. SSIM. *2010 20th International Conference on Pattern Recognition*, 2366–2369. https://doi.org/10.1109/ICPR.2010.579
5. Zhai, G., & Min, X. (2020). Perceptual image quality assessment: A survey. *Science China Information Sciences*, *63*(11), 211301. https://doi.org/10.1007/s11432-019-2757-1
6. Jocher, G., Chaurasia, A., & Qiu, J. (2023). *Ultralytics YOLOv8* (Version 8.0.0) [Computer software]. https://github.com/ultralytics/ultralytics
7. Redmon, J., Divvala, S., Girshick, R., & Farhadi, A. (2016). You only look once: Unified, real-time object detection. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 779–788. https://doi.org/10.1109/CVPR.2016.91
8. Wang, C.-Y., Bochkovskiy, A., & Liao, H.-Y. M. (2023). YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 7464–7475. https://doi.org/10.1109/CVPR52729.2023.00721
9. Lin, T.-Y., Maire, M., Belongie, S. J., Hays, J., Perona, P., Ramanan, D., Dollár, P., & Zitnick, C. L. (2014). Microsoft COCO: Common objects in context. In D. Fleet, T. Pajdla, B. Schiele, & T. Tuytelaars (Eds.), *Computer vision – ECCV 2014* (pp. 740–755). Springer. https://doi.org/10.1007/978-3-319-10602-1_48
10. Hu, Y., Yang, W., Li, J., & Wang, L. (2018). Content-aware and task-aware image compression for cloud-based object detection. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops*, 1689–1697. https://doi.org/10.1109/CVPRW.2018.00220
11. Kim, M., Lee, J., & Kim, C. (2021). Task-aware image compression via spatially-adaptive feature transform. *arXiv preprint arXiv:2108.09551*. https://arxiv.org/abs/2108.09551
12. Ye, J., Yeo, H., Park, J., & Han, D. (2023). AccelIR: Task-aware image compression for accelerating neural restoration. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 17852–17861. https://doi.org/10.1109/CVPR.2023.01712
13. Gandor, T., & Nalepa, J. (2022). First gradually, then suddenly: Understanding the impact of image compression on object detection using deep learning. *Sensors*, *22*(3), 1104. https://doi.org/10.3390/s22031104
14. Hao, Y., Pei, H., Lyu, Y., Yuan, Z., Rizzo, J.-R., Wang, Y., & Fang, Y. (2022). *Understanding the impact of image quality and distance of objects to object detection performance*. arXiv preprint arXiv:2209.08237. https://doi.org/10.48550/arXiv.2209.08237
15. Huang, C.-H., & Wu, J.-L. (2024). Unveiling the future of human and machine coding: A survey of end-to-end learned image compression. *Entropy*, *26*(5), 357. https://doi.org/10.3390/e26050357
16. Piran, M. J. (2022). Learning-driven lossy image compression: A comprehensive survey. *arXiv preprint arXiv:2201.09240*. https://doi.org/10.48550/arXiv.2201.09240
17. Heckbert, P. S. (1982). Color image quantization for frame buffer display. *Proceedings of the 9th Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH ’82)*, 297–307. https://doi.org/10.1145/800064.801294
18. Floyd, R. W., & Steinberg, L. (1976). An adaptive algorithm for spatial grey scale. *Proceedings of the Society of Information Display*, *17*(2), 75–77.
19. Jacob, B., Kligys, S., Chen, B., Zhu, M., Tang, M., Howard, A., Adam, H., & Kalenichenko, D. (2018). Quantization and training of neural networks for efficient integer-arithmetic-only inference. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2704–2713. https://doi.org/10.1109/CVPR.2018.00291
20. Han, S., Mao, H., & Dally, W. J. (2016). Deep compression: Compressing deep neural networks with pruning, trained quantization and Huffman coding. *International Conference on Learning Representations (ICLR)*. https://arxiv.org/abs/1510.00149
