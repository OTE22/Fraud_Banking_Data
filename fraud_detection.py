import streamlit as st
import joblib
import pandas as pd

model = joblib.load("baseline_fraud_model.pkl")
st.title("Fraud Detection Model")

model.pre