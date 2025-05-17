#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import uuid
from data_fetcher import get_user_sensor_data, get_user_workouts, get_genai_advice, get_user_posts, get_user_profile, get_genai_nutrition_feedback, get_user_weekly_calorie_summary, get_user_today_calorie_tracking


class TestGetUserSensorData(unittest.TestCase):

    @patch("data_fetcher.bigquery.Client")
    def test_valid_data(self, mock_client_cls):
        """Test fetching valid sensor data."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_row = MagicMock()
        mock_row.SensorName = "Heart Rate"  # Match function's attribute names
        mock_row.Timestamp = datetime(2024, 7, 29, 7, 15, 0)
        mock_row.SensorValue = 120.0
        mock_row.SensorUnits = "bpm"

        mock_client.query.return_value.result.return_value = [mock_row]

        result = get_user_sensor_data("user1", "workout1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sensor_type"], "Heart Rate")
        self.assertEqual(result[0]["timestamp"], "2024-07-29T07:15:00")
        self.assertEqual(result[0]["data"], 120.0)
        self.assertEqual(result[0]["units"], "bpm")

    @patch("data_fetcher.bigquery.Client")
    def test_no_data(self, mock_client_cls):
        """Test when workout ID returns no sensor data."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_client.query.return_value.result.return_value = []

        result = get_user_sensor_data("user1", "workout2")
        self.assertEqual(result, [])

    def test_invalid_workout_id(self):
        """Test with missing workout ID."""
        with self.assertRaises(ValueError):
            get_user_sensor_data("user1", "")

