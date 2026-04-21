# ============================================================
# FEATURE EXPLANATION PLACEHOLDER
# ============================================================
def generate_explanation(input_features, feature_names):
    # Simple placeholder: pairs each feature name with its value
    return list(zip(feature_names, input_features))
# ============================================================
# EARLY WARNING & DECISION SUPPORT SYSTEM
# SINGLE FILE STRUCTURED VERSION (PART 1)
# ============================================================

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

app = Flask(__name__)
DATABASE = "maternal_child.db"

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # ---------------- Patients ----------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            location TEXT,
            education TEXT
        )
    ''')

    # ---------------- Maternal ----------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maternal_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            bmi REAL,
            anemia_status TEXT,
            diabetes TEXT,
            hypertension TEXT,
            pregnancy_complications TEXT,
            income TEXT,
            sanitation TEXT
        )
    ''')

    # ---------------- Child ----------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS child_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            immunization_status TEXT,
            bmi REAL,
            infection_history TEXT,
            growth_indicator TEXT
        )
    ''')

    # ---------------- Postnatal ----------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postnatal_monitoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            bleeding TEXT,
            fever REAL,
            blood_pressure TEXT,
            infection_signs TEXT,
            mental_health TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---------------- Neonatal ----------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS neonatal_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            heart_rate INTEGER,
            temperature REAL,
            respiratory_rate INTEGER,
            infection_risk TEXT,
            growth_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---------------- Alerts ----------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            alert_type TEXT,
            risk_level TEXT,
            message TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# ============================================================
# RISK CLASSIFICATION FUNCTION
# ============================================================

def classify_risk(probability):
    if probability < 0.33:
        return "Low Risk", "green"
    elif probability < 0.66:
        return "Moderate Risk", "orange"
    else:
        return "High Risk", "red"


# ============================================================
# ALERT CREATION FUNCTION
# ============================================================

def create_alert(patient_id, alert_type, risk_level, message):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO alerts (patient_id, alert_type, risk_level, message)
        VALUES (?, ?, ?, ?)
    ''', (patient_id, alert_type, risk_level, message))

    conn.commit()
    conn.close()


# ============================================================
# POSTNATAL MONITORING
# ============================================================

@app.route('/postnatal-monitoring', methods=['GET', 'POST'])
def postnatal_monitoring():

    if request.method == 'POST':

        patient_id = request.form['patient_id']
        bleeding = request.form['bleeding']
        fever = float(request.form['fever'])
        infection = request.form['infection']

        if fever > 38 or infection == "Yes" or bleeding == "Severe":
            risk = "High Risk"
            create_alert(patient_id,
                         "Postnatal Emergency",
                         risk,
                         "Immediate medical attention required.")
        elif fever > 37:
            risk = "Moderate Risk"
        else:
            risk = "Stable"

        return render_template("postnatal_result.html",
                               risk=risk)

    return render_template("postnatal_monitoring.html")


# ============================================================
# NEONATAL MONITORING
# ============================================================

@app.route('/neonatal-health', methods=['GET', 'POST'])
def neonatal_health():

    if request.method == 'POST':

        patient_id = request.form['patient_id']
        temperature = float(request.form['temperature'])
        infection_risk = request.form['infection_risk']
        growth = request.form['growth']

        if temperature > 38 or infection_risk == "High" or growth == "Underweight":
            risk = "High Risk"
            create_alert(patient_id,
                         "Neonatal Emergency",
                         risk,
                         "Critical neonatal condition detected.")
        elif infection_risk == "Moderate":
            risk = "Moderate Risk"
        else:
            risk = "Stable"

        return render_template("neonatal_result.html",
                               risk=risk)

    return render_template("neonatal_health.html")
# ============================================================
# PATIENT REGISTRATION
# ============================================================

