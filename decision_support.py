import shap
import joblib
import numpy as np
import matplotlib.pyplot as plt
import os

# Load model
model = joblib.load("best_model.pkl")

# Create SHAP explainer
explainer = shap.Explainer(model)


def generate_explanation(input_features, feature_names):

    # Convert to numpy
    input_array = np.array([input_features])

    # Generate SHAP values
    shap_values = explainer(input_array)

    # Create static folder if not exists
    if not os.path.exists("static"):
        os.makedirs("static")

    # Plot SHAP explanation
    shap.plots.waterfall(shap_values[0], show=False)
    plt.savefig("static/shap_explanation.png", bbox_inches='tight')
    plt.close()

    # Get top contributing features
    contributions = dict(zip(feature_names,
                             shap_values.values[0]))

    # Sort by absolute impact
    sorted_features = sorted(contributions.items(),
                             key=lambda x: abs(x[1]),
                             reverse=True)

    return sorted_features[:5]
