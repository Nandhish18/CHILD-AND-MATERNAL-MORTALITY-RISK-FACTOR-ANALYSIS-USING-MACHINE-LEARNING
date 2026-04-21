import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from preprocessing import preprocess_pipeline


def train_models():

    # Load preprocessed data
    X_train, X_test, y_train, y_test = preprocess_pipeline()

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Support Vector Machine": SVC(probability=True),
        "Neural Network (MLP)": MLPClassifier(max_iter=1000),
        "Random Forest": RandomForestClassifier()
    }

    results = {}
    best_model = None
    best_accuracy = 0

    for name, model in models.items():

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        results[name] = {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": confusion_matrix(y_test, y_pred)
        }

        # Save best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model

    # Save best model
    joblib.dump(best_model, "best_model.pkl")

    return results


# --------------------------------------
# Confusion Matrix Plot
# --------------------------------------
def plot_confusion_matrix(cm, model_name):

    plt.figure()
    sns.heatmap(cm, annot=True, fmt='d')
    plt.title(f"{model_name} - Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.savefig(f"static/{model_name}_cm.png")
    plt.close()


# --------------------------------------
# Feature Importance (Random Forest)
# --------------------------------------
def get_feature_importance():

    model = joblib.load("best_model.pkl")

    if hasattr(model, "feature_importances_"):
        return model.feature_importances_
    else:
        return None
