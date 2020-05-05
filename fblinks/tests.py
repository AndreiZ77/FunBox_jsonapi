from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
import json, time, redis

class MyApiTestCase(APITestCase):
    def setUp(self):
        self.rs = redis.StrictRedis(host='localhost', port='6379', db=0)
        self.valid_data = {
                        "links": [
                            "https://ya.ru",
                            "https://ya.ru?q=123",
                            "funbox.ru",
                            "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
                        ]
                    }
        self.not_valid_data = {
            "no_links": [
                "12345"
            ]
        }


    def test_valid_post(self):
        response = self.client.post('/visited_links',
                                    self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_not_valid_post(self):
        response = self.client.post('/visited_links',
                                    self.not_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_get(self):
        timestamp = 1234567890
        self.rs.zadd('domains', {'test.com': timestamp})
        response = self.client.get(f'/visited_domains?from={timestamp-10}&to={timestamp+10}')
        self.assertTrue(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_valid_get(self):
        response = self.client.get(f'/visited_domains?from={"A123456789"}&to={0}')
        self.assertTrue(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_redis_data_post_get(self):
        # POST
        timestamp = int(time.time())
        response = self.client.post('/visited_links', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # GET
        response = self.client.get(f'/visited_domains?from={timestamp - 10}&to={timestamp + 10}')
        self.assertTrue(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        true_data = {'domains': [b'ya.ru', b'funbox.ru', b'stackoverflow.com'], 'status': 'ok'}
        self.assertEqual(response.data, true_data)

