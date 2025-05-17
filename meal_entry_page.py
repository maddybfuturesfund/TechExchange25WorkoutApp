import streamlit as st
from google.cloud import bigquery
from data_fetcher import get_user_today_calorie_tracking, get_genai_nutrition_feedback, get_user_weekly_calorie_summary
import streamlit as st
from modules import display_macro_calorie_chart, display_weekly_calorie_summary
import datetime
import time

userId = 'user1'
def display_meal_entry_page(userId):
    st.header("Calorie/Macro Tracking")
    meal_list = get_user_today_calorie_tracking(userId)

    @st.dialog("Meal Entry")
    def show_meal_entry():
        st.subheader("Enter Your Meal")
        date = st.date_input("What date did you eat?")
        mealname = st.text_input("What did you eat?")
        calories = st.number_input("How many calories did you eat?", min_value=0)
        protein = st.number_input("How many grams of protein did you eat?", min_value=0)
        carbs = st.number_input("How many grams of carbs did you eat?", min_value=0)
        fat = st.number_input("How many grams of fat did you eat?", min_value=0)
        submitted = st.button("Submit")

        if submitted:
                print("submit button clicked")   
                new_row = {
                    "MealId": "meal" + str(len(meal_list) + 1),
                    "UserId": userId,
                    "MealName": mealname,
                    "Calories": calories,
                    "Protein": protein,
                    "Carbs": carbs,
                    "Fats": fat,
                    "MealDate": date.strftime('%Y-%m-%d'),
                    "CreatedAt": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
                }

                try:
                    client = bigquery.Client(project="sectiona4project")
                    table_ref = client.dataset("ISE").table("CalorieTracking")

                    rows_to_insert = [new_row]
                    errors = client.insert_rows_json(table_ref, rows_to_insert)

                    if errors == []:
                        st.write("Entry successful")
                        st.rerun()
                        print("Successfully added row to sectiona4project.ISE.CalorieTracking")
                    else:
                        st.write("Entry failed")
                        print(f"Errors encountered while inserting rows: {errors}")

                except Exception as e:
                    print(f"An error occurred: {e}")
    

    if st.button("Meal Entry"):
        show_meal_entry()

    display_macro_calorie_chart(meal_list)


    st.markdown("## 🧠 AI-Powered Nutrition Feedback")
    
    with st.container():
        if st.button("💡 Generate Today's Feedback"):
            with st.spinner("Analyzing your meal data and generating feedback..."):
                feedback = get_genai_nutrition_feedback(userId)

            with st.expander("📋 View Nutrition Feedback", expanded=True):
                st.write(feedback["content"])


    st.markdown("## 📅 Weekly Meal Summary")
    weekly_df = get_user_weekly_calorie_summary(userId)
    display_weekly_calorie_summary(weekly_df)
if __name__ == '__main__':
    display_meal_entry_page(userId)