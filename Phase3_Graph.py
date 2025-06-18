import matplotlib.pyplot as plt
import numpy as np

# ✅ Strict Replacement: Import cleaned clause data
from Clauses_Clean import compliant_clauses, non_compliant_clauses

#print(compliant_clauses, non_compliant_clauses)

frameworks = list(compliant_clauses.keys())
num_vars = len(frameworks)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # to close the loop

def plot_radar(ax, data, title, color):
    labels = list(data.keys())
    values = [len(clauses) for clauses in data.values()]
    values += values[:1]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=11)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.fill(angles, values, color=color, alpha=0.25)

    # Add upright clause names
    for i, (framework, clauses) in enumerate(data.items()):
        angle = angles[i]
        for j, clause in enumerate(clauses):
            radius = j + 1
            ax.text(angle, radius, clause, ha='center', va='bottom', fontsize=8, rotation=0)

    ax.set_title(title, size=14, pad=15)
    ax.set_rlabel_position(30)
    ax.set_rticks(range(1, max(values)))
    ax.set_ylim(0, max(values))

    # Force render to access tick labels
    plt.draw()

    # Rotate and recolor radial (y-axis) tick labels
    tick_labels = ax.get_yticklabels()
    for label in tick_labels:
        label.set_rotation(30)
        label.set_color('blue')
        label.set_fontsize(10)
        label.set_verticalalignment('bottom')
        label.set_horizontalalignment('left')  


# === PLOT BOTH CHARTS ===
fig, axs = plt.subplots(1, 2, figsize=(20, 10), subplot_kw=dict(polar=True))

plot_radar(axs[0], compliant_clauses, "Compliant Clauses per Framework", "green")
plot_radar(axs[1], non_compliant_clauses, "Non-Compliant Clauses per Framework", "red")

plt.tight_layout()

# ✅ Save to PNG before showing
plt.savefig("Compliance_Radar_Charts.png", dpi=300)

plt.show()