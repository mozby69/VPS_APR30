# import requests
# from datetime import datetime
# from pytz import timezone

# class CurrentTimeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         try:
#             # Fetch time from the API
#             response = requests.get('https://worldtimeapi.org/api/ip')
#             response.raise_for_status()
#             data = response.json()

#             # Get the time and convert it to the Philippine timezone
#             internet_time = data.get('datetime') or data.get('utc_datetime')
#             utc_time = datetime.strptime(internet_time, '%Y-%m-%dT%H:%M:%S.%f%z')
#             philippine_timezone = timezone('Asia/Manila')
#             philippine_time = utc_time.astimezone(philippine_timezone)

#             # Store the Philippine time in the request object
#             request.current_time = philippine_time

#         except requests.RequestException as e:
#             print(f"Failed to fetch internet time: {e}")
#             # Use current time if fetching internet time fails
#             request.current_time = datetime.now().replace(tzinfo=timezone('Asia/Manila'))

#         response = self.get_response(request)
#         return response





























# import requests
# from datetime import datetime
# from django.http import JsonResponse



# class CurrentTimeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         try:

#             response = requests.get('https://worldtimeapi.org/api/ip')
#             response.raise_for_status()
#             data = response.json()

#             internet_time = data.get('datetime') or data.get('utc_datetime')
#             request.current_time = datetime.strptime(internet_time, '%Y-%m-%dT%H:%M:%S.%f%z')

#             #print(f"Internet Time: {request.current_time}")
#         except requests.RequestException as e:
           
#             print(f"Failed to fetch internet time: {e}")
#             request.current_time = datetime.now()

#         response = self.get_response(request)
#         return response












import pytz
from datetime import datetime

class CurrentTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current naive datetime object
        now = datetime.now()

        # Set the timezone to Asia/Manila
        manila_timezone = pytz.timezone('Asia/Manila')

        # Localize the naive datetime object to Philippine timezone
        request.current_time = now.astimezone(manila_timezone)

        

        response = self.get_response(request)

        return response


