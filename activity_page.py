import streamlit as st
from data_fetcher import get_user_workouts, get_user_posts
from modules import display_recent_workouts, display_activity_summary
from google.cloud import bigquery
import datetime
import uuid

userId = 'user1'
def display_activity_page(userId):
    st.header("Activity Page")

    st.subheader("Filter Workouts by Date")
    apply_filter = st.checkbox("Filter by date range")

    workouts = get_user_workouts(userId)

    if apply_filter:
        today = datetime.date.today()
        default_start = today - datetime.timedelta(days=30)

        start_end = st.date_input(
            label="Select date range:",
            value=(default_start, today),
            max_value=today,
        )

        if isinstance(start_end, tuple) and len(start_end) == 2:
            start_date, end_date = start_end
        else:
            st.error("Please select a valid start and end date.")
            return

        # Filter workouts by date
        filtered_workouts = []
        for w in workouts:
            ts = w.get('start_timestamp')
            if ts:
                try:
                    workout_date = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').date()
                    if start_date <= workout_date <= end_date:
                        filtered_workouts.append(w)
                except ValueError:
                    st.write(f"Invalid timestamp format: {ts}")

    else:
        filtered_workouts = workouts[:]

    if not filtered_workouts:
        st.warning("No workouts found for the selected criteria.")
    else:
        if len(filtered_workouts) > 3:
            display_recent_workouts(filtered_workouts[:3])
        else:
            display_recent_workouts(filtered_workouts)
    
        display_activity_summary(filtered_workouts)

    if filtered_workouts and len(filtered_workouts) > 0:
        steps = filtered_workouts[-1]['steps']
        calories = filtered_workouts[-1]['calories_burned']
        distance = filtered_workouts[-1]['distance']

    else:
        steps = 0 
        calories = 0
        distance = 0
        st.warning("No workout data available to share.")



    if "text_area_content" not in st.session_state:
        st.session_state["text_area_content"] = ""

    st.write("What achievement would you like to share from your workout?")
    col1, col2, col3 = st.columns(3)
    with col1:
        steps_button = st.button("Total Steps")
    with col2:
        distance_button = st.button("Distance")
    with col3:
        calories_button = st.button("Calories Burned")


    if steps_button:
        st.session_state["text_area_content"] = f"I walked {steps} steps today!"
    if calories_button:
        st.session_state["text_area_content"] = f"I burned {calories} calories in my recent workout!"
    if distance_button:
        st.session_state["text_area_content"] = f"I ran {distance} miles today!"

    post_content = st.text_area("What would you like to share?", placeholder = 'Share your fitness goals and achievements with others!', value = st.session_state["text_area_content"])
    share_button = st.button("share")



    if share_button:
        print("share button clicked")   
        new_row = {
            "PostId": "post" + str(len(get_user_posts(userId)) + 1),
            "AuthorId": userId,
            "Timestamp": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            "ImageUrl": "http://example.com/posts/post5.jpg",
            "Content": post_content
        }

        try:
            client = bigquery.Client(project="sectiona4project")
            table_ref = client.dataset("ISE").table("Posts")

            rows_to_insert = [new_row]
            errors = client.insert_rows_json(table_ref, rows_to_insert)

            if errors == []:
                st.write("Post created successfully")
                print("Successfully added row to sectiona4project.ISE.Posts")
                st.rerun()
            else:
                print(f"Errors encountered while inserting rows: {errors}")

        except Exception as e:
            print(f"An error occurred: {e}")



if __name__ == '__main__':
    display_activity_page(userId)
    
    
