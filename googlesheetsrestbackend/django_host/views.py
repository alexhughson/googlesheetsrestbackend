from django.http import HttpResponse

def handle_request(request, object, id=None):
    return HttpResponse(object + str(id))
