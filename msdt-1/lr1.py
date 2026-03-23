"""
Глава 3. Вычислительный эксперимент: динамическая оценка рейтинга источников
сообщений в социальных коммуникациях.

Реализация четырёх сценариев из главы 2:
  1. Базовый сценарий
  2. Разреженные оценки
  3. Координированная группа
  4. Скачкообразное изменение структуры

Для каждого сценария вычисляются:
  - Траектория рейтингов W(t) для каждого источника
  - Суммарная доля рейтинга группы S_C(t)
  - Норма изменения рейтинга Δ(t)
"""
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

matplotlib.use("Agg")

# ─── Воспроизводимость ───
np.random.seed(42)

# ─── Параметры эксперимента ───
N = 10           # число источников
T = 100          # число временных шагов
N_ITER = 300     # макс. итераций степенного метода
TOL = 1e-10      # порог сходимости степенного метода
ALPHA = 0.3      # параметр сглаживания (формула 6)

# Базовые характеристики источников q_i (различная «привлекательность»)
Q = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25])

# Координированная группа — источники 0, 1, 2
C = [0, 1, 2]
BETA = 2.0       # параметр усиления внутри группы
SPARSITY = 0.4   # вероятность наличия связи (сценарий 2)
T0 = 50          # момент структурного перелома (сценарий 4)
NOISE_STD = 0.15 # σ шума

def generate_Y(t, scenario):
    Y = np.zeros((N, N))
    eps = np.random.normal(0, NOISE_STD, (N, N))

    for i in range(N):
        for j in range(N):
            if i == j:
                continue  # источник не оценивает сам себя

            base = Q[i] + eps[i, j]

            if scenario == "base":
                # Формула (7): Y_ij = max(q_i + ε, 0)
                Y[i, j] = max(base, 0)

            elif scenario == "sparse":
                # Формула (8): Y_ij = a_ij * max(q_i + ε, 0)
                a = 1 if np.random.rand() < SPARSITY else 0
                Y[i, j] = a * max(base, 0)

            elif scenario == "group":
                # Формула (9): + β * 𝟙{i∈C, j∈C}
                bonus = BETA if (i in C and j in C) else 0
                Y[i, j] = max(base, 0) + bonus

            elif scenario == "jump":
                # Формула (10): + β * 𝟙{t≥t₀, i∈C, j∈C}
                bonus = BETA if (t >= T0 and i in C and j in C) else 0
                Y[i, j] = max(base, 0) + bonus

    return Y

def normalize_columns(Y):
    X = Y.copy()
    col_sums = X.sum(axis=0)
    for j in range(N):
        if col_sums[j] > 0:
            X[:, j] /= col_sums[j]
        else:
            X[:, j] = 1.0 / N
    return X

def power_iteration(X, w_init=None):
    if w_init is not None:
        w = w_init.copy()
    else:
        w = np.ones(N) / N

    for _ in range(N_ITER):
        w_new = X @ w
        norm = np.sum(np.abs(w_new))
        if norm > 0:
            w_new /= norm
        if np.sum(np.abs(w_new - w)) < TOL:
            break
        w = w_new
    return w_new

def run_scenario(scenario):
    W_history = np.zeros((T, N))
    W_smooth_history = np.zeros((T, N))
    S_C_history = np.zeros(T)
    Delta_history = np.zeros(T)

    w_prev = np.ones(N) / N
    w_smooth_prev = None

    for t in range(T):
        Y = generate_Y(t, scenario)
        X = normalize_columns(Y)
        w = power_iteration(X, w_init=w_prev)

        # Сглаживание: формула (6)
        if w_smooth_prev is None:
            w_smooth = w.copy()
        else:
            w_smooth = (1 - ALPHA) * w + ALPHA * w_smooth_prev

        # Показатели
        S_C = np.sum(w[C])                           # формула (13)
        Delta = np.sum(np.abs(w - w_prev)) if t > 0 else 0  # формула (14)

        W_history[t] = w
        W_smooth_history[t] = w_smooth
        S_C_history[t] = S_C
        Delta_history[t] = Delta

        w_prev = w
        w_smooth_prev = w_smooth

    return W_history, W_smooth_history, S_C_history, Delta_history


