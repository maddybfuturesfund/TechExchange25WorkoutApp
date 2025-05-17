import streamlit as st
from google.cloud import bigquery
from data_fetcher import get_genai_advice

user_id = 'user1'

FRIENDS_QUERY = """
    SELECT
        CASE
            WHEN UserId1 = @user_id THEN UserId2
            ELSE UserId1
        END AS friend_id
    FROM `sectiona4project.ISE.Friends`
    WHERE UserId1 = @user_id OR UserId2 = @user_id
"""

POSTS_QUERY = """
    SELECT PostId, AuthorId, Timestamp, ImageUrl, Content
    FROM `sectiona4project.ISE.Posts`
    WHERE AuthorId IN UNNEST(@friend_ids)
    ORDER BY Timestamp DESC
    LIMIT 10
"""

def get_friends(user_id):
  
    client = bigquery.Client(project="sectiona4project")

    # friends_params = {"user_id": user_id}
    
    friends_results = client.query(FRIENDS_QUERY, job_config=bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ])).result()

    friend_ids = [row.friend_id for row in friends_results]
    return friend_ids


def get_friends_latest_posts(user_id):
    friend_ids = get_friends(user_id)

    if not friend_ids:
        st.write("You have no friends, no posts to show.")
        return []

    client = bigquery.Client(project="sectiona4project")

    posts_results = client.query(POSTS_QUERY, job_config=bigquery.QueryJobConfig(query_parameters=[
        bigquery.ArrayQueryParameter("friend_ids", "STRING", friend_ids)
    ])).result()

    return posts_results

def community_page(user_id):
    st.title("Community Page")
    
    posts = get_friends_latest_posts(user_id)

    if posts:
        st.header("Latest Posts from Your Friends:")
        for post in posts:
            st.write(f"Post ID: {post.PostId}")
            st.write(f"Friend's ID: {post.AuthorId}")
            st.write(f"Content: {post.Content}")
            st.write(f"Timestamp: {post.Timestamp}")
            if post.ImageUrl:
                st.image(post.ImageUrl)
            st.write("---")
    
    st.header("GenAI Advice and Encouragement:")
    advice = get_genai_advice(user_id)
    st.write(f"Advice: {advice['content']}")

    if advice["image"]:
        st.image(advice["image"])


if __name__ == "__main__":
    community_page(user_id)