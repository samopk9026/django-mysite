from watch.models.models import action_log
from loginapp.models import database
import json
from django.http import HttpResponse, JsonResponse


# 把手表端的行为传输记录下来发送给ios端
def tend_to_change_description(token, new_description, status):
    data = database()
    # new_description = json.loads(request.body.decode())["new_description"]
    # new_description = request.body.decode().split("=")[1].split("%")[0]
    # print(new_description)
    # new_description = request.POST.get("new_description")
    # token = request.COOKIES.get("token")
    userid = data.get_username(token)
    action = action_log(owner=userid, status= status, action_code=101, action_detail=new_description)
    action.save()
