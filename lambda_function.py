import boto3
import requests
import base64
import json
import datetime

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response

# Setup the SSM client
ssm = boto3.client('ssm')

def get_parameter(name):
    #Retrieve parameter from SSM Parameter Store
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

def update_parameter(name, value):
    """Update parameter in SSM Parameter Store"""
    ssm.put_parameter(Name=name, Value=value, Type='String', Overwrite=True)

def refresh_credentials(client_id, client_secret, refresh_token):
    """Refresh Fitbit token using refresh_token"""
    encoded_credentials = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post('https://api.fitbit.com/oauth2/token', headers=headers, data=data)
    return response.json()

def get_meal_type_id(current_hour):
    if 6 <= current_hour < 11:
        return 1  # Breakfast
    elif 11 <= current_hour < 12:
        return 2  # Morning Snack
    elif 12 <= current_hour < 16:
        return 3  # Lunch
    elif 16 <= current_hour < 18:
        return 4  # Afternoon Snack
    elif 18 <= current_hour < 21:
        return 5  # Dinner
    else:
        return 6  # Anytime

def food_logger(food_item):
    # Retrieve tokens and credentials from SSM Parameter Store
    access_token = get_parameter('FITBIT_ACCESS_TOKEN')
    refresh_token = get_parameter('FITBIT_REFRESH_TOKEN')
    client_id = get_parameter('FITBIT_CLIENT_ID')
    client_secret = get_parameter('FITBIT_CLIENT_SECRET')

    # Use access token to make Fitbit API request
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.fitbit.com/1/user/-/profile.json', headers=headers)

    # Check if the access token needs to be refreshed
    if response.status_code == 401:  # Unauthorized
        # Refresh the tokens
        refreshed_tokens = refresh_credentials(client_id, client_secret, refresh_token)
        access_token = refreshed_tokens.get('access_token')
        refresh_token = refreshed_tokens.get('refresh_token')

        # Update tokens in SSM Parameter Store
        update_parameter('FITBIT_ACCESS_TOKEN', access_token)
        update_parameter('FITBIT_REFRESH_TOKEN', refresh_token)

        # Retry the Fitbit API request with the new access token
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.fitbit.com/1/user/-/profile.json', headers=headers)

    # Call the Fitbit API to search for the food item and log it
    try:
        access_token = access_token # Set your access token as an environment variable in Lambda
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Example: Search for the food item (you need to handle pagination and selecting the correct item)
        search_endpoint = f"https://api.fitbit.com/1/foods/search.json?query={food_item}"
        search_response = requests.get(search_endpoint, headers=headers)
        if search_response.status_code == 200:
            search_results = search_response.json()
            
            # Get the list of foods from the JSON response
            foods = search_results.get('foods')
            
            if foods and len(foods) > 0:
                # Get and print the first food item
                first_food = foods[0]
                food_id = first_food.get('foodId')
                print(first_food)
        
                # Get current date and time
                now = datetime.datetime.now()
                today_date = now.strftime('%Y-%m-%d')
                current_hour = now.hour
                
                # Set up the data for the food log
                food_log_data = {
                    "foodId": food_id,
                    "mealTypeId": get_meal_type_id(current_hour),
                    "unitId": first_food.get('defaultUnit').get('id'),
                    "amount": 1,
                    "date": today_date
                }
                
                # Convert the data dictionary to URL parameters
                params = "&".join(f"{key}={value}" for key, value in food_log_data.items())
                
                # Construct the endpoint with the parameters in the URL
                log_endpoint = f"https://api.fitbit.com/1/user/-/foods/log.json?{params}"
                
                # Make the POST request to log the food
                log_response = requests.post(log_endpoint, headers=headers)
                print(log_response.json())
                
                if log_response.status_code == 201:
                    print("Food logged successfully!")
                    return {
                        'statusCode': 200,
                        'body': 'Food logged successfully'  # Adjust this based on actual operation result
                    }
                else:
                    print(f"Failed to log food with status code: {log_response.statusCode}")
                    print(log_response.text)
                    speak_output = "Evil forces are stopping me from logging your food!"
                    # Ask for the food item and keep the session open
                    return {
                        'statusCode': 400
                    }
            else:
                print(f"No foods found for query: {food_item}")
                speak_output = "Mischievous forces are stopping me from finding that food!"
                return handler_input.response_builder.speak(speak_output).ask(speak_output).response
        else:
            print(f"Error with status code: {search_response.status_code}")
            print(search_response.text)
            speak_output = "I cant communicate with the food log. Someone must be trying to stop us."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

    except Exception as e:
        print(f"Error: {e}")
        # Handle the exception appropriately

    return {
        'statusCode': 200,
        'body': 'Food logged successfully'  # Adjust this based on actual operation result
    }

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Check if the request is of type LaunchRequest
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # Provide a welcome message
        speak_output = "Welcome to Nick Ate! What did Nick Eat?"
        # Ask for the food item and keep the session open
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class LogFoodIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LogFoodIntent")(handler_input)

    def handle(self, handler_input):
        food_item = handler_input.request_envelope.request.intent.slots["FoodItem"].value
        # Call your existing logic to log the food item to Fitbit here
        
        status = food_logger(food_item)
        print(status)

        if status["statusCode"] == 200:
            speech_text = f"Wicked! Logged that {food_item} to Fitbit!"
        else:
            speech_text = f"Evil forces are stopping me from logging your food!"
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        return handler_input.response_builder.response

# StopIntentHandler Class
class StopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Check if the intent name is AMAZON.StopIntent
        return is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # Provide a farewell message
        speak_output = "Thanks. Keep me posted on what you eat."
        # End the session and close the skill
        return handler_input.response_builder.speak(speak_output).set_should_end_session(True).response

# CancelIntentHandler Class
class CancelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Check if the intent name is AMAZON.CancelIntent
        return is_intent_name("AMAZON.CancelIntent")(handler_input)

    def handle(self, handler_input):
        # Provide a farewell message
        speak_output = "Come back when you have more food to tell me about!"
        # End the session and close the skill
        return handler_input.response_builder.speak(speak_output).set_should_end_session(True).response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(LogFoodIntentHandler())

lambda_handler = sb.lambda_handler()