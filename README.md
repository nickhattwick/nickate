Welcome to Nick Ate, an Alexa skill that allows you to log your food consumption to Fitbit if you like or will begrudgingly accept being called Nick. Due to potential Lambda costs if this somehow became popular, I'm providing steps to recreate this skill in your own dev environment and enjoy being called Nick and logging your food from the comfort of your own home. 

## How Nick Ate works
Enjoy a variety of conversation flows!
**Smooth sailing**
Nick: Alexa, open Nick Ate
Alexa: Welcome to Nick Ate! What did Nick Eat?
Nick: Nick ate a banana
Alexa: I found Banana, with a default serving size of 100 grams and 90 calories. Would you like me to log this item?
Nick: Yes
Alexa: Wicked! Logged that banana to Fitbit

**Master of numbers**
Nick: Alexa, open Nick Ate
Alexa: Welcome to Nick Ate! What did Nick Eat?
Nick: Nick ate a banana
Alexa: I found Banana, with a default serving size of 100 grams and 90 calories. Would you like me to log this item?
Nick: Update quantity to 2
Alexa: Wicked, logged 2.0 grams of Banana to Fitbit

**Lying in wait**
Nick: Alexa, open Nick Ate
Alexa: Welcome to Nick Ate! What did Nick Eat?
Nick: Nick ate a banana
Alexa: I found Banana, with a default serving size of 100 grams and 90 calories. Would you like me to log this item?
Nick: Next
Alexa: How about Banana, Raw, with a default serving size of 1 extra-small and 72 calories. Would you like me to log that instead?
Nick: Next
...

## Prerequisites

Before you begin, you'll need

- An AWS account
- An Amazon Developer account for creating Alexa skills
- A Fitbit developer account for creating a Fitbit app

### 1. Create a Fitbit App

1. Log in to your Fitbit developer account at dev.fitbit.com
2. Create a new Fitbit app and note down the client id and client secrets, generated for your Fitbit app, which will be required by the Lambda
3. Use the client id and client secret along with the url provided to retrieve your first access and refresh tokens

### 2. Store Fitbit Credentials in AWS Secrets Manager

1. In the AWS Management Console, navigate to AWS Secrets Manager.
2. Create new secrets for your Fitbit app.
3. Store the FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET, FITBIT_REFRESH_TOKEN, and FITBIT_ACCESS_TOKEN secret values in AWS Secrets Manager.

### 3. Create a deployment package for Lambda

1. Clone down this repository
2. Locally, pip install the requirements in requirements.txt
   `pip3 install -r requirements.txt -t .`
3. Create the deployment package
   `zip -r deployment_package.zip .`

### Create your Lambda function
1. In the AWS Management Console, navigate to AWS Lambda.
2. Create a new Lambda function.
3. Upload the deployment package created in section 3
4. Configure the Lambda function with appropriate permissions, such as Secrets Manager access and allow execution from Alexa.

### 4. Create an Alexa Skill

1. Log in to your Amazon Developer account.
2. Create a new Alexa skill called Nick Ate
3. Set the invocation name to "nick ate" or "Nick eight"
4. Configure the skill's interaction model providing the following intent handlers
   a. LogFoodIntent handler with a variable option for FoodItem and utterance examples like as "Nick ate {FoodItem}". Protip: Alexa mishears, so do both "ate" and "eight"
   b. ConfirmFoodIntent with example utterances like "yes" and "confirm"
   c. UpdateQuantityIntent with a variable of "quantity" and examples such as "Update quantity to {quantity}"
   d. SwitchFoodIntent with utterances like "next" or "wrong"
5. Set up the skill's endpoint to point to the AWS Lambda function you created earlier.
6. Build your Alexa skill in development
7. Test your Alexa skill in the Alexa Developer Console to ensure it works correctly.

### 5. Deploy and Test

1. Deploy your Alexa skill and Lambda function.
2. If your dev account and Alexa device use the same account, you should be able to use the skill on your device.

## Usage

So, what are you waiting for, deploy Nick Ate, log your food and enjoy your new name today.