scenarios = {
    "base":   "Базовый сценарий",
    "sparse": "Разреженные оценки",
    "group":  "Координированная группа",
    "jump":   "Скачкообразное изменение",
}

results = {}
for key in scenarios:
    np.random.seed(42)  # одинаковый seed для сопоставимости
    results[key] = run_scenario(key)
    print(f"[OK] {scenarios[key]}")


plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 8.5,
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "font.family": "DejaVu Sans",
})

colors_group = ["#d62728", "#e377c2", "#ff7f0e"]  # источники из C
colors_other = ["#1f77b4", "#2ca02c", "#9467bd", "#8c564b",
                "#17becf", "#bcbd22", "#7f7f7f"]    # остальные

def source_color(i):
    if i in C:
        return colors_group[C.index(i)]
    return colors_other[i - len(C)]

def source_label(i):
    tag = " (C)" if i in C else ""
    return f"Источник {i+1}{tag}"


output_dir = "."
os.makedirs(output_dir, exist_ok=True)


# ── 1. Общая сводная фигура (4 сценария × 3 графика) ──

fig, axes = plt.subplots(4, 3, figsize=(16, 18))
fig.suptitle("Результаты вычислительного эксперимента", fontsize=16, y=0.995)

for row, key in enumerate(scenarios):
    W_hist, W_sm, S_C, Delta = results[key]
    ts = np.arange(T)

    # Столбец 1: Траектория рейтингов W(t)
    ax = axes[row, 0]
    for i in range(N):
        lw = 1.8 if i in C else 0.9
        alpha = 1.0 if i in C else 0.5
        ax.plot(ts, W_hist[:, i], color=source_color(i),
                linewidth=lw, alpha=alpha, label=source_label(i))
    ax.set_ylabel("Wᵢ(t)")
    ax.set_title(f"{scenarios[key]}: траектории рейтингов")
    if row == 0:
        ax.legend(loc="upper right", ncol=2, fontsize=7)
    ax.set_xlim(0, T - 1)
    ax.grid(True, alpha=0.3)
    if key == "jump":
        ax.axvline(T0, color="gray", linestyle="--", alpha=0.7, label=f"t₀={T0}")

    # Столбец 2: Доля рейтинга группы S_C(t)
    ax = axes[row, 1]
    ax.plot(ts, S_C, color="#d62728", linewidth=1.5, label="S_C(t)")
    # Ожидаемая доля при равномерном рейтинге
    fair_share = len(C) / N
    ax.axhline(fair_share, color="gray", linestyle="--", alpha=0.6,
               label=f"Равномерная доля ({fair_share:.1f})")
    ax.set_ylabel("S_C(t)")
    ax.set_title(f"{scenarios[key]}: доля группы C")
    ax.legend(fontsize=8)
    ax.set_xlim(0, T - 1)
    ax.grid(True, alpha=0.3)
    if key == "jump":
        ax.axvline(T0, color="gray", linestyle="--", alpha=0.7)

    # Столбец 3: Изменение рейтинга Δ(t)
    ax = axes[row, 2]
    ax.plot(ts[1:], Delta[1:], color="#2ca02c", linewidth=1.0)
    ax.set_ylabel("Δ(t)")
    ax.set_title(f"{scenarios[key]}: подвижность рейтинга")
    ax.set_xlim(0, T - 1)
    ax.grid(True, alpha=0.3)
    if key == "jump":
        ax.axvline(T0, color="gray", linestyle="--", alpha=0.7)

    if row == 3:
        for c in range(3):
            axes[row, c].set_xlabel("t (временной шаг)")

plt.tight_layout()
plt.savefig(f"{output_dir}/all_scenarios_overview.png", bbox_inches="tight")
plt.close()
print("[OK] Сводная фигура")


