from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

AvailableWebActions = Literal[
    "get_click_params",  # анализ скриншота и определение координат для клика
    "click"  # выполнение клика по координатам
]


class ClickParameters(BaseModel):
    x: int
    y: int
    description: str
    expected_behaviour: str
    exact_element_text: str
    click_count: int = 1


class ClickResults(ClickParameters):
    actual_behaviour: str
    status: str
    action_description: str
    new_url: str | None = None
    base_url: str | None = None


class BasicWebAgent(BaseModel):
    action: AvailableWebActions = Field(
        description="what the agent should do"
    )
    web_link: HttpUrl = Field(  # Теперь обязательное поле!
        description="URL of the page to work with"
    )
    request: str = Field(
        None,
        description="human description of what to find on screenshot or where to click"
    )
    click_params: Optional[ClickParameters] = Field(
        None,
        description="Click parameters when action=='click'"
    )
