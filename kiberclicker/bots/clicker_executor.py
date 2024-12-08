import asyncio

from kibernikto.interactors import OpenAIExecutor
import base64
import json
import pprint
import traceback
from datetime import datetime
from typing import Dict, Literal
from openai._types import NOT_GIVEN
from ..tools.schema import AvailableWebActions, BasicWebAgent, ClickParameters, ClickResults
from playwright.async_api import async_playwright, Page, PlaywrightContextManager, Browser, BrowserContext

from kibernikto.interactors import OpenAiExecutorConfig, OpenAIExecutor


class ClickerExecutor(OpenAIExecutor):
    def __init__(self):
        clicker_config = OpenAiExecutorConfig(
            temperature=0.1,
            max_tokens=1300,
            who_am_i="You analyze the image and provide answers based on what is asked")
        self.manager: PlaywrightContextManager = PlaywrightContextManager()
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        super().__init__(config=clicker_config, unique_id=datetime.now().timestamp())

    async def init_browser(self, web_link: str):
        if self.browser is None:
            p = await self.manager.start()

            self.browser: Browser = await p.firefox.launch(headless=False,
                                                           slow_mo=100,  # делает движения мыши видимыми
                                                           args=['--start-maximized']
                                                           )
            self.context = await self.browser.new_context(
                # viewport={'width': 2560, 'height': 1440},
                # screen={'width': 2560, 'height': 1440},
                no_viewport=True,  # Отключает эмуляцию viewport - использует реальный размер окна
                ignore_https_errors=True,  # Игнорировать ошибки HTTPS
                java_script_enabled=True,  # Включить JavaScript
            )
            start_page = await self.context.new_page()
            self.page = start_page
            await self.page.goto(web_link)
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(timeout=1300)

    async def close(self):
        await self.context.close()
        await self.browser.close()

    async def get_click_options(self, screenshot_bytes: bytes, request: str | None = None, amount=5):
        request_text = f"{request}" if request is not None else ""
        return await self._analyse_screenshot(screenshot_bytes,
                                              f"{request_text}. Return the {amount} most important clickable objects "
                                              f"(links or buttons) as an array of JSON objects "
                                              f"with fields {ClickParameters.model_fields.keys()}",
                                              amount=amount)

    async def _analyse_screenshot(self, screenshot_bytes: bytes, request: str = None, amount=5):
        # Конвертируем в base64
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        image_url = f"data:image/png;base64,{screenshot_base64}"

        timestamp = datetime.now().timestamp()

        additional_data = {
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        }

        response = await super().heed_and_reply(
            message=request,
            response_type="json_object",
            additional_content=additional_data
        )

        try:
            click_targets = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            click_targets = []

        # debug
        screenshot_path = f"/tmp/screenshot_{timestamp}.png"
        with open(screenshot_path, "wb") as f:
            f.write(base64.b64decode(screenshot_base64))

        pprint.pprint(click_targets)
        return click_targets

    async def click(self, page: Page, point: ClickParameters, open_new=False):
        url = page.url
        if open_new:
            # Создаём копию страницы для каждого клика
            new_page = await self.context.new_page()
            await new_page.goto(page.url)
        else:
            new_page = page

        # Наводим мышку
        await new_page.mouse.move(point.x, point.y, steps=50)
        # Подсвечиваем точку
        await new_page.evaluate(f"""() => {{
            const div = document.createElement('div');
            div.style.position = 'absolute';
            div.style.left = '{point.x}px';
            div.style.top = '{point.y}px';
            div.style.width = '20px';
            div.style.height = '20px';
            div.style.backgroundColor = 'red';
            div.style.borderRadius = '50%';
            div.style.opacity = '0.5';
            div.style.zIndex = '10000';
            document.body.appendChild(div);
        }}""")
        await new_page.wait_for_timeout(2000)

        print(f"clicking (by text for now) ({point.x}, {point.y}, {point.exact_element_text})")

        # await new_page.mouse.click(point.x, point.y)
        await new_page.click(f"text={point.exact_element_text}")

        await new_page.wait_for_load_state('networkidle')
        new_url = new_page.url
        url_text = "Url did not change."
        if new_url != url:
            url_text = f"Url changed to {new_url}."
            print(f"url activity")
        else:
            print(f"screen activity")

        screenshot_bytes: bytes = await new_page.screenshot(full_page=True, scale="css")
        request = (
            f"Evaluate the changes that occurred after clicking on {point} on the page {page.url}. {url_text}. "
            f"Does everything look good? "
            f"How well did the actual changes match your expectations? "
            f"Return as a JSON object complying with json-schema: {ClickResults.model_json_schema()}")
        result = await self._analyse_screenshot(screenshot_bytes=screenshot_bytes, request=request)
        # await new_page.close()
        return result