# ── 2. Отдельные детальные фигуры для каждого сценария ──

for key in scenarios:
    W_hist, W_sm, S_C, Delta = results[key]
    ts = np.arange(T)

    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    fig.suptitle(f"{scenarios[key]}", fontsize=15, y=1.01)

    # (a) Траектории рейтингов
    ax1 = fig.add_subplot(gs[0, 0])
    for i in range(N):
        lw = 2.0 if i in C else 0.8
        alpha = 1.0 if i in C else 0.45
        ax1.plot(ts, W_hist[:, i], color=source_color(i),
                 linewidth=lw, alpha=alpha, label=source_label(i))
    ax1.set_xlabel("t")
    ax1.set_ylabel("Wᵢ(t)")
    ax1.set_title("(а) Траектории рейтингов")
    ax1.legend(loc="upper right", ncol=2, fontsize=7)
    ax1.grid(True, alpha=0.3)
    if key == "jump":
        ax1.axvline(T0, color="gray", linestyle="--", alpha=0.7)

    # (b) Сглаженные траектории
    ax2 = fig.add_subplot(gs[0, 1])
    for i in range(N):
        lw = 2.0 if i in C else 0.8
        alpha = 1.0 if i in C else 0.45
        ax2.plot(ts, W_sm[:, i], color=source_color(i),
                 linewidth=lw, alpha=alpha, label=source_label(i))
    ax2.set_xlabel("t")
    ax2.set_ylabel("W̃ᵢ(t)")
    ax2.set_title(f"(б) Сглаженные траектории (α={ALPHA})")
    ax2.grid(True, alpha=0.3)
    if key == "jump":
        ax2.axvline(T0, color="gray", linestyle="--", alpha=0.7)

    # (c) Доля группы S_C(t)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(ts, S_C, color="#d62728", linewidth=1.5)
    fair_share = len(C) / N
    ax3.axhline(fair_share, color="gray", linestyle="--", alpha=0.6,
                label=f"Равномерная доля = {fair_share:.2f}")
    # Показать «справедливую» долю на основе q
    expected_share = np.sum(Q[C]) / np.sum(Q)
    ax3.axhline(expected_share, color="#ff7f0e", linestyle=":",
                alpha=0.6, label=f"Доля по qᵢ = {expected_share:.2f}")
    ax3.set_xlabel("t")
    ax3.set_ylabel("S_C(t)")
    ax3.set_title("(в) Суммарная доля группы C")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    if key == "jump":
        ax3.axvline(T0, color="gray", linestyle="--", alpha=0.7)

    # (d) Δ(t) + гистограмма
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(ts[1:], Delta[1:], color="#2ca02c", linewidth=1.0, alpha=0.8)
    ax4.set_xlabel("t")
    ax4.set_ylabel("Δ(t)")
    mean_delta = np.mean(Delta[1:])
    ax4.axhline(mean_delta, color="#2ca02c", linestyle="--", alpha=0.5,
                label=f"Среднее Δ = {mean_delta:.4f}")
    ax4.set_title("(г) Подвижность рейтинга Δ(t)")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    if key == "jump":
        ax4.axvline(T0, color="gray", linestyle="--", alpha=0.7)

    plt.savefig(f"{output_dir}/scenario_{key}.png", bbox_inches="tight")
    plt.close()
    print(f"[OK] Детальная фигура: {scenarios[key]}")


# ── 3. Сравнительная фигура: S_C(t) по всем сценариям ──

fig, ax = plt.subplots(figsize=(10, 5))
style_map = {
    "base":   {"color": "#1f77b4", "ls": "-",  "label": "Базовый"},
    "sparse": {"color": "#ff7f0e", "ls": "--", "label": "Разреженный"},
    "group":  {"color": "#d62728", "ls": "-.",  "label": "Группа (постоянно)"},
    "jump":   {"color": "#9467bd", "ls": ":",   "label": "Группа (с t₀=50)"},
}
for key in scenarios:
    S_C = results[key][2]
    s = style_map[key]
    ax.plot(np.arange(T), S_C, color=s["color"], linestyle=s["ls"],
            linewidth=1.8, label=s["label"])