@app.route('/patient-registration', methods=['GET', 'POST'])
def patient_registration():

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        location = request.form['location']
        education = request.form['education']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO patients (name, age, location, education)
            VALUES (?, ?, ?, ?)
        ''', (name, age, location, education))

        conn.commit()
        conn.close()

        return redirect(url_for('maternal_data_form'))

    return render_template('patient_registration.html')


# ============================================================
# MATERNAL DATA FORM
# ============================================================

@app.route('/maternal-data-form', methods=['GET', 'POST'])
def maternal_data_form():

    if request.method == 'POST':

        patient_id = request.form['patient_id']
        bmi = request.form['bmi']
        anemia = request.form['anemia']
        diabetes = request.form['diabetes']
        hypertension = request.form['hypertension']
        complications = request.form['complications']
        income = request.form['income']
        sanitation = request.form['sanitation']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO maternal_data
            (patient_id, bmi, anemia_status, diabetes,
             hypertension, pregnancy_complications,
             income, sanitation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, bmi, anemia, diabetes,
              hypertension, complications, income, sanitation))

        conn.commit()
        conn.close()

        return redirect(url_for('child_data_form'))

    return render_template('maternal_data_form.html')


# ============================================================
# CHILD DATA FORM
# ============================================================

@app.route('/child-data-form', methods=['GET', 'POST'])
def child_data_form():

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        immunization = request.form['immunization']
        bmi = request.form['bmi']
        infection = request.form['infection']
        growth = request.form['growth']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO child_data
            (patient_id, immunization_status, bmi,
             infection_history, growth_indicator)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, immunization, bmi, infection, growth))
        conn.commit()
        conn.close()

        # Attempt risk prediction after saving child data

        try:
            # You may need to adjust these values and logic to match your model's expected input
            # Dummy values for maternal features (should be fetched from DB in a real app)
            age = 30.0
            maternal_bmi = 22.0
            diabetes = 0
            hypertension = 0
            child_bmi = float(bmi)
            # Map immunization string to int
            if isinstance(immunization, str):
                if immunization.lower() == 'complete':
                    immunization_val = 1
                elif immunization.lower() == 'incomplete':
                    immunization_val = 0
                else:
                    immunization_val = 0  # default/fallback
            else:
                immunization_val = int(immunization)
            # Load model and predict
            import joblib
            import numpy as np
            model = joblib.load("best_model.pkl")
            features = np.array([[age, maternal_bmi, diabetes, hypertension, child_bmi, immunization_val]])
            probability = model.predict_proba(features)[0][1]
            risk_label, color = classify_risk(probability)
            return render_template("prediction_result.html",
                                   probability=round(probability * 100, 2),
                                   risk=risk_label,
                                   color=color)
        except Exception as e:
            return f"Data Saved Successfully! (Risk prediction unavailable: {str(e)})"

    return render_template('child_data_form.html')


# ============================================================
# MODEL TRAINING (SINGLE FILE VERSION)
# ============================================================

def train_models():

    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.neural_network import MLPClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from imblearn.over_sampling import SMOTE

    # Load CSV dataset
    df = pd.read_csv("uploaded_dataset.csv")

    df.ffill(inplace=True)

    # Encode categorical
    for col in df.select_dtypes(include='object').columns:
        df[col] = LabelEncoder().fit_transform(df[col])

    X = df.drop("risk_label", axis=1)
    y = df["risk_label"]

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "SVM": SVC(probability=True),
        "MLP": MLPClassifier(max_iter=1000),
        "Random Forest": RandomForestClassifier()
    }

    best_model = None
    best_acc = 0
    results = {}


    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        results[name] = {
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1
        }
        if acc > best_acc:
            best_acc = acc
            best_model = model

    # Generate bar plot for model comparison
    import matplotlib.pyplot as plt
    import numpy as np
    if not os.path.exists('static'):
        os.makedirs('static')
    metrics = ['accuracy', 'precision', 'recall', 'f1_score']
    model_names = list(results.keys())
    values = {metric: [results[m][metric] for m in model_names] for metric in metrics}
    x = np.arange(len(model_names))
    width = 0.2
    plt.figure(figsize=(10,6))
    for i, metric in enumerate(metrics):
        plt.bar(x + i*width, values[metric], width, label=metric)
    plt.xticks(x + width*1.5, model_names)
    plt.ylabel('Score')
    plt.ylim(0, 1)
    plt.title('Model Comparison Metrics')
    plt.legend()
    plot_path = 'static/model_comparison.png'
    plt.savefig(plot_path)
    plt.close()
    # Format results for display
    for m in results:
        for metric in metrics:
            results[m][metric] = f"{results[m][metric]:.2f}"
    return results, plot_path
@app.route('/model-comparison')
def model_comparison():
    results, plot_path = train_models()
    plot_url = '/' + plot_path.replace('\\', '/')
    return render_template("model_comparison.html", results=results, plot_url=plot_url)

    joblib.dump(best_model, "best_model.pkl")

    return results


@app.route('/model-training')
def model_training():
    results = train_models()
    return render_template("model_training.html", results=results)


# ============================================================
# RISK PREDICTION
# ============================================================

@app.route('/risk-prediction', methods=['GET', 'POST'])
def risk_prediction():

    if request.method == 'POST':

        if not os.path.exists("best_model.pkl"):
            return "Model not trained yet!"

        age = float(request.form['age'])
        maternal_bmi = float(request.form['maternal_bmi'])
        diabetes = int(request.form['diabetes'])
        hypertension = int(request.form['hypertension'])
        child_bmi = float(request.form['child_bmi'])
        immunization = int(request.form['immunization'])

        model = joblib.load("best_model.pkl")

        features = np.array([[age,
                              maternal_bmi,
                              diabetes,
                              hypertension,
                              child_bmi,
                              immunization]])

        probability = model.predict_proba(features)[0][1]
        risk_label, color = classify_risk(probability)

        if risk_label == "High Risk":
            create_alert(1,
                         "High-Risk Pregnancy",
                         risk_label,
                         "Immediate intervention required.")

        return render_template("prediction_result.html",
                               probability=round(probability * 100, 2),
                               risk=risk_label,
                               color=color)

    return render_template("risk_prediction.html")


# ============================================================
# DECISION SUPPORT
# ============================================================

@app.route('/decision-support', methods=['POST'])
def decision_support():

    age = float(request.form['age'])
    maternal_bmi = float(request.form['maternal_bmi'])
    diabetes = int(request.form['diabetes'])
    hypertension = int(request.form['hypertension'])
    child_bmi = float(request.form['child_bmi'])
    immunization = int(request.form['immunization'])

    input_features = [
        age,
        maternal_bmi,
        diabetes,
        hypertension,
        child_bmi,
        immunization
    ]

    feature_names = [
        "Age",
        "Maternal BMI",
        "Diabetes",
        "Hypertension",
        "Child BMI",
        "Immunization"
    ]

    top_features = generate_explanation(input_features, feature_names)

    suggestions = []

    for feature, value in top_features:

        if feature == "Maternal BMI" and value > 0:
            suggestions.append("Nutritional counseling recommended.")

        if feature == "Diabetes" and value > 0:
            suggestions.append("Refer to endocrinologist.")

        if feature == "Hypertension" and value > 0:
            suggestions.append("Immediate BP monitoring required.")

        if feature == "Child BMI" and value > 0:
            suggestions.append("Child growth monitoring advised.")

    return render_template("decision_support.html",
                           features=top_features,
                           suggestions=suggestions)
# ============================================================
# ALERTS PAGE (ACTIVE ALERTS)
# ============================================================

@app.route('/alerts')
def alerts():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM alerts
        WHERE status = 'Active'
        ORDER BY created_at DESC
    """)
    alert_list = cursor.fetchall()

    conn.close()

    return render_template("alerts.html", alerts=alert_list)


# ============================================================
# NOTIFICATIONS PAGE (ALL ALERT HISTORY)
# ============================================================

@app.route('/notifications')
def notifications():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM alerts
        ORDER BY created_at DESC
    """)
    alert_list = cursor.fetchall()

    conn.close()

    return render_template("notifications.html", alerts=alert_list)


# ============================================================
# ANALYTICS DASHBOARD
# ============================================================

@app.route('/analytics')
def analytics():

    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM alerts", conn)
    conn.close()

    if df.empty:
        return "No data available for analytics."

    # ---------------- Pie Chart ----------------
    risk_counts = df['risk_level'].value_counts()

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure()
    plt.pie(risk_counts,
            labels=risk_counts.index,
            autopct='%1.1f%%')
    plt.title("Risk Distribution")
    plt.savefig("static/risk_distribution.png")
    plt.close()

    # ---------------- Trend Analysis ----------------
    df['created_at'] = pd.to_datetime(df['created_at'])

    trend_data = df.groupby(
        df['created_at'].dt.date
    ).size().reset_index(name='count')

    fig = px.line(trend_data,
                  x='created_at',
                  y='count',
                  title="Alert Trend Over Time")

    fig.write_html("static/trend.html")

    return render_template("analytics.html")


# ============================================================
# PDF REPORT GENERATION
# ============================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


@app.route('/reports')
def generate_report():

    file_path = "static/health_report.pdf"
    doc = SimpleDocTemplate(file_path)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(
        "Maternal & Child Mortality Risk Report",
        styles["Title"]
    ))

    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(
        "Risk Distribution Summary:",
        styles["Heading2"]
    ))

    elements.append(Spacer(1, 0.3 * inch))

    if os.path.exists("static/risk_distribution.png"):
        elements.append(Image(
            "static/risk_distribution.png",
            width=400,
            height=300
        ))

    doc.build(elements)

    return f"<a href='/static/health_report.pdf' download>Download Report</a>"


# ============================================================
# ADMIN PANEL
# ============================================================

@app.route('/admin-panel')
def admin_panel():
    return render_template("admin_panel.html")


# ---------------- Dataset Upload ----------------

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():

    file = request.files['dataset']

    if file and file.filename.endswith(".csv"):
        file.save("uploaded_dataset.csv")
        return "Dataset uploaded successfully!"

    return "Invalid file format. Please upload CSV."


# ---------------- Manage Users ----------------

@app.route('/manage-users')
def manage_users():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, age, location, education
        FROM patients
    """)

    users = cursor.fetchall()
    conn.close()

    return render_template("manage_users.html",
                           users=users)


# ---------------- Retrain Model ----------------

@app.route('/retrain-model')
def retrain_model():

    train_models()
    return "Model Retrained Successfully!"


# ============================================================
# HOME ROUTE
# ============================================================

@app.route('/')
def home():
    return redirect(url_for('patient_registration'))


# ============================================================
# FINAL RUN
# ============================================================

if __name__ == '__main__':
    app.run(debug=True)
