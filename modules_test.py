#############################################################################
# modules_test.py
#
# This file contains tests for modules.py and app.py
#
# You will write these tests in Unit 2.
#############################################################################


import unittest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, Mock, MagicMock, call
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts
from unittest.mock import patch, Mock, call
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts, display_filtered_workouts, display_weekly_calorie_summary, display_macro_calorie_chart
import altair as alt
import pandas as pd

# Write your tests below


# Function written in part with ChatGPT
# Prompt: "write robust streamlit testing for this function I have implemented, 
# knowing that other functions are still meant to be implemented".
# https://chatgpt.com/share/67cb8b94-4ac0-8005-88e6-142af3dcb082
class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    @patch("streamlit.write", new_callable=Mock)
    @patch("streamlit.subheader", new_callable=Mock)
    @patch("streamlit.columns", new_callable=MagicMock)
    @patch("streamlit.container", new_callable=MagicMock)
    @patch("streamlit.metric", new_callable=Mock)
    @patch("streamlit.line_chart", new_callable=Mock)
    @patch("streamlit.bar_chart", new_callable=Mock)
    @patch("streamlit.divider", new_callable=Mock)
    @patch("streamlit.markdown", new_callable=Mock)
    @patch("data_fetcher.get_user_workouts")
    def test_empty_workouts(
        self,
        mock_get_user_workouts,
        mock_markdown,
        mock_divider,
        mock_bar_chart,
        mock_line_chart,
        mock_metric,
        mock_container,
        mock_columns,
        mock_subheader,
        mock_write
    ):
        mock_get_user_workouts.return_value = []

        app = AppTest.from_file("app.py")
        app.run(timeout=10)  # give it time in case it's slow

        mock_write.assert_any_call("No workouts found.")
        mock_get_user_workouts.assert_called_once_with('user1')

        
    @patch('streamlit.write')
    @patch('streamlit.markdown')
    @patch('data_fetcher.get_user_workouts')
    def test_single_workout(self, mock_get_user_workouts, mock_markdown, mock_write):
        mock_get_user_workouts.return_value = [{
            'workout_id': '123',
            'start_timestamp': '2023-10-26 10:00',
            'end_timestamp': '2023-10-26 11:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500
        }]

        app = AppTest.from_file("app.py")
        app.run()
        
        mock_markdown.assert_any_call("**Workout ID:** 123")
        mock_write.assert_any_call("📅 **Start Time:** 2023-10-26 10:00")
        mock_write.assert_any_call("🏁 **End Time:** 2023-10-26 11:00")
        mock_write.assert_any_call("📏 **Distance:** 5.0 km")
        mock_write.assert_any_call("🚶 **Steps:** 10000")
        mock_write.assert_any_call("🔥 **Calories Burned:** 500 kcal")

        mock_get_user_workouts.assert_called_once()

    @patch('streamlit.write')
    @patch('streamlit.markdown')
    @patch('data_fetcher.get_user_workouts')
    def test_multiple_workouts(self, mock_get_user_workouts, mock_markdown, mock_write):
        mock_get_user_workouts.return_value = [
            {
                'workout_id': '1',
                'start_timestamp': '2023-10-26 10:00',
                'end_timestamp': '2023-10-26 11:00',
                'distance': 5.0,
                'steps': 10000,
                'calories_burned': 500,
            },
            {
                'workout_id': '2',
                'start_timestamp': '2023-10-27 10:00',
                'end_timestamp': '2023-10-27 11:00',
                'distance': 3.0,
                'steps': 6000,
                'calories_burned': 300,
            },
        ]

        app = AppTest.from_file("app.py")
        app.run()
        
        mock_markdown.assert_any_call("**Workout ID:** 1")
        mock_markdown.assert_any_call("**Workout ID:** 2")
        mock_write.assert_any_call("📅 **Start Time:** 2023-10-26 10:00")
        mock_write.assert_any_call("🏁 **End Time:** 2023-10-26 11:00")
        mock_write.assert_any_call("📏 **Distance:** 5.0 km")
        mock_write.assert_any_call("🚶 **Steps:** 10000")
        mock_write.assert_any_call("🔥 **Calories Burned:** 500 kcal")
        mock_write.assert_any_call("📅 **Start Time:** 2023-10-27 10:00")
        mock_write.assert_any_call("🏁 **End Time:** 2023-10-27 11:00")
        mock_write.assert_any_call("📏 **Distance:** 3.0 km")
        mock_write.assert_any_call("🚶 **Steps:** 6000")
        mock_write.assert_any_call("🔥 **Calories Burned:** 300 kcal")

        mock_get_user_workouts.assert_called_once()


    @patch('streamlit.write')
    @patch('data_fetcher.get_user_workouts')
    def test_missing_data(self, mock_get_user_workouts, mock_write):
        mock_get_user_workouts.return_value = [
            {
                'workout_id': '123',
                'start_timestamp': '2023-10-26 10:00',
                'end_timestamp': '2023-10-26 11:00',
                'distance': 5.0,
                'steps': 10000,
                'calories_burned': 500
            },
            {
                'workout_id': '456',
                'start_timestamp': '2023-10-27 10:00',
                'end_timestamp': '2023-10-27 11:00',
                'distance': 3.0,
                'steps': 6000,
            }
        ]

        app = AppTest.from_file("app.py")
        app.run()

        mock_write.assert_any_call("Cannot display chart data with missing values.")
        mock_get_user_workouts.assert_called_once()
        
class TestDisplayGenaiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    @patch("streamlit.header")
    @patch("streamlit.image")
    @patch("streamlit.write")
    def test_display_genai_advice_with_image(self, mock_write, mock_image, mock_header):
        """Test when an image is provided, using mock dependencies."""
        
        # Mock data
        timestamp = "2024-01-01 00:00:00"
        content = "You're doing great! Keep up the good work."
        image = "https://plus.unsplash.com/premium_photo-1669048780129.jpg"

        # Call function directly
        display_genai_advice(timestamp, content, image)

        # Check if header is called
        mock_header.assert_called_once_with("Gen AI ADVICE")

        # Check if expected content is written
        written_args = [call_args.args[0] for call_args in mock_write.call_args_list]
        self.assertIn(f"timestamp : {timestamp}", written_args)
        self.assertIn(f"content: {content}", written_args)

        # Ensure image is displayed
        mock_image.assert_called()

    @patch("streamlit.header")
    @patch("streamlit.image")
    @patch("streamlit.write")
    def test_display_genai_advice_no_image(self, mock_write, mock_image, mock_header):
        """Test when no image is provided."""
        
        # Mock data
        timestamp = "2024-01-01 00:00:00"
        content = "You're doing great! Keep up the good work."
        image = None

        # Call function directly
        display_genai_advice(timestamp, content, image)

        # Check if header is called
        mock_header.assert_called_once_with("Gen AI ADVICE")

        # Check if expected content is written
        written_args = [call_args.args[0] for call_args in mock_write.call_args_list]
        self.assertIn(f"timestamp : {timestamp}", written_args)
        self.assertIn(f"content: {content}", written_args)
        self.assertIn("No image to be displayed", written_args)

        # Ensure image is NOT displayed
        mock_image.assert_not_called()

    @patch("streamlit.write")
    def test_display_genai_advice_timestamp(self, mock_write):
        """Test if timestamp is displayed properly."""
        
        # Mock data
        timestamp = "2024-03-26 10:00:00"
        content = "This is a test content."
        image = None

        # Call function directly
        display_genai_advice(timestamp, content, image)

        # Check if timestamp is written
        written_args = [call_args.args[0] for call_args in mock_write.call_args_list]
        self.assertIn(f"timestamp : {timestamp}", written_args)

    @patch("streamlit.write")
    def test_display_genai_advice_content(self, mock_write):
        """Test if content is displayed properly."""
        
        # Mock data
        timestamp = "2024-03-26 10:00:00"
        content = "This is a test content."
        image = None

        # Call function directly
        display_genai_advice(timestamp, content, image)

        # Check if content is written
        written_args = [call_args.args[0] for call_args in mock_write.call_args_list]
        self.assertIn(f"content: {content}", written_args)
    
        

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    @patch("streamlit.text", new_callable=Mock)
    @patch("streamlit.subheader", new_callable=Mock)
    @patch("streamlit.container", new_callable=MagicMock)
    @patch("streamlit.columns", new_callable=MagicMock)
    @patch("data_fetcher.get_user_workouts")
    def test_empty_workout_list(
        self,
        mock_get_user_workouts,
        mock_columns,
        mock_container,
        mock_subheader,
        mock_text
    ):
        """Test that message is shown when no workouts exist."""
        mock_get_user_workouts.return_value = []
        mock_columns.return_value = [Mock(), Mock(), Mock()]

        app = AppTest.from_file("app.py")
        app.run(timeout=10)

        mock_text.assert_called_once_with("No workouts to display.")
        mock_get_user_workouts.assert_called_once()

    @patch("streamlit.write", new_callable=Mock)
    @patch("streamlit.subheader", new_callable=Mock)
    @patch("streamlit.container", new_callable=MagicMock)
    @patch("streamlit.columns", new_callable=MagicMock)
    @patch("data_fetcher.get_user_workouts")
    def test_non_empty_workout_list(
        self,
        mock_get_user_workouts,
        mock_columns,
        mock_container,
        mock_subheader,
        mock_write
    ):
        """Test when one workout is present."""
        mock_get_user_workouts.return_value = [{
            'start_timestamp': '2024-10-26T10:00:00',
            'end_timestamp': '2024-10-26T11:00:00',
            'distance': 3.5,
            'steps': 5000,
            'calories_burned': 300,
            'start_lat_lng': '(34.0522, -118.2437)',
            'end_lat_lng': '(34.0522, -118.2437)'
        }]

        # Mock return from st.columns
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

        app = AppTest.from_file("app.py")
        app.run(timeout=10)

        expected_calls = [
            call("Workout Date: 2024-10-26"),
            call("Workout Start Time: 10:00:00"),
            call("Workout End Time: 11:00:00"),
            call("Distance: 3.5 miles"),
            call("Steps: 5000"),
            call("Calories Burned: 300"),
            call("Start Location: (34.0522, -118.2437)"),
            call("End Location: (34.0522, -118.2437)")
        ]

        mock_write.assert_has_calls(expected_calls, any_order=False)
        mock_get_user_workouts.assert_called_once()



