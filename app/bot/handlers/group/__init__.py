from . import command
from . import message
from . import callback_query

routers = [
    callback_query.router,
    command.router,
    command.router_id,
    message.router,
]
