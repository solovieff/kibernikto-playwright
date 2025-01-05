import asyncio
import json
import pprint
import traceback
from typing import List

from kiberclicker import tools
from kiberclicker._utils import generate_test_report, save_report
from kiberclicker.tools.schema import ClickResults
from kiberclicker.tools.web_agent import CLICKER
from kibernikto.bots.cybernoone import Kibernikto
from kibernikto.interactors import OpenAiExecutorConfig
from kibernikto.interactors.tools import Toolbox, get_tools_from_module


async def run_cmd_chat():
    tools_definitions: List[Toolbox] = get_tools_from_module(tools,
                                                             permitted_names=None)
    config = OpenAiExecutorConfig(who_am_i="You can click and view browser pages and help with testing.",
                                  tools=tools_definitions)

    browser_ai = Kibernikto(master_id="brwoser_man", username="browseee", config=config)

    try:
        reply = await browser_ai.heed_and_reply("Gutten Abend!")
        print(reply)

        while True:
            question = input("Enter your question (or 'exit' to quit): ")

            if question.lower() == 'exit':
                print("Exiting...")
                break

            reply = await browser_ai.heed_and_reply(question)
            print(f"Reply: {reply}")
    finally:
        if browser_ai:
            await browser_ai.client.close()


async def multitest_website(web_link: str):
    base_results = await test_website(web_link)

    new_url_results = [x for x in base_results if x.new_url is not None]

    for i, result in enumerate(new_url_results):
        secondary_results = await test_website(result.new_url, index=i + 1)
        base_results += secondary_results

    save_report(base_results)
    return base_results


async def test_website(web_link: str, index=0, persist_html=False) -> List[ClickResults]:
    print(f"\n\nTESTING {web_link}\n\n")
    from kiberclicker.tools.web_agent import CLICKER
    if not CLICKER.browser:
        await CLICKER.init_browser(web_link)
    else:
        await CLICKER._init_page(web_link)
        CLICKER._reset()

    results = []
    click_options = await tools.web_agent.web_agent(action="get_click_params", web_link=web_link,
                                                    default_clickables_amount=5)
    pprint.pprint(click_options)

    # some cases of bad auto-json
    click_options = pull_out_clickables(click_options)

    for click_option in click_options:
        click_result_json: dict = await tools.web_agent.web_agent(action="click", web_link=web_link,
                                                                  click_params=click_option)
        pprint.pprint(click_result_json)
        try:
            click_result: ClickResults = ClickResults.model_validate(click_result_json)
            results.append(click_result)
        except Exception as e:
            traceback.print_exc()
            print(f"failed to validate click result: {e} from {click_result_json}")

    print("RESULTS")
    for res in results:
        pprint.pprint(res.model_dump())

    with open(f'/tmp/{index}_results.json', 'w', encoding='utf-8') as f:
        for res in results:
            json.dump(res.model_dump(), f, ensure_ascii=False, indent=4)
            f.write('\n')
    if persist_html:
        save_report(results)
    return results


def pull_out_clickables(click_options_obj):
    if isinstance(click_options_obj, list):
        return click_options_obj

    if isinstance(click_options_obj, dict):
        if "click_count" in click_options_obj:
            return [click_options_obj, ]
        first_key = next(iter(click_options_obj))
        return click_options_obj[first_key]

    raise ValueError("Bad data format.")


if __name__ == '__main__':
    #asyncio.run(run_cmd_chat())
    asyncio.run(test_website(web_link="https://example.com/"))