class TestGetUserWorkouts(unittest.TestCase):
    @patch("data_fetcher.bigquery.Client")  # Mocking BigQuery client globally
    def test_valid_workout_data(self, mock_client):
        """Test fetching valid workout data."""
        mock_instance = mock_client.return_value
        mock_query_job = MagicMock()

        mock_row = MagicMock()
        mock_row.WorkoutId = "workout1"
        mock_row.StartTimestamp = datetime(2024, 7, 29, 7, 0, 0)
        mock_row.EndTimestamp = datetime(2024, 7, 29, 8, 0, 0)
        mock_row.StartLocationLat = 34.0522
        mock_row.StartLocationLong = -118.2437
        mock_row.EndLocationLat = 34.0523
        mock_row.EndLocationLong = -118.2438
        mock_row.TotalDistance = 5.0
        mock_row.TotalSteps = 10000
        mock_row.CaloriesBurned = 500

        mock_query_job.result.return_value = [mock_row]
        mock_instance.query.return_value = mock_query_job

        result = get_user_workouts("user1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["workout_id"], "workout1")
        self.assertEqual(result[0]["start_timestamp"], "2024-07-29 07:00:00")
        self.assertEqual(result[0]["end_timestamp"], "2024-07-29 08:00:00")
        self.assertEqual(result[0]["start_lat_lng"], (34.0522, -118.2437))
        self.assertEqual(result[0]["end_lat_lng"], (34.0523, -118.2438))
        self.assertEqual(result[0]["distance"], 5.0)
        self.assertEqual(result[0]["steps"], 10000)
        self.assertEqual(result[0]["calories_burned"], 500)

    @patch("data_fetcher.bigquery.Client")
    def test_no_workout_data(self, mock_client):
        """Test when no workouts are found."""
        mock_instance = mock_client.return_value
        mock_query_job = MagicMock()
        
        mock_query_job.result.return_value = []
        mock_instance.query.return_value = mock_query_job

        result = get_user_workouts("user_without_workouts")
        self.assertEqual(result, [])

    @patch("data_fetcher.bigquery.Client")
    def test_missing_optional_fields(self, mock_client):
        """Test when some optional fields are missing."""
        mock_instance = mock_client.return_value
        mock_query_job = MagicMock()
        
        mock_row = MagicMock()
        mock_row.WorkoutId = "workout1"
        mock_row.StartTimestamp = datetime(2024, 7, 29, 7, 0, 0)
        mock_row.EndTimestamp = None
        mock_row.StartLocationLat = None
        mock_row.StartLocationLong = None
        mock_row.EndLocationLat = None
        mock_row.EndLocationLong = None
        mock_row.TotalDistance = 5.0
        mock_row.TotalSteps = 10000
        mock_row.CaloriesBurned = 500

        mock_query_job.result.return_value = [mock_row]
        mock_instance.query.return_value = mock_query_job

        result = get_user_workouts("user1")  # No second argument

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start_timestamp"], "2024-07-29 07:00:00")
        self.assertIsNone(result[0]["end_timestamp"])
        self.assertIsNone(result[0]["start_lat_lng"])
        self.assertIsNone(result[0]["end_lat_lng"])


class TestGetGenAIAdvice(unittest.TestCase):

    @patch("data_fetcher.bigquery.Client")
    @patch("data_fetcher.model.generate_content")
    def test_valid_workout_data(self, mock_generate_content, mock_client):
        """Test generating advice with valid workout data."""
        mock_instance = mock_client.return_value
        mock_query_job = MagicMock()

        mock_row = MagicMock()
        mock_row.TotalDistance = 5.0
        mock_row.TotalSteps = 8000
        mock_row.CaloriesBurned = 400
        mock_query_job.result.return_value.to_dataframe.return_value = [mock_row]

        mock_instance.query.return_value = mock_query_job
        mock_generate_content.return_value.text = "Keep it up! Stay hydrated."

        result = get_genai_advice("user1")

        self.assertIn("advice_id", result)
        self.assertIn("timestamp", result)
        self.assertEqual(result["content"], "Keep it up! Stay hydrated.")
        self.assertIn("image", result)

    @patch("data_fetcher.bigquery.Client")
    @patch("data_fetcher.model.generate_content")
    def test_no_workout_data(self, mock_generate_content, mock_client):
        """Test generating advice when no workout data is available."""
        mock_instance = mock_client.return_value
        mock_query_job = MagicMock()
        mock_query_job.result.return_value.to_dataframe.return_value = []

        mock_instance.query.return_value = mock_query_job

        mock_generate_content.return_value.text = "Without knowing the actual numerical values, I can provide general advice."

        result = get_genai_advice("user_no_data")

        self.assertEqual(result["content"], "Without knowing the actual numerical values, I can provide general advice.")

class TestGetPosts(unittest.TestCase):

    @patch("data_fetcher.bigquery.Client")  
    def test_valid_post(self, mock_client):
        """Test fetching valid workout data."""
        mock_instance = mock_client.return_value
        mock_query_job = MagicMock()

        mock_row = MagicMock()
        mock_row.PostId = "post1"
        mock_row.AuthorId = "user1"
        mock_row.Timestamp = datetime(2024, 7, 29, 7, 0, 0)
        mock_row.Content = "This is a test post."
        mock_row.ImageUrl = "image_url"

        mock_query_job.result.return_value = [mock_row]
        mock_instance.query.return_value = mock_query_job

        result = get_user_posts("user1")  # No second argument

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["user_id"], "user1")
        self.assertEqual(result[0]["post_id"], "post1")
        self.assertEqual(result[0]["timestamp"], "2024-07-29 07:00:00")
        self.assertEqual(result[0]["content"], "This is a test post.")
        self.assertEqual(result[0]["image"], "image_url")

class TestGenAINutritionFeedback(unittest.TestCase):

    @patch("data_fetcher.bigquery.Client")
    @patch("data_fetcher.model.generate_content")
    def test_valid_nutrition_data(self, mock_generate_content, mock_bigquery_client):
        """Test feedback generation with valid nutrition data."""

        # Mock result row from BigQuery
        mock_row = MagicMock()
        mock_row.total_calories = 1300
        mock_row.total_protein = 40
        mock_row.total_fats = 30
        mock_row.total_carbs = 50

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = iter([mock_row])
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        mock_generate_content.return_value.text = "Good job! Your macros look balanced overall."

        feedback = get_genai_nutrition_feedback("user1")

        self.assertIn("feedback_id", feedback)
        self.assertIn("timestamp", feedback)
        self.assertIn("content", feedback)
        self.assertEqual(feedback["content"], "Good job! Your macros look balanced overall.")

    @patch("data_fetcher.bigquery.Client")
    @patch("data_fetcher.model.generate_content")
    def test_no_nutrition_data(self, mock_generate_content, mock_bigquery_client):
        """Test when no nutrition data is available for today."""

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = iter([])
        mock_bigquery_client.return_value.query.return_value = mock_query_job

        feedback = get_genai_nutrition_feedback("user1")

        self.assertEqual(feedback["content"], "No nutrition data found for today. Try logging your meals!")
        self.assertIsNone(feedback["image"])

    def test_empty_user_id(self):
        """Test with missing user ID."""
        with self.assertRaises(ValueError):
            get_genai_nutrition_feedback("")

