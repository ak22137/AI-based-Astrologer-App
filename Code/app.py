import streamlit as st
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
import datetime
import google.generativeai as genai

# --- UI ---
st.set_page_config(page_title="AI Astrologer", layout="centered")
st.title("AI Astrologer")
st.write("Enter your birth details and ask any astrology question!")

name = st.text_input("Name")
date = st.date_input(
    "Date of Birth",
    min_value=datetime.date(1990, 1, 1),
    max_value=datetime.date.today(),
    value=datetime.date(1990, 1, 1)
)
time = st.text_input("Time of Birth (HH:MM)")
place = st.text_input("Place of Birth")
question = st.text_area("Ask a free-text astrology question")

submit = st.button("Get Astrology Response")

# --- Astrology Logic (Rule-based + AI-driven) ---
def astrology_response(name, date, time, place, question):
    # Rule-based example: Zodiac sign
    try:
        month = date.month
        day = date.day
        zodiac = get_zodiac_sign(month, day)
    except Exception:
        zodiac = "Unknown"

    prompt = (
        f"You are an expert astrologer. Given the following details:\n"
        f"Name: {name}\nDate: {date}\nTime: {time}\nPlace: {place}\nZodiac: {zodiac}\n"
        f"Question: {question}\n"
        "Provide a helpful, insightful astrology-based answer."
    )

    # Gemini Flash 2.0 API call
    api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else None
    if not api_key:
        return "Gemini API key not found. Please add it to Streamlit secrets."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    answer = response.text if hasattr(response, "text") else str(response)
    return f"Zodiac Sign: {zodiac}\n\n{answer}"

# Zodiac sign calculation (simple Western astrology)
def get_zodiac_sign(month, day):
    zodiac_dates = [
        (1, 20, "Aquarius"), (2, 19, "Pisces"), (3, 21, "Aries"), (4, 20, "Taurus"),
        (5, 21, "Gemini"), (6, 21, "Cancer"), (7, 23, "Leo"), (8, 23, "Virgo"),
        (9, 23, "Libra"), (10, 23, "Scorpio"), (11, 22, "Sagittarius"), (12, 22, "Capricorn")
    ]
    for i in range(len(zodiac_dates)):
        m, d, sign = zodiac_dates[i]
        if (month == m and day >= d) or (month == (m % 12) + 1 and day < zodiac_dates[(i+1)%12][1]):
            return sign
    return "Capricorn"

# --- LangGraph Example (optional, for advanced flows) ---
def langgraph_astrology_flow():
    # Example: Simple graph with one node
    graph = StateGraph()
    def node_fn(state):
        return astrology_response(**state)
    graph.add_node("astrology", node_fn)
    graph.add_edge("astrology", END)
    graph.set_entry_point("astrology")
    return graph

# --- Main Logic ---
if submit:
    if not (name and date and time and place and question):
        st.error("Please fill in all fields and ask a question.")
    else:
        with st.spinner("Consulting the stars..."):
            result = astrology_response(name, date, time, place, question)
            st.success(result)
