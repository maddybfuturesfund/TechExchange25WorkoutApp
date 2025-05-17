#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################
import streamlit as st
from internals import create_component
import streamlit as st
import pandas as pd
import altair as alt
# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Displays a user post in a formatted Streamlit layout."""
    with st.container():
        # User Info Section
        col1, col2 = st.columns([1, 8])
        with col1:
            st.image(user_image, width=50)
        with col2:
            st.markdown(f"**{username}**")
            st.caption(timestamp)

        # Post Content
        st.write(content)

        # Post Image (if exists)
        if post_image:
            st.image(post_image, use_container_width=False)
    
        st.markdown("---")

# Function written in part with Gemini
# Prompt: what should display_activity_summary return
# https://docs.google.com/document/d/1Q6FG2HOza7nRNnsZdfhs8krbtd_FY57Byn4MoN9fSMk/edit?usp=sharing
def display_activity_summary(workouts_list):
    """Displays a summary and charts of the user's workout activities.

    Args:
        workouts_list (list of dictionaries): List of workout sessions, each containing:
            - 'start_timestamp': str
            - 'end_timestamp': str
            - 'dihonstance': float (km)
            - 'steps': int
            - 'calories_burned': int
    Return: A dictionary of processed data.
    """

    st.subheader("Your Workout Summary")

    if not workouts_list:
        st.write("No workouts found.")
        return {}
        

    workout_details = []
    for workout in workouts_list:
        workout_details.append({
            "workout_id": workout.get('workout_id', 'N/A'),
            "start_timestamp": workout.get('start_timestamp', 'N/A'),
            "end_timestamp": workout.get('end_timestamp', 'N/A'),
            "distance": workout.get('distance', 0),
            "steps": workout.get('steps', 0),
            "calories_burned": workout.get('calories_burned', 0)
        })

    for workout in workouts_list:
        if "distance" not in workout or "steps" not in workout or "calories_burned" not in workout:
            st.write("Cannot display chart data with missing values.")

    total_distance = sum(workout['distance'] for workout in workouts_list)
    total_steps = sum(workout['steps'] for workout in workouts_list)
    total_calories = sum(workout['calories_burned'] for workout in workouts_list)

    workout_names = [f"Workout {i+1}" for i in range(len(workouts_list))]
    distances = [workout['distance'] for workout in workouts_list]
    steps = [workout['steps'] for workout in workouts_list]

    for workout in workout_details:
        with st.container():
            st.markdown(f"**Workout ID:** {workout['workout_id']}")
            st.write(f"📅 **Start Time:** {workout['start_timestamp']}")
            st.write(f"🏁 **End Time:** {workout['end_timestamp']}")
            st.write(f"📏 **Distance:** {workout['distance']} km")
            st.write(f"🚶 **Steps:** {workout['steps']}")
            st.write(f"🔥 **Calories Burned:** {workout['calories_burned']} kcal")
            st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Distance", f"{total_distance:.1f} km")
    col2.metric("Total Steps", f"{total_steps:,}")
    col3.metric("Calories Burned", f"{total_calories} kcal")

    st.line_chart({"Distance (km)": distances}, use_container_width=True)
    st.bar_chart({"Steps": steps}, use_container_width=True)

    st.write("Stay consistent and keep pushing yourself! 💪")

def display_recent_workouts(workouts_list):
    """
    Displays information about each workout in the list

    Args: List of workout with each workout being a dictionary of information about distance, calories, steps, location, and time
    
    Returns: None
    """
    #Used Gemini to help with layout of columns, avoid using HTML custom components(original code included creating a custom HTML component for each workout but found it was hard to test that way) and with CSS of containers
    #Prompts: How can I create with columns of containers in streamlit? CSS for creating a box shadow on a container?
    if len(workouts_list) == 0:
        st.text("No workouts to display.")
        return
    st.subheader('Recent Workouts')

  

    cols = st.columns(3)

    for i, workout in enumerate(workouts_list):
        # Select the appropriate column for this workout
        col = cols[i % 3]  # Cycle through columns

        with col:
            # Create an inner container for each workout
            inner_container = st.container()
            inner_container.subheader("Workout " + str(i+1))
            with inner_container:
                # Add workout information to the inner container
                st.write(f"Workout Date: {workout['start_timestamp'][:10]}")
                st.write(f"Workout Start Time: {workout['start_timestamp'][11:]}")
                st.write(f"Workout End Time: {workout['end_timestamp'][11:]}")
                st.write(f"Distance: {workout['distance']} miles")
                st.write(f"Steps: {workout['steps']}")
                st.write(f"Calories Burned: {workout['calories_burned']}")
                st.write(f"Start Location: {workout['start_lat_lng']}")
                st.write(f"End Location: {workout['end_lat_lng']}")
       

