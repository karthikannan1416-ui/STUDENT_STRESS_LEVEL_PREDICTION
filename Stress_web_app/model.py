import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset (USE FULL PATH if needed)
df = pd.read_csv(r"C:\Users\sanja\Downloads\student_lifestyle_dataset.csv")

# Encode target (Low, Moderate, High → 0,1,2)
le = LabelEncoder()
df['Stress Level'] = le.fit_transform(df['Stress Level'])

# Features and target
X = df[['Sleep Hours','Study Hours','Mobile Usage','Exercise','Relaxation']]
y = df['Stress Level']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ RANDOM FOREST MODEL
model = RandomForestClassifier(
    n_estimators=100,   # number of trees
    max_depth=None,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Accuracy (for your review)
accuracy = model.score(X_test, y_test)
print("Random Forest Accuracy:", accuracy)

# Save model
pickle.dump(model, open("model.pkl", "wb"))

print("model.pkl created successfully!")