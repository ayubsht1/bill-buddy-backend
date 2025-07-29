from rest_framework.response import Response

def custom_response(success=True, message=None, data=None, errors=None, status_code=200):
    """
    Returns a consistent response format for API views.
    
    Parameters:
    - success: bool, operation status
    - message: str, human-readable message
    - data: dict or list, response data
    - errors: dict or list, errors if any
    - status_code: int, HTTP status code
    
    Returns:
    - DRF Response object
    """
    response_data = {
        "success": success,
        "message": message if message else ("Operation successful" if success else "Operation failed"),
        "data": data if data is not None else {},
        "errors": errors if errors is not None else {}
    }
    return Response(response_data, status=status_code)
