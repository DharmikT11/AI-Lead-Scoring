import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import os

# Load the dataset
df = pd.read_csv('data/leads.csv')

# Define usable columns only (confirmed from your dataset)
features = ['credit_score', 'age_group', 'family_background', 'income']
target = 'intent'

# Select features + target
df_encoded = df[features + [target]].copy()

# Label encode categorical fields
label_encoders = {}
for col in ['age_group', 'family_background']:
    le = LabelEncoder()
    df_encoded[col] = le.fit_transform(df_encoded[col])
    label_encoders[col] = le

# Prepare data
X = df_encoded[features]
y = df_encoded[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model trained with accuracy: {acc:.2f}")

# Save model and encoders
os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/model.pkl')
joblib.dump(label_encoders, 'model/encoders.pkl')
print("✅ Model and encoders saved.")
