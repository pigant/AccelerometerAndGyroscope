import json
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    if request.method == 'POST':
        dic = json.loads(request.POST['data'])
        print ('El acc {}'.format(dic['accelerometer']))
        print ('El gyro {}'.format(dic['gyroscope']))
        print ('El magneto {}'.format(dic['magnetic']))
        print (request.POST['data'])
    return HttpResponse(content='listo')
