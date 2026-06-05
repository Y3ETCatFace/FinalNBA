import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss
from sklearn.isotonic import IsotonicRegression

# ==========================================
# 1. DATA
# ==========================================
df = pd.read_csv("training_data.csv")

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

PM_TARGET = "plus_minus"
WIN_TARGET = "outcome"

X = df.drop(columns=[PM_TARGET, WIN_TARGET]).values.astype(np.float32)
y_win = df[WIN_TARGET].values.astype(np.float32)
y_pm = df[PM_TARGET].values.astype(np.float32)

# ==========================================
# 2. SPLIT (TRAIN / CALIBRATION / TEST)
# ==========================================
X_train, X_temp, y_train_win, y_temp_win, y_train_pm, y_temp_pm = train_test_split(
    X, y_win, y_pm, test_size=0.4, random_state=42
)

X_val, X_test, y_val_win, y_test_win, y_val_pm, y_test_pm = train_test_split(
    X_temp, y_temp_win, y_temp_pm, test_size=0.5, random_state=42
)

# ==========================================
# 3. SCALING
# ==========================================
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# Tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)

y_train_win = torch.tensor(y_train_win, dtype=torch.float32).unsqueeze(1)
y_val_win = torch.tensor(y_val_win, dtype=torch.float32).unsqueeze(1)
y_test_win = torch.tensor(y_test_win, dtype=torch.float32).unsqueeze(1)

y_train_pm = torch.tensor(y_train_pm, dtype=torch.float32).unsqueeze(1)

# ==========================================
# 4. MODEL
# ==========================================
class EdgeNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()

        self.backbone = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.15),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU()
        )

        self.pm_head = nn.Linear(32, 1)
        self.win_head = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        z = self.backbone(x)
        return self.pm_head(z), self.win_head(z)

model = EdgeNet(X_train.shape[1])

# ==========================================
# 5. LOSS / OPTIMIZER
# ==========================================
mse = nn.MSELoss()
bce = nn.BCELoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=3e-4,
    weight_decay=1e-4
)

# ==========================================
# 6. TRAINING
# ==========================================
best_auc = 0

for epoch in range(200):
    model.train()

    pm_pred, win_pred = model(X_train)

    loss_pm = mse(pm_pred, y_train_pm)
    loss_win = bce(win_pred, y_train_win)

    loss = loss_win + 0.15 * loss_pm

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    # ==========================================
    # VALIDATION (RAW MODEL)
    # ==========================================
    model.eval()
    with torch.no_grad():
        _, val_probs = model(X_val)

        val_probs = val_probs.numpy().ravel()
        val_true = y_val_win.numpy().ravel()

        auc = roc_auc_score(val_true, val_probs)
        ll = log_loss(val_true, val_probs)
        brier = brier_score_loss(val_true, val_probs)

    if auc > best_auc:
        best_auc = auc

    if epoch % 10 == 0:
        print(f"[RAW] Epoch {epoch} | AUC {auc:.3f} | LogLoss {ll:.3f} | Brier {brier:.3f}")

# ==========================================
# 7. CALIBRATION (ISOTONIC REGRESSION)
# ==========================================
model.eval()
with torch.no_grad():
    _, val_probs = model(X_val)
    _, test_probs = model(X_test)

val_probs = val_probs.numpy().ravel()
val_true = y_val_win.numpy().ravel()

test_probs = test_probs.numpy().ravel()
test_true = y_test_win.numpy().ravel()

# Fit calibration model
iso = IsotonicRegression(out_of_bounds="clip")
iso.fit(val_probs, val_true)

calibrated_test_probs = iso.transform(test_probs)

# ==========================================
# 8. FINAL EVALUATION (CALIBRATED)
# ==========================================
cal_auc = roc_auc_score(test_true, calibrated_test_probs)
cal_ll = log_loss(test_true, calibrated_test_probs)
cal_brier = brier_score_loss(test_true, calibrated_test_probs)

print("\n====================================")
print("FINAL CALIBRATED RESULTS")
print("====================================")
print(f"Calibrated AUC:   {cal_auc:.3f}")
print(f"Calibrated LogLoss:{cal_ll:.3f}")
print(f"Calibrated Brier: {cal_brier:.3f}")
print("Best Raw AUC:", best_auc)