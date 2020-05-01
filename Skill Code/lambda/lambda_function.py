# -*- coding: utf-8 -*-                                 #
#                                                       #
#   Author : Krishnasis Mandal <krishnasis@hotmail.com> #
#                                                       #
#   Lambda function for Alexa Skill - Voice Worldwide   #
#                                                       #
#########################################################
# https://www.amazon.in/Krishnasis-Voice-Worldwide/dp/B081Z2P86D 

import logging
import ask_sdk_core.utils as ask_utils
import boto3
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Refer to documentation about the different Handlers in an Alexa Skill flow 

# Handler that will handle when the skill is first invoked
class LaunchRequestHandler(AbstractRequestHandler):
    
    # Tell in this handler, what is happening
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # Replace AWS ACCESS KEY and SECRET KEY with your own credentials
        client = boto3.client('dynamodb', aws_access_key_id = 'AWS_ACCESS_KEY_ID', aws_secret_access_key = 'AWS_SECRET_KEY', region_name = 'us-east-1')
        
        # Replace TableName with the name of the table that is storing the dialog  
        response = client.get_item(TableName = 'dialogs',Key = {'id':{'S':str(1)}})
        
        # Get the message from the table 
        last_message=response['Item']['dialog']['S']
        
        # Prompt the user to dictate this own message
        speak_output = "Hello! Welcome to Voice Worldwide!! The last person said, " + last_message
        speak_output += ". Now it is your turn to speak. Tell the world what you want to say!... Try saying : Tell everyone, you are the best"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



class RecordIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RecordIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Replace AWS ACCESS KEY and SECRET KEY with your own credentials
        client = boto3.client('dynamodb',aws_access_key_id='AWS_ACCESS_KEY_ID', aws_secret_access_key='AWS_SECRET_KEY', region_name='us-east-1')
        
        # Get slot value. Refer to documentation to know what is a slot. Basically it's a block in a sentence 
        # Tell the world {sentence} -- Something like this. 
        # The intent of the skill that records the message is triggered by Tell the world, and the {sentence} is what the user is saying
        user_sentence=ask_utils.get_slot_value(handler_input=handler_input, slot_name="sentence")
        
        # Insert into dynamodb - Pretty nifty, right?
        client.put_item(TableName='dialogs', Item={'id':{'S':'1'},'dialog':{'S':user_sentence}})
        
        # Response from Alexa after the message from user has been stored in the database. 
        speak_output = "I have told the world what you wanted to say.. Hope it was something nice!"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# What Alexa will say if the user asks for information about the skill
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "In this skill, you will hear what the person who invoked the skill before you had said, and you can then give your own input for the next person"
        speak_output +=" Say something nice to the world! Try saying : Tell everyone, you are the best"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Handler to handle the response / action when the user says stop or cancel 
class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # The message before the skill is closed
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# When a session with the user is over 
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

# What to do if Alexa doesn't understand.. happens a lot. 
class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Sorry, I don't understand " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

# Mother of all except blocks (in Alexa context!) 
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

# Add the individual handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(RecordIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler()) 

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()