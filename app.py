#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts
from google.cloud import bigquery



userId = 'user1'

def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to your workout space!')

    
    # An example of displaying a custom component called "my_custom_component"
    #value = st.text_input('Enter your awesome name')
    #display_my_custom_component(value)


    #Display
    workouts = get_user_workouts(userId)
    display_activity_summary(workouts)
    display_recent_workouts(workouts)
    display_genai_advice_component(userId)
    display_display_posts(userId)

def display_display_posts(userId):
    st.title('Posts')
    posts = get_user_posts(userId)
    for post in posts:
        user_profile = get_user_profile(post['user_id'])
        post_image = post['image'] if post['image'] and post['image'].startswith("http") else None
        display_post(
            username=user_profile['username'],
            user_image=user_profile['profile_image'],
            timestamp=post['timestamp'],
            content=post['content'],
            post_image=post_image
        )

def display_genai_advice_component(userId):

    gen_ai_data = get_genai_advice(userId)
    print(gen_ai_data)
    display_genai_advice(gen_ai_data['timestamp'], gen_ai_data['content'], gen_ai_data['image'])



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
    