fair_share = len(C) / N
ax.axhline(fair_share, color="gray", linestyle="--", alpha=0.5,
           label=f"Равномерная доля = {fair_share:.2f}")
ax.axvline(T0, color="gray", linestyle=":", alpha=0.4)
ax.set_xlabel("t (временной шаг)")
ax.set_ylabel("S_C(t)")
ax.set_title("Сравнение доли группы C по всем сценариям")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/comparison_S_C.png", bbox_inches="tight")
plt.close()
print("[OK] Сравнительная фигура S_C")


# ── 4. Сравнительная фигура: Δ(t) по всем сценариям ──

fig, ax = plt.subplots(figsize=(10, 5))
for key in scenarios:
    Delta = results[key][3]
    s = style_map[key]
    ax.plot(np.arange(1, T), Delta[1:], color=s["color"], linestyle=s["ls"],
            linewidth=1.2, alpha=0.85, label=s["label"])

ax.axvline(T0, color="gray", linestyle=":", alpha=0.4)
ax.set_xlabel("t (временной шаг)")
ax.set_ylabel("Δ(t)")
ax.set_title("Сравнение подвижности рейтинга Δ(t) по всем сценариям")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/comparison_Delta.png", bbox_inches="tight")
plt.close()
print("[OK] Сравнительная фигура Δ")


# ── 5. Средние рейтинги: столбчатая диаграмма ──

fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), sharey=True)
for idx, key in enumerate(scenarios):
    W_hist = results[key][0]
    mean_w = np.mean(W_hist, axis=0)
    colors = [source_color(i) for i in range(N)]
    labels = [f"S{i+1}" for i in range(N)]
    bars = axes[idx].bar(labels, mean_w, color=colors, edgecolor="white", linewidth=0.5)
    axes[idx].set_title(scenarios[key], fontsize=10)
    axes[idx].set_xlabel("Источник")
    if idx == 0:
        axes[idx].set_ylabel("Средний Wᵢ")
    axes[idx].grid(True, axis="y", alpha=0.3)

plt.suptitle("Средний рейтинг источников по сценариям", fontsize=13)
plt.tight_layout()
plt.savefig(f"{output_dir}/mean_ratings_bar.png", bbox_inches="tight")
plt.close()
print("[OK] Столбчатая диаграмма средних рейтингов")


# ── 6. Числовые итоги ──

print("\n" + "=" * 70)
print("ЧИСЛОВЫЕ ИТОГИ ВЫЧИСЛИТЕЛЬНОГО ЭКСПЕРИМЕНТА")
print("=" * 70)

for key in scenarios:
    W_hist, W_sm, S_C, Delta = results[key]
    mean_w = np.mean(W_hist, axis=0)
    print(f"\n--- {scenarios[key]} ---")
    print(f"  Средний рейтинг источников:")
    for i in range(N):
        tag = " *" if i in C else ""
        print(f"    Источник {i+1:2d}: {mean_w[i]:.4f}{tag}")
    print(f"  Средняя доля группы C:  S_C = {np.mean(S_C):.4f}")
    print(f"  Средняя подвижность:    Δ   = {np.mean(Delta[1:]):.4f}")
    print(f"  Макс. подвижность:      Δ   = {np.max(Delta[1:]):.4f}")

    if key == "jump":
        print(f"  S_C до скачка (t<{T0}):  {np.mean(S_C[:T0]):.4f}")
        print(f"  S_C после скачка (t≥{T0}): {np.mean(S_C[T0:]):.4f}")

print(f"\nПараметры: N={N}, T={T}, |C|={len(C)}, β={BETA}, "
      f"sparsity={SPARSITY}, α={ALPHA}, σ_noise={NOISE_STD}")
print(f"Графики сохранены в {output_dir}/")
