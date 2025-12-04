from datetime import datetime
from django.shortcuts import (
    HttpResponseRedirect,
    get_object_or_404,
    render,
    reverse,
)

from django.contrib.auth.models import User

from django.views import View
# Create your views here.


class DisplayAssessment(View):
    def get(self, request):
        string_to_date = datetime.strptime("2024-06-12", "%Y-%m-%d").date()
        # date_to_string = datetime.date()
        date_to_string = string_to_date.strftime("%Y-%m-%dT%X")
        current_time = datetime.now()
        
        print(string_to_date)
        print(date_to_string)
        print(current_time)
        print(type(string_to_date))
        print(type(date_to_string))

        user = User.objects.all()
        print(user)
        return render(
            request,
            "assessments/assessments.html",
        )
