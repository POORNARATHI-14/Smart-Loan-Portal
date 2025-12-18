import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay

df=pd.read_csv(r"C:\Users\poorn\Downloads\project-20251212T021942Z-3-001\project\demopro\loan_data_set.csv")
#print(df)

df.replace("",float("nan"),inplace=True)

categorical_cols = ['Gender','Married','Education','Self_Employed','Property_Area','Loan_Status','Dependents']
numeric_cols = ['ApplicantIncome','CoapplicantIncome','LoanAmount','Loan_Amount_Term','Credit_History']

encoders={}

df['Dependents'].fillna(df['Dependents'].mode()[0], inplace=True)
for col in categorical_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

for col in numeric_cols:
    df[col].fillna(df[col].mean(), inplace=True)

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

#print(df)

df['TotalIncome'] = df['ApplicantIncome'] + df['CoapplicantIncome']
df['LoanRatio'] = df['LoanAmount'] / (df['TotalIncome'] + 1)
df['EMI'] = df['LoanAmount'] / df['Loan_Amount_Term']


X=df.drop(columns=['Loan_Status','Loan_ID'])
y=df['Loan_Status']
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.4,random_state=42)

#print("---------------")
#print(X_train,X_test)
#print("---------------")
#print(y_train,y_test)

#print("---------------")

model=DecisionTreeClassifier(random_state=42)
model.fit(X_train,y_train)

y_pred=model.predict(X_test)
acc=accuracy_score(y_test,y_pred)
print("DT Accuracy : ",acc)

model1 = RandomForestClassifier(
    n_estimators=600,
    max_depth=10,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    bootstrap=True
)

model1.fit(X_train, y_train)
y_pred1 = model1.predict(X_test)
print("RFC Accuracy:", accuracy_score(y_test, y_pred1))


joblib.dump(model1,"loan_model.joblib")
joblib.dump(encoders,"loan_encoders.joblib")

model = joblib.load("loan_model.joblib")
encoders = joblib.load("loan_encoders.joblib")

TRAIN_COLUMNS = [
    'Gender', 'Married', 'Dependents', 'Education', 'Self_Employed',
    'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term',
    'Credit_History', 'Property_Area', 'TotalIncome', 'LoanRatio', 'EMI'
]

def predict_loan_status(input_data):
    df = pd.DataFrame([input_data])

    for col in ['Gender','Married','Dependents','Education','Self_Employed','Property_Area']:
        if col in df.columns:
            df[col] = encoders[col].transform(df[col])

    df['TotalIncome'] = df['ApplicantIncome'] + df['CoapplicantIncome']
    df['LoanRatio'] = df['LoanAmount'] / (df['TotalIncome'] + 1)
    df['EMI'] = df['LoanAmount'] / df['Loan_Amount_Term']

    for col in TRAIN_COLUMNS:
        if col not in df.columns:
            df[col] = 0  

    df = df[TRAIN_COLUMNS]

    pred = model.predict(df)[0]
    return "Approved" if pred == 1 else "Rejected"


data = {
    'Gender':'Male',
    'Married':'Yes',
    'Dependents':'0',
    'Education':'Graduate',
    'Self_Employed':'No',
    'ApplicantIncome':80000,
    'CoapplicantIncome':20000,
    'LoanAmount':200000,
    'Loan_Amount_Term':360,
    'Credit_History':1,      
    'Property_Area':'Urban'
}
print(predict_loan_status(data))

datap = {
 'Gender':'Male',
 'Married':'Yes',
 'Dependents':'0',
 'Education':'Graduate',
 'Self_Employed':'No',
 'ApplicantIncome':8000,
 'CoapplicantIncome':2000,
 'LoanAmount':120,   
 'Loan_Amount_Term':360,
 'Credit_History':1,
 'Property_Area':'Urban'
}
print(predict_loan_status(datap))

def explain_result(input_data):
    reasons = []

    total_income = input_data['ApplicantIncome'] + input_data['CoapplicantIncome']
    loan_amt = input_data['LoanAmount']      
    loan_term = input_data['Loan_Amount_Term']
    credit = input_data['Credit_History']

    emi = loan_amt / loan_term
    emi_ratio = emi / (total_income + 1)

    if credit == 0:
        reasons.append("Poor credit history")

    if total_income < 5000:
        reasons.append("Low total income")

    if emi_ratio > 0.04:
        reasons.append("High EMI compared to income")

    if input_data['Education'] == "Not Graduate":
        reasons.append("Lower education level")

    if input_data['Property_Area'] == "Rural":
        reasons.append("High risk property area")

   
    if not reasons:
        reasons.append("Good credit history")
        reasons.append("Sufficient income")
        reasons.append("Affordable EMI")
        reasons.append("Low financial risk")

    return reasons

models = {
    "Decision Tree": (model, y_pred),
    "Random Forest": (model1, y_pred1)
}

for name, (m, y_p) in models.items():
    print(f"--- {name} ---")
    print("Accuracy:", accuracy_score(y_test, y_p))
    print("Precision:", precision_score(y_test, y_p))

    cm = confusion_matrix(y_test, y_p)
    print("Confusion Matrix:\n", cm)
    print("\n")