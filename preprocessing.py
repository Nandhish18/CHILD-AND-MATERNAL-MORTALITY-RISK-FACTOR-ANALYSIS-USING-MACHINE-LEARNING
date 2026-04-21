import pandas as pd
import numpy as np
import sqlite3

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE


DATABASE = "maternal_child.db"


# --------------------------------------
# LOAD DATA FROM SQLITE
# --------------------------------------
def load_data_from_db():
    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT p.age, p.location, p.education,
           m.bmi as maternal_bmi,
           m.anemia_status,
           m.diabetes,
           m.hypertension,
           m.pregnancy_complications,
           m.income,
           m.sanitation,
           c.immunization_status,
           c.bmi as child_bmi,
           c.infection_history,
           c.growth_indicator
    FROM patients p
    JOIN maternal_data m ON p.id = m.patient_id
    JOIN child_data c ON p.id = c.patient_id
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


# --------------------------------------
# HANDLE MISSING VALUES
# --------------------------------------
def handle_missing_values(df):

    # Numeric columns → fill with mean
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Categorical columns → fill with mode
    categorical_cols = df.select_dtypes(include='object').columns
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df


# --------------------------------------
# ENCODING
# --------------------------------------
def encode_categorical(df):

    label_encoders = {}
    categorical_cols = df.select_dtypes(include='object').columns

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    return df, label_encoders


# --------------------------------------
# FEATURE SCALING
# --------------------------------------
def scale_features(X):

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler


# --------------------------------------
# APPLY SMOTE
# --------------------------------------
def apply_smote(X, y):

    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    return X_resampled, y_resampled


# --------------------------------------
# COMPLETE PREPROCESSING PIPELINE
# --------------------------------------
def preprocess_pipeline(target_column="growth_indicator"):

    # Load data
    df = load_data_from_db()

    # Handle missing values
    df = handle_missing_values(df)

    # Encoding
    df, encoders = encode_categorical(df)

    # Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Scaling
    X_scaled, scaler = scale_features(X)

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Apply SMOTE (only on training data)
    X_train_resampled, y_train_resampled = apply_smote(X_train, y_train)

    print("Original Training Samples:", len(y_train))
    print("After SMOTE Samples:", len(y_train_resampled))

    return X_train_resampled, X_test, y_train_resampled, y_test


# --------------------------------------
# RUN TEST
# --------------------------------------
if __name__ == "__main__":
    X_train, X_test, y_train, y_test = preprocess_pipeline()
    print("Preprocessing Completed Successfully!")