def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    
    st.header("Gen AI ADVICE")
    st.write(f"timestamp : {timestamp}")
    st.write(f"content: {content}")
    if not image:
        st.write("No image to be displayed")
    else:
        # print(f"Rendering image: {image}") 
        st.image(image)

    

def display_filtered_workouts(filtered_workouts):
    """
    Displays filtered workouts in a 3-column layout similar to display_recent_workouts.

    Args:
        filtered_workouts (list of dicts): Each workout should contain:
            - 'workout_id': str
            - 'start_timestamp': str
            - 'end_timestamp': str
            - 'distance': float
            - 'steps': int
            - 'calories_burned': int
            - 'start_lat_lng': tuple
            - 'end_lat_lng': tuple
    """
    if not filtered_workouts:
        st.info("No workout found during this time")
        return

    st.subheader("Filtered Workouts")

    cols = st.columns(3)  # Creates a 3-column layout

    for i, workout in enumerate(filtered_workouts):
        col = cols[i % 3]  # Cycle through the 3 columns: 0, 1, 2

        with col:
            with st.container():
                st.subheader(f"Workout {i + 1}")
                st.write(f"🆔 **ID:** {workout.get('workout_id', 'N/A')}")
                st.write(f"🕒 **Start:** {workout.get('start_timestamp', 'N/A')}")
                st.write(f"🏁 **End:** {workout.get('end_timestamp', 'N/A')}")
                st.write(f"📏 **Distance:** {workout.get('distance', 0)} miles")
                st.write(f"🚶 **Steps:** {workout.get('steps', 0)}")
                st.write(f"🔥 **Calories:** {workout.get('calories_burned', 0)} kcal")
                st.write(f"📍 **Start Location:** {workout.get('start_lat_lng', 'N/A')}")
                st.write(f"📍 **End Location:** {workout.get('end_lat_lng', 'N/A')}")

    pass

#Used Gemini to help me figure out a way to display data in a table and have the totals of the macros in the last column
def display_macro_calorie_chart(meal_list):
    df = pd.DataFrame(meal_list)

    if len(meal_list) != 0:
        columns_to_display = ['meal_name', 'calories', 'protein', 'carbs', 'fat']
        if all(col in df.columns for col in columns_to_display):
            df_display = df[columns_to_display].copy()
            df_display.columns = ['Meal', 'Calories', 'Protein', 'Carbs', 'Fats'] # Rename columns for clarity
            
            numeric_cols = df[['calories', 'protein', 'carbs', 'fat']] # Explicitly select numeric columns
            sums = numeric_cols.sum()

            # Create a DataFrame for the totals row
            totals_row = pd.DataFrame([['Total', sums['calories'], sums['protein'], sums['carbs'], sums['fat']]],
                                    columns=['Meal', 'Calories', 'Protein', 'Carbs', 'Fats'])

            # Concatenate the original DataFrame with the totals row
            combined_df = pd.concat([df_display, totals_row], ignore_index=False)

            st.subheader("Today's Meals")
            st.table(combined_df)
        
    else:
        st.write("No meal data")



def display_weekly_calorie_summary(df):
    """Displays a bar chart of daily nutrient totals for the week."""
    if df.empty:
        st.info("No meal data available for the past week.")
        return

    st.subheader("📊 Weekly Calorie & Macro Summary")

    df["MealDate"] = df["MealDate"].astype(str)

    st.dataframe(df)

    # Melt dataframe for grouped bar chart
    melted = df.melt(id_vars="MealDate", value_vars=["total_calories", "total_protein", "total_fats", "total_carbs"],
                     var_name="Nutrient", value_name="Value")

    # chart = alt.Chart(melted).mark_bar().encode(
    #     x=alt.X('MealDate:N', title='Date'),
    #     y=alt.Y('Value:Q', title='Total'),
    #     color='Nutrient:N',
    #     column='Nutrient:N'
    # ).properties(height=300).interactive()

    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X('MealDate:N', title='Date'),
        y=alt.Y('Value:Q', title='Total'),
        color=alt.Color('Nutrient:N', title='Nutrient'),
        xOffset='Nutrient:N'
    ).properties(height=400).configure_axisX(labelAngle=0)

    st.altair_chart(chart, use_container_width=True)
