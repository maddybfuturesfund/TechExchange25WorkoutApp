#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

from google.cloud import bigquery
import random
import os 
import uuid
from datetime import datetime, timedelta
import vertexai
from vertexai.preview.generative_models import GenerativeModel

QUERY_WORKOUTS = """
    SELECT * FROM `sectiona4project.ISE.Workouts` 
    WHERE UserId = @user_id
"""

QUERY_SENSOR_DATA = """
    SELECT
        sd.Timestamp,
        sd.SensorValue,
        st.Name AS SensorName,
        st.Units AS SensorUnits
    FROM
        `sectiona4project.ISE.SensorData` AS sd
    JOIN
        `sectiona4project.ISE.SensorTypes` AS st ON sd.SensorId = st.SensorId
    WHERE
        sd.WorkoutID = @workout_id
    ORDER BY
        sd.Timestamp
"""
ADVICE_QUERY = """
    SELECT TotalDistance, TotalSteps, CaloriesBurned
    FROM `sectiona4project.ISE.Workouts`
    WHERE UserId = @user_id
    ORDER BY EndTimestamp DESC
    LIMIT 1
"""

QUERY_PROFILES = """
    SELECT * FROM `sectiona4project.ISE.Users` 
    WHERE UserId = @user_id
"""

QUERY_POSTS = """
    SELECT * FROM `sectiona4project.ISE.Posts` 
    WHERE AuthorId = @user_id
"""

QUERY_WORKOUTS_BY_DATE = """
    SELECT * FROM `sectiona4project.ISE.Workouts` 
    WHERE UserId = @user_id
    AND DATE(StartTimestamp) BETWEEN @start_date AND @end_date
"""

QUERY_CALORIES = """
    SELECT * FROM `sectiona4project.ISE.CalorieTracking` 
    WHERE UserId = @user_id
"""

QUERY_TODAY_CALORIES = """
    SELECT * FROM `sectiona4project.ISE.CalorieTracking` WHERE MealDate=CURRENT_DATE()
    AND UserId = @user_id
"""

QUERY_NUTRITION_FEEDBACK = """
    SELECT 
    SUM(Calories) AS total_calories,
    SUM(Protein) AS total_protein,
    SUM(Fats) AS total_fats,
    SUM(Carbs) AS total_carbs
    FROM `sectiona4project.ISE.CalorieTracking`
    WHERE UserId = @user_id AND MealDate = @meal_date
"""

WEEKLY_CALORIE_QUERY = """
    SELECT 
        MealDate,
        SUM(Calories) AS total_calories,
        SUM(Protein) AS total_protein,
        SUM(Fats) AS total_fats,
        SUM(Carbs) AS total_carbs
    FROM `sectiona4project.ISE.CalorieTracking`
    WHERE UserId = @user_id AND MealDate BETWEEN @start_date AND @end_date
    GROUP BY MealDate
    ORDER BY MealDate
"""

def get_user_sensor_data(user_id, workout_id):
    """Fetch timestamped sensor data for a given workout from BigQuery.

    Args:
        user_id (str): The ID of the user (not used, kept for consistency).
        workout_id (str): The ID of the workout.

    Returns:
        list: A list of sensor readings as dictionaries.
    """
    if not workout_id:
        raise ValueError("Workout ID must not be empty.")

    client = bigquery.Client(project="sectiona4project")
    query_job = client.query(
        QUERY_SENSOR_DATA,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id)]
        )
    )

    return [
        {
            'sensor_type': row.SensorName,
            'timestamp': row.Timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            'data': row.SensorValue,
            'units': row.SensorUnits
        }
        for row in query_job.result()
    ]


def get_user_workouts(user_id) -> list:
    """Fetch user's workout data from BigQuery.

    Args:
        user_id (str): The ID of the user.

    Returns:
        list: A list of workout records as dictionaries.
    """
    client = bigquery.Client(project="sectiona4project")
    query_job = client.query(
        QUERY_WORKOUTS,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
    )

    return [
        {
            'workout_id': row.WorkoutId,
            'start_timestamp': row.StartTimestamp.strftime('%Y-%m-%d %H:%M:%S') if row.StartTimestamp else None,
            'end_timestamp': row.EndTimestamp.strftime('%Y-%m-%d %H:%M:%S') if row.EndTimestamp else None,
            'start_lat_lng': (row.StartLocationLat, row.StartLocationLong) if row.StartLocationLat and row.StartLocationLong else None,
            'end_lat_lng': (row.EndLocationLat, row.EndLocationLong) if row.EndLocationLat and row.EndLocationLong else None,
            'distance': row.TotalDistance,
            'steps': row.TotalSteps,
            'calories_burned': row.CaloriesBurned,
        }
        for row in query_job.result()
    ]


def get_user_profile(user_id):
    
    client = bigquery.Client(project="sectiona4project")
    query_job = client.query(
        QUERY_PROFILES,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
    )

    results = []
    for row in query_job.result():
        results.append({
            'user_id': row.UserId,
            'full_name': row.Name,
            'username': row.Username,
            'profile_image': row.ImageUrl,
            'date_of_birth': row.DateOfBirth
        })
    
    if not results:
        return None
    else:
        return results[0]
    '''
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]
    '''


def get_user_posts(user_id):
    
    client = bigquery.Client(project="sectiona4project")
    query_job = client.query(
        QUERY_POSTS,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
    )
    return[
        {
            'user_id': row.AuthorId,
            'post_id': row.PostId,
            'timestamp': row.Timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'content': row.Content,
            'image': row.ImageUrl
        }
        for row in query_job.result()
    ]
    
    """
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])
    return [{
        'user_id': user_id,
        'post_id': 'post1',
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'image': 'image_url',
    }]
    """


