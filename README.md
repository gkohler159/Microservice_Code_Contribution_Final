The date_service.py microservice and the test_server is a basic implementation of the Microservice for the Kanban board that will assign urgency to dates. 

To RUN: 
python data_service.py: 
This program auto runs on its own. Logging is included for any troubleshooting. This is the automated service

python test_server.py
This program helps to test the data_service.py as a separate server. The user will need to follow the prompts as follows:
card_id: Any given id 
date: Must be in the format of "2025-08-04T15:55:00"
options (1 or 2): 1 will add a new card, 2 will obtain the due date


