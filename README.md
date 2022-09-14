# Pidgeon

### ***See Store Screenshots at bottom of README***

The premise of this project is was to allow users to subscribe to a text bot (will be referred to as an ***"alert"*** in documentation) and receive daily text messages with information relevant to them. This is an entire fullstack CRUD project using multiple different software systems to function. The initial focus was around sharing COVID-19 daily statistics updates. 

<img width=20% src=https://user-images.githubusercontent.com/46686623/190029257-3e7c9a08-b140-4f3b-be8c-51143b4ffdad.png>

## How it works

### Tech Stack

* Backend: Python (Flask)
* Database: PostgreSQL
* Hosting: Heroku
* SMS: Twilio
* SMS Scheduling: Heroku Scheduler
* Frontend: Shopify
* Webcrawling: Selenium (headless Chromium)
* Subscription Management: Seal Subscriptions (Shopify app)
* Webhook management: Zapier
* User management:  Klaviyo

### Logic Flow

1. Users would select an alert via the Pidgeon Shopify store and make a purchase.
2. Shopify would then create an instance for the user and their purchase in the Shopify CRM.
3. This would trigger Seal Subscription to create an instance for the users subscription in the Seal system.
4. Shopify was connected to Klaviyo such that a new event in Shopify, such as an alert subscription, would be represented in Klaviyo system.
5. The creation of a subscription in Klaviyo would trigger a Webhook from Zapier to create entry in database.
6. Heroku would receive request for an alert subscription and send the user a "Welcome to Pidgeon" SMS.
7. Each aleart had a Heroku Scheduler setup to run daily, that would retrieve subscriptions from the database (users phone number's) for an alert. 
9. When the program would run, it would build the SMS with the retrieved data and send it to the user via a Twilio number.

***Note:*** A similar flow would occur when a user cancelled their subscription, but instead it would mark the subscription as ended. The user would continue to receive alerts until the end of their billing cycle.

### Design Descisions

I will give explanation for certain design descisions as it might not be obvious from the flow. 

* ***Seal subscription:*** Shopify doesn't natively handle subscription based products (at least not when the store was made). Hence it was required to use a third party service to handle subscriptions.
* ***Klaviyo:*** Although Shopify has webhooks, the webhooks didn't handle subscriptions or send the required information (phone number) from the subscriptions. However, the Klaviyo integration had a simple way of retrieving the information with minimal work. Thus I leveraged the Klaviyo infrastructure to take the subscription information and use it to trigger a Zapier webhook to send the required data in JSON to my Heroku/Flask backend.
* ***Zapier:*** Zapier allowed me to notify the backend when changes were made to subscriptions via Klaviyo and provided authetification for the webhooks.
* ***Shopify:*** I mainly focus on backend design and Shopify gave me the infrastructure to handle front-end, payments and subscriptions without needing any code. It was a great accelerator in the development process.


## Screenshots

Screenshots below are of the Pidgeon Shopify store. I did all designs using Figma. 

<img width="1512" alt="Screen Shot 2022-09-13 at 7 34 01 PM" src="https://user-images.githubusercontent.com/46686623/190029042-f96465a8-4f65-44dc-bc88-de593d196bff.png">

<img width="1504" alt="Screen Shot 2022-09-13 at 7 34 46 PM" src="https://user-images.githubusercontent.com/46686623/190029048-427a1ec1-677c-4b58-af5f-c48923cd9fca.png">

<img width="1471" alt="Screen Shot 2022-09-13 at 7 35 40 PM" src="https://user-images.githubusercontent.com/46686623/190029059-f0d8cd8d-d8d4-428e-b002-d7e6d95fdc96.png">