vertexai.init(project="sectiona4project", location="us-central1")
model = GenerativeModel(model_name="gemini-1.5-flash-002")
def get_genai_advice(user_id):
    """Generates fitness advice based on the user's most recent workout."""
    if not user_id:
        raise ValueError("User ID must not be empty.")

    IMAGES = [
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None
    ]

    client = bigquery.Client(project="sectiona4project")

    query_job = client.query(
        ADVICE_QUERY,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
            ]
        )
    )

    workout_row = next(query_job.result(), None)

    if not workout_row:
        return {
            "advice_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "content": "No recent workout data found.",
            "image": None
        }

    total_distance = workout_row.TotalDistance
    total_steps = workout_row.TotalSteps
    calories_burned = workout_row.CaloriesBurned

    prompt = (
        f"Based on a workout where the user covered {total_distance} km, "
        f"took {total_steps} steps, and burned {calories_burned} calories, "
        f"give a brief fitness advice on recovery, future training, or improvements."
    )

    response = model.generate_content(prompt)
    advice_content = response.text if response else "Could not generate advice."

    return {
        "advice_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "content": advice_content,
        "image": random.choice(IMAGES)
    }

def get_genai_nutrition_feedback(user_id):
    """Generates nutrition feedback based on today's total calorie and macro intake."""
    if not user_id:
        raise ValueError("User ID must not be empty.")

    client = bigquery.Client(project="sectiona4project")

    today = datetime.utcnow().date()

    query_job = client.query(
        QUERY_NUTRITION_FEEDBACK,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("meal_date", "DATE", today)
            ]
        )
    )

    result = next(query_job.result(), None)

    if not result or result.total_calories is None:
        return {
            "feedback_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "content": "No nutrition data found for today. Try logging your meals!",
            "image": None
        }

    calories = result.total_calories
    protein = result.total_protein
    fats = result.total_fats
    carbs = result.total_carbs

    prompt = (
        f"Today, the user consumed:\n"
        f"- Calories: {calories} kcal\n"
        f"- Protein: {protein} g\n"
        f"- Fats: {fats} g\n"
        f"- Carbohydrates: {carbs} g\n\n"
        "Provide brief, personalized nutrition feedback. Suggest improvements, assess balance, and be encouraging. "
        "Compare to average adult dietary recommendations."
    )

    response = model.generate_content(prompt)
    feedback_content = response.text if response else "Could not generate feedback."

    return {
        "feedback_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "content": feedback_content
    }

def get_user_calorie_tracking(user_id):
        client = bigquery.Client(project="sectiona4project")
        query_job = client.query(
            QUERY_CALORIES,
            job_config=bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]))

        return [
        {
            'meal_id': row.MealId if row.MealId else None,
            'user_id': row.UserId if row.UserId else None,
            'date': row.MealDate.strftime('%Y-%m-%d') if row.MealDate else None,
            'meal_name': row.MealName if row.MealName else None,
            'calories': row.Calories if row.Calories else None,
            'protein': row.Protein if row.Protein else None,
            'carbs': row.Carbs if row.Carbs else None,
            'fat': row.Fats if row.Fats else None,
            'created_at': row.CreatedAt.strftime('%Y-%m-%d %H:%M:%S') if row.CreatedAt else None
        }
        for row in query_job.result()
    ]

def get_user_today_calorie_tracking(user_id):
        client = bigquery.Client(project="sectiona4project")
        query_job = client.query(
            QUERY_TODAY_CALORIES,
            job_config=bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]))

        return [
        {
            'meal_id': row.MealId if row.MealId else None,
            'user_id': row.UserId if row.UserId else None,
            'date': row.MealDate.strftime('%Y-%m-%d') if row.MealDate else None,
            'meal_name': row.MealName if row.MealName else None,
            'calories': row.Calories if row.Calories else None,
            'protein': row.Protein if row.Protein else None,
            'carbs': row.Carbs if row.Carbs else None,
            'fat': row.Fats if row.Fats else None,
            'created_at': row.CreatedAt.strftime('%Y-%m-%d %H:%M:%S') if row.CreatedAt else None
        }
        for row in query_job.result()
    ]

        


def get_user_workouts_by_date(user_id: str, start_date: str, end_date: str) -> list:
    """
    Fetch user's workouts between a start and end date (inclusive).

    Args:
        user_id (str): User ID
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
        list: Filtered workout records
    """
    client = bigquery.Client(project="sectiona4project")
    query_job = client.query(
        QUERY_WORKOUTS_BY_DATE,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
    )

    return [
        {
            'workout_id': row.WorkoutId,
            'start_timestamp': row.StartTimestamp.isoformat() if row.StartTimestamp else None,
            'end_timestamp': row.EndTimestamp.isoformat() if row.EndTimestamp else None,
            'start_lat_lng': (row.StartLocationLat, row.StartLocationLong) if row.StartLocationLat and row.StartLocationLong else None,
            'end_lat_lng': (row.EndLocationLat, row.EndLocationLong) if row.EndLocationLat and row.EndLocationLong else None,
            'distance': row.TotalDistance,
            'steps': row.TotalSteps,
            'calories_burned': row.CaloriesBurned,
        }
        for row in query_job.result()
    ]


def get_user_weekly_calorie_summary(user_id):
    """Fetches total calories and macros for each of the last 7 days."""
    client = bigquery.Client(project="sectiona4project")

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", today),
        ]
    )

    query_job = client.query(WEEKLY_CALORIE_QUERY, job_config=job_config)
    return query_job.to_dataframe()