class TestDisplayPost(unittest.TestCase):
    #I used gemini to generate some of this code
    @patch('streamlit.image')
    @patch('streamlit.write')
    @patch('streamlit.markdown')
    @patch('streamlit.caption')
    def test_display_post_loads_properly(self, mock_caption, mock_markdown, mock_write, mock_image):
        """Test if display_post loads properly with valid data."""
        # Mock data
        username = 'remi_the_rems'
        user_image = 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg'
        timestamp = '2024-01-01 00:00:00'
        content = "great workout"
        post_image = None

        # Call function directly
        display_post(username, user_image, timestamp, content, post_image)

        # Check if image is called with correct arguments
        mock_image.assert_called_once_with(user_image, width=50)

        # Check if markdown is called with correct arguments
        mock_markdown.assert_called_with("---")

        # Check if caption is called with correct arguments
        mock_caption.assert_called_with(timestamp)

        # Check if write is called with correct arguments
        mock_write.assert_called_with(content)

    

class TestDisplayFilteredWorkouts(unittest.TestCase):
    """Tests the display_filtered_workouts function directly."""

    @patch("streamlit.info")
    def test_empty_filtered_workouts(self, mock_info):
        """Should show info message when no workouts found."""
        from modules import display_filtered_workouts

        # Empty list simulates no filtered workouts
        display_filtered_workouts([])

        mock_info.assert_called_once_with("No workout found during this time")

    @patch("streamlit.subheader")
    @patch("streamlit.write")
    def test_filtered_workout_display(self, mock_write, mock_subheader):
        """Should render all filtered workout data correctly."""
        from modules import display_filtered_workouts

        workout_data = [{
            'workout_id': 'w001',
            'start_timestamp': '2024-10-20T07:00:00',
            'end_timestamp': '2024-10-20T08:00:00',
            'distance': 5.0,
            'steps': 8500,
            'calories_burned': 400,
            'start_lat_lng': (36.12, -86.67),
            'end_lat_lng': (36.13, -86.68)
        }]

        display_filtered_workouts(workout_data)

        expected_calls = [
            call("🆔 **ID:** w001"),
            call("🕒 **Start:** 2024-10-20T07:00:00"),
            call("🏁 **End:** 2024-10-20T08:00:00"),
            call("📏 **Distance:** 5.0 miles"),
            call("🚶 **Steps:** 8500"),
            call("🔥 **Calories:** 400 kcal"),
            call("📍 **Start Location:** (36.12, -86.67)"),
            call("📍 **End Location:** (36.13, -86.68)"),
        ]

        for expected in expected_calls:
            self.assertIn(expected, mock_write.call_args_list)

        mock_subheader.assert_any_call("Filtered Workouts")


