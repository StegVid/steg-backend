import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware:
    """Middleware to log all requests and responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization
        self.request_count = 0
        
    def __call__(self, request):
        # Code to be executed for each request before the view is called
        self.request_count += 1
        request_id = self.request_count
        start_time = time.time()
        
        # Log request details
        logger.info(f"Request #{request_id} started: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        
        # Call the view
        response = self.get_response(request)
        
        # Code to be executed for each request/response after the view is called
        duration = time.time() - start_time
        logger.info(f"Request #{request_id} completed: {response.status_code} in {duration:.2f}s")
        
        return response 