class TestGetUserWorkoutsByDate(unittest.TestCase):
    
    @patch("data_fetcher.bigquery.Client")
    def test_workouts_in_date_range(self, mock_client_cls):
        """Test fetching workouts filtered by date range."""
        mock_client = mock_client_cls.return_value
        mock_query_job = MagicMock()

        mock_row = MagicMock()
        mock_row.WorkoutId = "workout1"
        mock_row.StartTimestamp = datetime(2024, 7, 29, 7, 0, 0)
        mock_row.EndTimestamp = datetime(2024, 7, 29, 8, 0, 0)
        mock_row.StartLocationLat = 34.0522
        mock_row.StartLocationLong = -118.2437
        mock_row.EndLocationLat = 34.0523
        mock_row.EndLocationLong = -118.2438
        mock_row.TotalDistance = 5.0
        mock_row.TotalSteps = 10000
        mock_row.CaloriesBurned = 500

        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        from data_fetcher import get_user_workouts_by_date

        result = get_user_workouts_by_date("user1", "2024-07-01", "2024-07-31")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["workout_id"], "workout1")
        self.assertEqual(result[0]["start_timestamp"], "2024-07-29T07:00:00")
        self.assertEqual(result[0]["end_timestamp"], "2024-07-29T08:00:00")
        self.assertEqual(result[0]["start_lat_lng"], (34.0522, -118.2437))
        self.assertEqual(result[0]["end_lat_lng"], (34.0523, -118.2438))
        self.assertEqual(result[0]["distance"], 5.0)
        self.assertEqual(result[0]["steps"], 10000)
        self.assertEqual(result[0]["calories_burned"], 500)

    @patch("data_fetcher.bigquery.Client")
    def test_no_workouts_in_range(self, mock_client_cls):
        """Test when no workouts fall in the given range."""
        mock_client = mock_client_cls.return_value
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []

        mock_client.query.return_value = mock_query_job

        from data_fetcher import get_user_workouts_by_date
        result = get_user_workouts_by_date("user1", "2024-07-01", "2024-07-02")

        self.assertEqual(result, [])

