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

The Qanadli score assesses pulmonary embolism severity by assigning weights to obstructed arteries.

### Algorithm

1.  **Graph Traversal**: The arterial tree is traversed from the root to identify the set of arteries, $S$, to be included in the score. The traversal logic is as follows:
    *   For proximal (mediastinal, lobar) arteries: If an artery's obstruction value is above a minimum threshold (`--min-obstruction-thresh`), it is added to the set $S$, and the traversal along that path stops.
    *   For distal (segmental) arteries: All segmental arteries that are not downstream of an already-included proximal artery are added to the set $S$.

2.  **Assign Weights and Degrees**: For each artery $s \in S$:
    *   A **weight**, $w_s$, is assigned.
        *   $w_s = 1$ for a segmental artery.
        *   $w_s = \text{number of downstream segmental arteries}$ for a proximal artery.
    *   An **obstruction degree**, $d'_s$, is determined from the raw obstruction value $o_s$ based on two thresholds, $T_{min}$ (`--min-obstruction-thresh`) and $T_{max}$ (`--max-obstruction-thresh`):
        $ d'_s = \left\{        \begin{array}{ll}            0 & \text{if } o_s < T_{min} \\            1 & \text{if } T_{min} \le o_s < T_{max} \\            2 & \text{if } o_s \ge T_{max}        \end{array}    \right. $

3.  **Calculate Score**: The final score is the sum of the weighted degrees, normalized by the maximum possible score.

$$ \text{Qanadli Score} = \frac{\sum_{s \in S} w_s \cdot d'_s}{2 \sum_{s \in S} w_s} $$

The denominator represents the maximum possible weighted score, as the maximum value for any $d'_s$ is 2.
