# data/

This folder stores the collected RGB training dataset.

## data.csv

Columns:

| Column      | Description                                         |
|-------------|------------------------------------------------------|
| R           | Red channel value (0–255)                             |
| G           | Green channel value (0–255)                           |
| B           | Blue channel value (0–255)                             |
| Material    | Label assigned to the sample (e.g. PET, HDPE, Unlabeled) |
| timestamp   | When the reading was recorded                         |

A small seed dataset (6 example rows for PET and HDPE) is included so
`train.py` has something to train on immediately after cloning the
repository. Replace or extend it with your own measurements using:

- The web dashboard's **Save Sample** button, or
- `python collect.py <MATERIAL> --count 10`

## Training vs. unknown/experimental data

Rows saved with a real label (e.g. `PET`, `HDPE`) are treated as training
data. Rows saved as `Unlabeled` (the default when no label is entered on
the dashboard) are **not** used for training until they are manually
reviewed and relabeled — see Section 20/22 of the project documentation
for why unverified readings should not be trusted as ground truth.