class TestGetUserTodayCalorieTracking(unittest.TestCase):

    @patch("data_fetcher.bigquery.Client")
    def test_no_meal_data(self, mock_bigquery_client):
        """Test when no calorie tracking data is available for today."""
        mock_instance = mock_bigquery_client.return_value
        mock_query_job = MagicMock()
        
        mock_query_job.result.return_value = []
        mock_instance.query.return_value = mock_query_job

        result = get_user_today_calorie_tracking("user_with_no_meal_data")
        
        self.assertEqual(result, [])

    @patch("data_fetcher.bigquery.Client")
    def test_one_meal_data(self, mock_bigquery_client):
        """Test fetching valid calorie tracking data for today."""
        mock_instance = mock_bigquery_client.return_value
        mock_query_job = MagicMock()

        mock_row = MagicMock()
        mock_row.MealId = "meal1"
        mock_row.UserId = "user1"
        mock_row.MealName = "Oatmeal"
        mock_row.Calories = 300
        mock_row.Protein = 10
        mock_row.Carbs = 50
        mock_row.Fats = 9
        mock_row.MealDate = datetime(2025, 7, 29, 7)
        mock_row.CreatedAt = datetime(2025, 7, 29, 7, 0, 0)

        mock_query_job.result.return_value = [mock_row]
        mock_instance.query.return_value = mock_query_job

        result = get_user_today_calorie_tracking("user1")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["meal_id"], "meal1")
        self.assertEqual(result[0]["user_id"], "user1")
        self.assertEqual(result[0]["meal_name"], "Oatmeal")
        self.assertEqual(result[0]["calories"], 300)
        self.assertEqual(result[0]["protein"], 10)
        self.assertEqual(result[0]["carbs"], 50)
        self.assertEqual(result[0]["fat"], 9)
        self.assertEqual(result[0]["date"], "2025-07-29")
        self.assertEqual(result[0]["created_at"], "2025-07-29 07:00:00")

    @patch("data_fetcher.bigquery.Client")
    def test_multiple_meal_data(self, mock_bigquery_client):
        """Test fetching valid calorie tracking data for today."""
        mock_instance = mock_bigquery_client.return_value
        mock_query_job = MagicMock()

        mock_row1 = MagicMock()
        mock_row1.MealId = "meal1"
        mock_row1.UserId = "user1"
        mock_row1.MealName = "Oatmeal"
        mock_row1.Calories = 300
        mock_row1.Protein = 10
        mock_row1.Carbs = 50
        mock_row1.Fats = 9
        mock_row1.MealDate = datetime(2025, 7, 29, 7)
        mock_row1.CreatedAt = datetime(2025, 7, 29, 7, 0, 0)

        mock_row2 = MagicMock()
        mock_row2.MealId = "meal2"
        mock_row2.UserId = "user1"
        mock_row2.MealName = "Taco Salad"
        mock_row2.Calories = 800
        mock_row2.Protein = 10
        mock_row2.Carbs = 40
        mock_row2.Fats = 13
        mock_row2.MealDate = datetime(2025, 7, 29, 12)
        mock_row2.CreatedAt = datetime(2025, 7, 29, 12, 0, 0)

        mock_query_job.result.return_value = [mock_row1, mock_row2]
        mock_instance.query.return_value = mock_query_job

        result = get_user_today_calorie_tracking("user1")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["meal_id"], "meal1")
        self.assertEqual(result[0]["user_id"], "user1")
        self.assertEqual(result[0]["meal_name"], "Oatmeal")
        self.assertEqual(result[0]["calories"], 300)
        self.assertEqual(result[0]["protein"], 10)
        self.assertEqual(result[0]["carbs"], 50)
        self.assertEqual(result[0]["fat"], 9)
        self.assertEqual(result[0]["date"], "2025-07-29")
        self.assertEqual(result[0]["created_at"], "2025-07-29 07:00:00")

        self.assertEqual(result[1]["meal_id"], "meal2")
        self.assertEqual(result[1]["user_id"], "user1")
        self.assertEqual(result[1]["meal_name"], "Taco Salad")
        self.assertEqual(result[1]["calories"], 800)
        self.assertEqual(result[1]["protein"], 10)
        self.assertEqual(result[1]["carbs"], 40)
        self.assertEqual(result[1]["fat"], 13)
        self.assertEqual(result[1]["date"], "2025-07-29")
        self.assertEqual(result[1]["created_at"], "2025-07-29 12:00:00")

        
        
        

    
        



class TestGetUserWeeklyCalorieSummary(unittest.TestCase):
    @patch("data_fetcher.bigquery.Client")
    def test_weekly_summary_valid(self, mock_client_cls):
        """Test summary with valid weekly meal data."""
        mock_client = mock_client_cls.return_value
        mock_query_job = MagicMock()

        # Mock row return
        mock_row = MagicMock()
        mock_row.MealDate = datetime(2025, 4, 20).date()
        mock_row.total_calories = 1200.0
        mock_row.total_protein = 45.0
        mock_row.total_fats = 35.0
        mock_row.total_carbs = 60.0

        mock_query_job.to_dataframe.return_value = [
            {
                "MealDate": mock_row.MealDate,
                "total_calories": mock_row.total_calories,
                "total_protein": mock_row.total_protein,
                "total_fats": mock_row.total_fats,
                "total_carbs": mock_row.total_carbs
            }
        ]
        mock_client.query.return_value = mock_query_job

        df = get_user_weekly_calorie_summary("user1")

        self.assertEqual(len(df), 1)
        self.assertEqual(df[0]["MealDate"], datetime(2025, 4, 20).date())
        self.assertEqual(df[0]["total_calories"], 1200.0)
        self.assertEqual(df[0]["total_protein"], 45.0)
        self.assertEqual(df[0]["total_fats"], 35.0)
        self.assertEqual(df[0]["total_carbs"], 60.0)

    @patch("data_fetcher.bigquery.Client")
    def test_no_data_returned(self, mock_client_cls):
        """Test when no meals are recorded for the past 7 days."""
        mock_client = mock_client_cls.return_value
        mock_query_job = MagicMock()

        mock_query_job.to_dataframe.return_value = []
        mock_client.query.return_value = mock_query_job

        df = get_user_weekly_calorie_summary("user1")
        self.assertEqual(df, [])

if __name__ == "__main__":
    unittest.main()
