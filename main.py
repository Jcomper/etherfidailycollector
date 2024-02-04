#!/usr/bin/env python3.10
from config import *

row_data = {}
etherfi_headers = {
    'authority': 'app.ether.fi',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://app.ether.fi',
    'referer': 'https://app.ether.fi/portfolio',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

async def sleep(sleep_from: int, sleep_to: int):
    delay = random.randint(sleep_from, sleep_to)

    logger.info(f"💤 Sleep {delay} s.")
    for _ in range(delay):
        await asyncio.sleep(1)

async def get_info(session, wallet, retry = 0):
    max_retry = 3
    try:

        if (len(api_keys[chain])) > 0:
            api_key = random.choice(api_keys[chain])
            get_latest_block_url = f'{base_url[chain]}/api?module=proxy&action=eth_blockNumber&apikey={api_key}'
        else:
            get_latest_block_url = f'{base_url[chain]}/api?module=proxy&action=eth_blockNumber'


        async with session.get(get_latest_block_url, ssl=False, timeout=10) as resp:
            resp_json = await resp.json(content_type=None)
            row_data[wallet]['blockNumber'] = resp_json['result']

        if row_data[wallet]['blockNumber'] == "Invalid API Key":
            logger.error(f'{wallet} : {chain} : Invalid API Key : {api_key}')
            raise('Invalid API Key')

        else: 
            row_data[wallet]['blockNumber'] = hexToInt(row_data[wallet]['blockNumber'])
            logger.success(f'{wallet} : ethereum latest block {row_data[wallet]["blockNumber"]}')
            get_etherfi_url = f'https://app.ether.fi/api/portfolio/{wallet}/{row_data[wallet]["blockNumber"]}'
            
            async with session.get(get_etherfi_url, headers=etherfi_headers, ssl=False, timeout=10) as resp:
                resp_json = await resp.json(content_type=None)
                row_data[wallet]['etherfi']['loyaltyPoints'] = resp_json['loyaltyPoints']
                row_data[wallet]['etherfi']['eigenlayerPoints'] = resp_json['eigenlayerPoints']
                row_data[wallet]['etherfi']['dailyCollector'].update(resp_json['badges'][0])

    except Exception as error:
        logger.error(f'{wallet} | error : {error}')
        retry += 1
        if retry < max_retry:
            logger.warning(f'{wallet} : retry {retry}/{max_retry}')
            time_sleep = 3
            await asyncio.sleep(time_sleep)
            return await get_info(session, wallet, retry)
        else:
            raise(f'{wallet} | error : {error}')

async def process_daily_collector(session, wallet):
    try:
        process_etherfi_url = f'https://app.ether.fi/api/dailyStreak/updateStreak'
        payload = {'account': f'{wallet}'}
        async with session.post(process_etherfi_url, data=json.dumps(payload), headers = etherfi_headers, ssl=False, timeout=10) as resp:
            resp_json = await resp.json(content_type=None)
            if resp_json['message'] == 'Streak updated successfully':
                logger.success(f'{wallet} : {resp_json["message"]}')
            else:
                logger.error(f'{wallet} : {resp_json["message"]}')
        
    except Exception as error:
        logger.error(f'{wallet} | error : {error}')

async def main(wallet):

    async with aiohttp.ClientSession() as session:

        await get_info(session, wallet)

        cooldownActive = row_data[wallet]['etherfi']['dailyCollector']['cooldownActive']
        loyaltyPoints = row_data[wallet]['etherfi']['loyaltyPoints']

        if loyaltyPoints > 0 and cooldownActive == False:
            logger.success(f'{wallet} : Do collect: LoyaltyPoints = {loyaltyPoints} : Cooldown Active = {cooldownActive}')
            await process_daily_collector(session, wallet)
        else:
            logger.warning(f'{wallet} : Nothing to collect: LoyaltyPoints = {loyaltyPoints} : Cooldown Active = {cooldownActive}')

async def run():

    for wallet in WALLETS:
        row_data.update({wallet: {
            "blockNumber" : {},
        }})

        row_data[wallet].update({'etherfi': {'loyaltyPoints': {}, 'eigenlayerPoints': {}, 'dailyCollector':{}}})

    while True:
        try:
            for wallet in WALLETS:
                await main(wallet)
                await sleep(SLEEP_FROM, SLEEP_TO)
        except asyncio.TimeoutError:
            pass
        except Exception as error:
            logger.error(f'{wallet} | error : {error}')

        logger.info(f'💤 CYCLE Sleep')
        await sleep(CYCLE_SLEEP_FROM, CYCLE_SLEEP_TO)


if __name__ == "__main__":

    cprint('ether.fi Daily Collector', 'green')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

