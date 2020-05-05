import json
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import time

#connect to Redis
rs = redis.StrictRedis(host='localhost', port='6379', db=0)

@api_view(['POST'])
def visited_links(request):
    # POST json api data
    for key in rs.keys(): rs.delete(key) # domains clear
    if request.method == 'POST':
        try:
            item = json.loads(request.body)
            domains = {}
            for url in item['links']:
                url = url.replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
                domains[url]=time.time()
            rs.zadd('domains', domains)

            # rs.set(time.time(), str(json.dumps(values)))
            # rs.sadd(key, *values)

            return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
        except:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def visited_domains(request):
    # GET json api data
    if request.method == 'GET':
        try:
            req_from, req_to = int(request.GET.get('from')), int(request.GET.get('to'))
            temp = rs.zrangebyscore('domains', min=req_from, max=req_to)
            if not temp: return Response({'status': 'no content'}, status=status.HTTP_204_NO_CONTENT)
            response = {
                'domains': temp,
                'status':'ok'}
            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

