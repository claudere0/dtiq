# Response to Reviewers

**Manuscript ID:** ID1139  
**Title:** TASK-AWARE EVALUATION OF JPEG RECOMPRESSION AND RGB BIT-DEPTH REDUCTION FOR OBJECT DETECTION  

Dear Reviewers,

We would like to thank you for your thorough and constructive feedback. Your comments have significantly improved the quality and clarity of our manuscript. Below, we provide a point-by-point response to your suggestions, detailing the exact modifications made to the text, methodology, and figures.

---

### **Point 1: Softening the Main Conclusion on JPEG**
**Response:** We completely agree with this assessment. We have revised the Abstract, Discussion, and Conclusion to explicitly clarify that JPEG's superiority in our tests applies specifically to a direct comparison with uniform RGB bit-depth reduction when stored in a standard 24-bit lossless PNG container. We have also added a dedicated paragraph acknowledging that different storage methodologies (e.g., indexed PNGs with palettes or direct packed bitstreams) could theoretically mitigate the container overhead observed in our experiments.

### **Point 2: Adding Additional Detectors**
**Response:** This was an excellent suggestion. To demonstrate the generalizability of our findings, we have substantially expanded the scope of the paper by conducting full evaluations on two additional, heavier architectures: **YOLOv8m** (a medium-weight CNN) and **RT-DETR-L** (a state-of-the-art Transformer-based detector). 
- We updated the "Methods and Materials" section to outline the inclusion of these models.
- The "Results" section has been entirely rewritten to include tables for all three architectures.
- We have introduced a new $2 \times 2$ grid figure that demonstrates the consistent mAP50 vs. dataset size degradation curves across all three models, confirming that our initial observations hold true regardless of the underlying network architecture.

### **Point 3: Modern Compression Formats**
**Response:** We have updated the Introduction to explicitly address this limitation. We clarify that the primary objective of this study was to establish a fundamental baseline using legacy storage formats (JPEG and PNG) because they currently dominate global edge-AI and surveillance pipelines. We explicitly mention that evaluating modern codecs (WebP, AVIF, JPEG XL) requires highly specialized encoder configurations, making it a critical avenue reserved for future work.

### **Point 4: Statistical Stability and Object Sizes**
**Response:** To address the stability and source of degradation, we re-ran all experiments and implemented a detailed breakdown by object size. 
- The new Results tables now include $\text{mAP}_S$ (Small), $\text{mAP}_M$ (Medium), and $\text{mAP}_L$ (Large).
- The text now analyzes how small objects are significantly more vulnerable to both JPEG artifacts and severe BPC quantization, providing exactly the granular insight requested into where the detection pipeline fails.

### **Point 5: Literature Review Table**
**Response:** We have inserted a new structured table (Table I) into the "Literature Review" section. This table compares key recent studies (e.g., Gandor & Nalepa, Hao et al., Ye et al.) by dataset, detector, compression type, and key findings. This modification firmly contextualizes our contribution within the broader landscape of "Compression for Machines."

### **Point 6: Academic Style and Figure Quality**
**Response:** We have completed a full proofreading pass to enforce a strict, formal academic tone and eliminated the technical hyphens previously present in the manuscript. 
Furthermore, we have completely overhauled the visualizations:
- We increased the global font sizes for all matplotlib-generated figures (axes labels, titles, and legends).
- The primary comparison plot was redesigned into a cleaner $2 \times 2$ grid layout to prevent visual clutter while elegantly displaying the data from all three neural network architectures.

---

We believe these revisions directly address all your concerns and have greatly strengthened the manuscript. Thank you once again for your valuable time and insight.
