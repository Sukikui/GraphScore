# Scoring Formulas

These scores are a measure of pulmonary embolism severity based on arterial obstruction.

## Mastora Score

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

### Algorithm

1. **Traverse arterial tree**  
Perform a depth-first search starting from the root of the directed graph.

2. **Classify each segment**  
Determine artery type via `get_arterie_type(edge_attrs)`:  
- **mediastinal** (level 1 & 2)  
- **lobar** (level 3)  
- **segmental** (level 4)  

3. **Filter by obstruction thresholds**  
- **Mediastinal/lobar**: include if obstruction > `min_obstruction_thresh`  
- **Segmental**: always include  
- Recurse into unaffected mediastinal/lobar to capture downstream segmental branches.

4. **Assign weights**  
- **Mediastinal/lobar**: weight = number of downstream subsegments (`get_subsegments_below`)  
- **Segmental**: weight = 1

5. **Map obstruction to degree**  
For each obstruction value $o_i$:  
```text
d_i = 0, if o_i < min_obstruction_thresh  
d_i = 1, if min_obstruction_thresh ≤ o_i < max_obstruction_thresh  
d_i = 2, if o_i ≥ max_obstruction_thresh
```

6. **Compute final score**
7. 
$$ \text{Qanadli Score} = \frac{\sum_{i \in A} w_i \cdot d_i}{2 \sum_{i \in A} w_i} \in [0,1] $$
