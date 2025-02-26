from typing import List, Union
from pydantic import BaseModel, Field

class YandexDirectAuth(BaseModel):
    login: str
    token: str
    goals: list[int]

class VkAuth(BaseModel):
    access_token: str

class Account(BaseModel):
    account_name: str
    source: str
    auth: Union[YandexDirectAuth, VkAuth, dict]

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_auth_by_source()

    def _validate_auth_by_source(self):
        """Валидирует auth в зависимости от source"""
        if self.source.upper() == 'YANDEX_DIRECT':
            if isinstance(self.auth, dict):
                self.auth = YandexDirectAuth(**self.auth)
        elif self.source.upper() == 'VK':
            if isinstance(self.auth, dict):
                self.auth = VkAuth(**self.auth) 