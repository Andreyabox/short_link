from locust import HttpUser, task, between, constant, tag
import random
import logging
from faker import Faker

class ShortLinkUser(HttpUser):
    # Можно использовать разные варианты wait_time в зависимости от теста
    wait_time = between(1, 5)  # или constant(3) для фиксированного интервала
    
    host = "http://127.0.0.1:8000"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()  # Генератор случайных данных
        self.short_codes = []  # Для хранения созданных коротких ссылок
        self.username = f"user{random.randint(1, 10000)}"
        self.password = self.fake.password()

    def on_start(self):
        """Регистрация и аутентификация пользователя"""
        try:
            # Регистрация
            resp = self.client.post("/register", 
                                  json={
                                      "username": self.username,
                                      "password": self.password
                                  })
            resp.raise_for_status()
            
            # Получение токена
            resp = self.client.post("/token", 
                                   data={
                                       "username": self.username,
                                       "password": self.password
                                   })
            resp.raise_for_status()
            self.token = resp.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Создаем несколько ссылок при старте
            for _ in range(3):
                self._create_short_link()
                
        except Exception as e:
            logging.error(f"Error during startup: {e}")
            self.environment.runner.quit()

    def _create_short_link(self):
        """Создание короткой ссылки"""
        original_url = self.fake.uri()
        data = {"original_url": original_url}
        
        resp = self.client.post("/links", 
                               json=data,
                               headers=self.headers)
        if resp.status_code == 200:
            short_code = resp.json().get("short_code")
            if short_code:
                self.short_codes.append(short_code)
        return resp

    @task(3)  # Более высокая частота выполнения
    @tag("get_link")
    def get_link(self):
        """Получение существующей ссылки"""
        if self.short_codes:
            short_code = random.choice(self.short_codes)
            with self.client.get(f"/links/{short_code}", 
                                headers=self.headers,
                                catch_response=True) as response:
                if response.status_code == 404:
                    response.failure("Link not found")
                elif response.elapsed.total_seconds() > 1.0:
                    response.failure("Response too slow")

    @task(2)
    @tag("create_link")
    def create_link(self):
        """Создание новой короткой ссылки"""
        response = self._create_short_link()
        if response.status_code != 200:
            response.failure(f"Failed to create link: {response.text}")

    @task(1)
    @tag("stats")
    def get_stats(self):
        """Получение статистики"""
        if self.short_codes:
            short_code = random.choice(self.short_codes)
            self.client.get(f"/links/{short_code}/stats",
                          headers=self.headers,
                          name="/links/[short_code]/stats")

    @task(1)
    @tag("list_links")
    def list_links(self):
        """Получение списка ссылок"""
        self.client.get("/links",
                       headers=self.headers)

    @task(1)
    @tag("delete_link")
    def delete_link(self):
        """Удаление ссылки"""
        if self.short_codes:
            short_code = self.short_codes.pop()
            self.client.delete(f"/links/{short_code}",
                             headers=self.headers,
                             name="/links/[short_code] (DELETE)")