class TestDisplayWeeklyCalorieSummary(unittest.TestCase):
    """Tests the display_weekly_calorie_summary function."""

    @patch("streamlit.info")
    def test_empty_dataframe(self, mock_info):
        """Should show info message when no data is present."""
        df = pd.DataFrame()
        display_weekly_calorie_summary(df)
        mock_info.assert_called_once_with("No meal data available for the past week.")

    @patch("streamlit.altair_chart")
    @patch("streamlit.dataframe")
    @patch("streamlit.subheader")
    def test_valid_dataframe(self, mock_subheader, mock_dataframe, mock_altair_chart):
        """Should render bar chart and table with valid data."""
        data = {
            'MealDate': ['2025-04-19', '2025-04-20'],
            'total_calories': [400, 600],
            'total_protein': [30, 40],
            'total_fats': [10, 20],
            'total_carbs': [50, 60]
        }
        df = pd.DataFrame(data)

        display_weekly_calorie_summary(df)

        mock_subheader.assert_called_once_with("📊 Weekly Calorie & Macro Summary")
        mock_dataframe.assert_called_once_with(df)
        mock_altair_chart.assert_called_once()

class TestDisplayMacroCalorieChart(unittest.TestCase):
    """Tests the display_macro_calorie_chart function."""

    @patch("streamlit.subheader")
    @patch("streamlit.table")
    @patch("streamlit.write")
    def test_empty_meal_list(self, mock_write, mock_dataframe, mock_subheader):
        """Should show info message when no data is present."""
        df = pd.DataFrame()
        display_macro_calorie_chart(df)

        mock_subheader.assert_not_called()
        mock_write.assert_called_once_with("No meal data")
        mock_dataframe.assert_not_called()

    #Asked Gemini how to write tests for dataframes
    @patch("streamlit.subheader")
    @patch("streamlit.table")
    @patch("streamlit.write")
    def test_single_meal_list(self, mock_write, mock_dataframe, mock_subheader):
        """Should render table with valid data."""
        meal_list = [{'meal_name': 'Breakfast', 'calories': 300, 'protein': 20, 'carbs': 40, 'fat': 10}]
        display_macro_calorie_chart(meal_list)

        mock_subheader.assert_called_once_with("Today's Meals")
        mock_write.assert_not_called()
        args, _ = mock_dataframe.call_args
        displayed_df = args[0]
        self.assertIsInstance(displayed_df, pd.DataFrame)
        self.assertEqual(displayed_df.shape, (2, 5))  # 1 meal + 1 total row
        self.assertEqual(displayed_df.iloc[0]['Meal'], 'Breakfast')
        self.assertEqual(displayed_df.iloc[0]['Calories'], 300)
        self.assertEqual(displayed_df.iloc[0]['Protein'], 20)
        self.assertEqual(displayed_df.iloc[0]['Carbs'], 40)
        self.assertEqual(displayed_df.iloc[0]['Fats'], 10)
        self.assertEqual(displayed_df.iloc[1]['Meal'], 'Total')
        self.assertEqual(displayed_df.iloc[1]['Calories'], 300)
        self.assertEqual(displayed_df.iloc[1]['Protein'], 20)
        self.assertEqual(displayed_df.iloc[1]['Carbs'], 40)
        self.assertEqual(displayed_df.iloc[1]['Fats'], 10)
        
    @patch("streamlit.subheader")
    @patch("streamlit.table")
    @patch("streamlit.write")
    def test_multiple_meal_list(self, mock_write, mock_dataframe, mock_subheader):
        """Should render table with valid data."""
        meal_list = [
            {'meal_name': 'Breakfast', 'calories': 300, 'protein': 20, 'carbs': 40, 'fat': 10},
            {'meal_name': 'Lunch', 'calories': 500, 'protein': 30, 'carbs': 60, 'fat': 20},
            {'meal_name': 'Snack', 'calories': 150, 'protein': 5, 'carbs': 15, 'fat': 5}
        ]        
        
        display_macro_calorie_chart(meal_list)

        mock_subheader.assert_called_once_with("Today's Meals")
        mock_write.assert_not_called()
        args, _ = mock_dataframe.call_args
        displayed_df = args[0]
        self.assertIsInstance(displayed_df, pd.DataFrame)
        self.assertEqual(displayed_df.shape, (4, 5))  # 1 meal + 1 total row
        self.assertEqual(displayed_df.iloc[0]['Meal'], 'Breakfast')
        self.assertEqual(displayed_df.iloc[0]['Calories'], 300)
        self.assertEqual(displayed_df.iloc[0]['Protein'], 20)
        self.assertEqual(displayed_df.iloc[0]['Carbs'], 40)
        self.assertEqual(displayed_df.iloc[0]['Fats'], 10)
        self.assertEqual(displayed_df.iloc[1]['Meal'], 'Lunch')
        self.assertEqual(displayed_df.iloc[1]['Calories'], 500)
        self.assertEqual(displayed_df.iloc[1]['Protein'], 30)
        self.assertEqual(displayed_df.iloc[1]['Carbs'], 60)
        self.assertEqual(displayed_df.iloc[1]['Fats'], 20)
        self.assertEqual(displayed_df.iloc[2]['Meal'], 'Snack')
        self.assertEqual(displayed_df.iloc[2]['Calories'], 150)
        self.assertEqual(displayed_df.iloc[2]['Protein'], 5)
        self.assertEqual(displayed_df.iloc[2]['Carbs'], 15)
        self.assertEqual(displayed_df.iloc[2]['Fats'], 5)
        self.assertEqual(displayed_df.iloc[3]['Meal'], 'Total')
        self.assertEqual(displayed_df.iloc[3]['Calories'], 300 + 500 + 150)
        self.assertEqual(displayed_df.iloc[3]['Protein'], 20 + 30 + 5)
        self.assertEqual(displayed_df.iloc[3]['Carbs'], 40 + 60 + 15)
        self.assertEqual(displayed_df.iloc[3]['Fats'], 10 + 20 + 5)

    @patch("streamlit.subheader")
    @patch("streamlit.table")
    @patch("streamlit.write")
    def test_missing_columns(self, mock_write, mock_dataframe, mock_subheader):
        """Test the function when the meal list has missing required columns."""
        meal_list = [{'name': 'Breakfast', 'cals': 300, 'p': 20, 'ch': 40}]
        display_macro_calorie_chart(meal_list)

        mock_subheader.assert_not_called()
        mock_dataframe.assert_not_called()
        mock_write.assert_not_called() 

    @patch("streamlit.subheader")
    @patch("streamlit.table")
    @patch("streamlit.write")
    def test_extra_columns(self, mock_write, mock_dataframe, mock_subheader):
        """Test the function with extra columns in the meal data."""
        meal_list = [{'meal_name': 'Breakfast', 'calories': 300, 'protein': 20, 'carbs': 40, 'fat': 10, 'sodium': 500}]
        display_macro_calorie_chart(meal_list)

        mock_subheader.assert_called_once_with("Today's Meals")
        args, _ = mock_dataframe.call_args
        displayed_df = args[0]
        self.assertIsInstance(displayed_df, pd.DataFrame)
        self.assertEqual(displayed_df.shape, (2, 5))
        self.assertTrue('Meal' in displayed_df.columns)
        self.assertTrue('Calories' in displayed_df.columns)
        self.assertTrue('Protein' in displayed_df.columns)
        self.assertTrue('Carbs' in displayed_df.columns)
        self.assertTrue('Fats' in displayed_df.columns)
        mock_write.assert_not_called()
    







if __name__ == "__main__":
    unittest.main()
