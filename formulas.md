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

The Qanadli score measures pulmonary embolism severity by summing weighted obstruction degrees and normalizing by the maximum possible.

### Steps

1. **Tree Traversal**  
   - Start at the root of the arterial tree.  
   - For each **proximal** artery (mediastinal or lobar):  
     - If obstruction `o > T_min`, add to set S and **do not** traverse its children.  
     - Otherwise, continue down its children.  
   - For each **segmental** artery not already covered by a proximal parent, add to S.

2. **Weight & Degree Assignment**  
   For each artery s in S:  
   - **Weight** wₛ:  
     - = 1 for a segmental artery  
     - = number of downstream segmental arteries for a proximal artery  
   - **Obstruction Degree** d′ₛ (based on raw obstruction oₛ):  
     ```
     if oₛ < T_min then d′ₛ = 0
     else if oₛ < T_max then d′ₛ = 1
     else                 d′ₛ = 2
     ```

3. **Score Calculation**  
   ```
   numerator   = sum over s in S of (wₛ × d′ₛ)
   denominator = 2 × sum over s in S of wₛ
   Qanadli Score = numerator / denominator
    ```
