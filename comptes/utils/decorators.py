from django.core.exceptions import PermissionDenied
from functools import wraps

def role_autorise(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request,*args,**kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Vous devez être connecté pour accéder à cette page.")
            if request.user.role not in roles:
                raise PermissionDenied("Vous n'avez pas la permission d'accéder à cette page.")
            return view_func(request,*args,**kwargs)
        return wrapper
    return decorator