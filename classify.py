"""
Lyciasalamandra Species Classification via Electronic Nose
==========================================================
Discriminates between two endangered endemic salamander species
(L. flavimembris and L. fazilae) using pheromone odor data
collected with a DiagNose 2 electronic nose system.

Original study: MEF Research Competition 2023 — 1st Place in Turkey (Biology)
Presented at: European Herpetological Congress
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix
)

# ── 1. LOAD DATA ─────────────────────────────────────────────────────────────

df = pd.read_csv("data/Semender.csv")

# Features: 12 sensor area values (computed via Trapezoidal Rule in original study)
# Target: species label  D = L. fazilae (Göcek)  |  M = L. flavimembris (Marmaris)
X = df.drop(columns=["Örnek NO", "TÜR"])
y = df["TÜR"]

print("=" * 60)
print("Dataset")
print("=" * 60)
print(f"Total specimens : {len(df)}")
print(f"  L. fazilae    (D): {(y == 'D').sum()}")
print(f"  L. flavimembris (M): {(y == 'M').sum()}")
print(f"Features        : {X.shape[1]} sensors")
print()

# ── 2. TRAIN / TEST SPLIT ────────────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=1
)

# ── 3. DEFINE MODELS ─────────────────────────────────────────────────────────

models = {
    "Artificial Neural Network (MLP)": MLPClassifier(
        solver="lbfgs",
        alpha=0.0001,
        hidden_layer_sizes=(4,),   # single hidden layer, 4 neurons
        random_state=1,
        max_iter=1000,
    ),
    "Decision Tree": DecisionTreeClassifier(
        criterion="entropy",
        min_samples_split=2,
        splitter="best",
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
    ),
    "Support Vector Machine": SVC(
        C=1.0,
        kernel="rbf",
        gamma="scale",
        decision_function_shape="ovr",
        break_ties=False,
        random_state=None,
    ),
}

# ── 4. TRAIN & EVALUATE ──────────────────────────────────────────────────────

results = {}

print("=" * 60)
print("Model Results")
print("=" * 60)

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds) * 100
    results[name] = {"accuracy": acc, "predictions": preds, "model": model}
    print(f"\n{name}")
    print(f"  Accuracy : %{acc:.2f}")
    print(f"  Classification Report:")
    report = classification_report(y_test, preds, target_names=["L. fazilae (D)", "L. flavimembris (M)"])
    print("    " + report.replace("\n", "\n    "))

# ── 5. SUMMARY TABLE ─────────────────────────────────────────────────────────

print("=" * 60)
print("Summary")
print("=" * 60)
summary = pd.DataFrame(
    [(name, f"%{v['accuracy']:.2f}") for name, v in results.items()],
    columns=["Model", "Accuracy"]
).sort_values("Accuracy", ascending=False)
print(summary.to_string(index=False))
print()

# ── 6. VISUALIZATIONS ────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle(
    "Lyciasalamandra Species Classification via Electronic Nose",
    fontsize=14, fontweight="bold"
)

# 6a. Accuracy bar chart
ax = axes[0, 0]
names = [n.replace(" (MLP)", "").replace(" ", "\n") for n in results.keys()]
accs = [v["accuracy"] for v in results.values()]
colors = ["#2ecc71" if a == max(accs) else "#3498db" for a in accs]
bars = ax.bar(names, accs, color=colors, edgecolor="white", linewidth=1.5)
ax.set_ylim(0, 100)
ax.set_ylabel("Accuracy (%)")
ax.set_title("Model Comparison")
ax.axhline(60, color="red", linestyle="--", linewidth=1, label="60% threshold")
ax.legend(fontsize=8)
for bar, acc in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"%{acc:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

# 6b–6e. Confusion matrices
cm_axes = [axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1]]
for ax, (name, v) in zip(cm_axes, results.items()):
    cm = confusion_matrix(y_test, v["predictions"], labels=["D", "M"])
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["L. fazilae", "L. flavimembris"],
                yticklabels=["L. fazilae", "L. flavimembris"],
                cbar=False)
    short_name = name.replace("Artificial Neural Network (MLP)", "ANN")\
                     .replace("Support Vector Machine", "SVM")
    ax.set_title(f"{short_name}  (%{v['accuracy']:.1f})", fontsize=10)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

# 6f. Sensor value distributions by species
ax = axes[1, 2]
sensor_means = df.groupby("TÜR")[X.columns].mean().T
sensor_means.columns = ["L. fazilae (D)", "L. flavimembris (M)"]
sensor_means.plot(kind="bar", ax=ax, color=["#e74c3c", "#3498db"],
                  edgecolor="white", linewidth=0.5)
ax.set_title("Mean Sensor Response by Species")
ax.set_xlabel("Sensor")
ax.set_ylabel("Mean Area Value")
ax.tick_params(axis="x", rotation=45)
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("results/classification_results.png", dpi=150, bbox_inches="tight")
print("Figure saved → results/classification_results.png")
plt.show()
