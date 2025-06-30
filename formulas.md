# Scoring Formulas

## Mastora Score

The Mastora score is a measure of pulmonary embolism severity based on arterial obstruction.

### Algorithm

1.  **Select Arteries**: Identify a set of arteries, $A$, based on their anatomical level (mediastinal, lobar, segmental).
2.  **Collect Obstructions**: For each artery $i \in A$, get its obstruction value, $o_i$, which is a float in the range $[0, 1]$.
3.  **Calculate Score**: The calculation depends on whether percentages or degrees are used. Let $N = |A|$ be the number of selected arteries.

#### Percentage-based Calculation

If using percentages directly (`--use-percentage` flag):

$$ \text{Mastora Score} = \frac{\sum_{i \in A} o_i}{N} $$

#### Degree-based Calculation

If not using percentages, each obstruction value $o_i$ is first converted to a degree $d_i$ on a scale from 1 to 5:

$$ d_i = \lfloor \frac{o_i}{0.25} \rfloor + 1 $$

The final score is the sum of these degrees normalized by the maximum possible sum of degrees ($N \times 5$):

$$ \text{Mastora Score} = \frac{\sum_{i \in A} d_i}{5N} $$

---

## Qanadli Score

The Qanadli score quantifies pulmonary embolism severity by summing weighted obstruction degrees and normalizing.

### Algorithm

1. **Select Arteries**  
   Identify the set $S$ via a root-to-leaf traversal:
   - **Proximal** (mediastinal or lobar):  
     - If $o_s > T_{\min}$, add $s$ to $S$ and stop that branch.  
     - Otherwise continue to children.  
   - **Segmental**: add every segmental artery not covered by a selected proximal.

2. **Collect Obstructions**  
   For each $s\in S$, let $o_s\in[0,1]$ be its raw obstruction.

3. **Assign Weights**  
   For each $s\in S$:  
   - $w_s = 1$ if $s$ is segmental  
   - $w_s = |\{\text{downstream segmental arteries}\}|$ if $s$ is proximal  

5. **Final Score**  
   Let $W = \sum_{s\in S}w_s$. Then  
   $$ \text{Qanadli Score} = \frac{\sum_{s\in S}w_s\,d'_s}{2\,W} \quad\in[0,1]. $$
