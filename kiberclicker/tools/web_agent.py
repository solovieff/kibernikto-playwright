import pprint
import traceback

from playwright.async_api import Page

from .schema import AvailableWebActions, BasicWebAgent, ClickParameters
from ..bots.clicker_executor import ClickerExecutor

CLICKER = ClickerExecutor()


async def web_agent(
        action: AvailableWebActions,
        web_link: str,
        request: str | None = None,
        click_params: dict | None = None,
        default_clickables_amount: int = 5,
        key: str = "unknown"
):
    print(
        f"\n\t- [web_agent] \n"
        f"action='{action}'\n"
        f"request='{request}'\n"
        f"web_link='{web_link}'\n"
        f"click_params={click_params}\n"
        f"key={key}\n"
    )
    result = None
    try:
        if action == "get_click_params":
            await CLICKER.page.wait_for_load_state('domcontentloaded')
            screenshot_bytes: bytes = await CLICKER.page.screenshot(full_page=True, type="png", scale="css")
            result = await CLICKER.get_click_options(screenshot_bytes, request=request, amount=default_clickables_amount)

            # await page.close()
        elif action == "click":
            if not click_params:
                return "click_params are required for click action"
            click_point: ClickParameters = ClickParameters.model_validate(click_params)
            result = await CLICKER.click(page=CLICKER.page, point=click_point, open_new=True)
        else:
            result = "Unknown action"

        print(f"[WEB AGENT RESULT]\n {result}\n")
        return result

    except Exception as error:
        print(traceback.format_exc())
        return f"{error}"


def web_agent_tool():
    return {
        "type": "function",
        "function": {
            "name": "web_agent",
            "description": "Call agent connected to browser. "
                           "He can look at the page via playwright screenshot, click and check results.",
            "parameters": BasicWebAgent.model_json_schema()
        }
    }
