from django.utils.decorators import available_attrs
from functools import wraps

import logging

def task():
    from django_ztask.conf import settings
    import zmq
    def wrapper(func):
        function_name = '%s.%s' % (func.__module__, func.__name__)
        
        logger = logging.getLogger('ztaskd')
        logger.info('Registered task: %s' % function_name)
        
        from django_ztask.context import shared_context as context
        socket = context.socket(zmq.PUSH)
        socket.connect(settings.ZTASKD_URL)
        @wraps(func)
        def _func(*args, **kwargs):
            if settings.ZTASKD_ALWAYS_EAGER:
                try:
                    socket.send_pyobj((function_name, args, kwargs))
                except Exception, e:
                    func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        def _func_delay(*args, **kwargs):
            try:
                socket.send_pyobj(('ztask_log', ('.delay is depricated... use.async instead', function_name), None))
            except:
                pass
            _func(*args, **kwargs)
        setattr(func, 'async', _func)
        setattr(func, 'delay', _func_delay)
        return func
    
    return wrapper
