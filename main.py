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

async def get_proxy(wallet):
    if 'proxy' in row_data[wallet]:
        if len(row_data[wallet]['proxy']) > 0:
            return f"http://{row_data[wallet]['proxy']}"
        else:
            return None
    else:
        return None

async def get_info(session, wallet, retry = 0):
    proxy = await get_proxy(wallet)

    max_retry = 3
    try:
        get_etherfi_url = f'https://app.ether.fi/api/portfolio/v3/{wallet}'
        
        async with session.get(get_etherfi_url, headers=etherfi_headers, ssl=False, proxy=proxy, timeout=10) as resp:
            resp_json = await resp.json(content_type=None)
            if ('totalIntegrationLoyaltyPoints' in resp_json):
                loyaltyPoints = resp_json['totalIntegrationLoyaltyPoints']
            if ('totalIntegrationEigenLayerPoints' in resp_json):
                eigenlayerPoints = resp_json['totalIntegrationEigenLayerPoints']

            row_data[wallet]['etherfi']['loyaltyPoints'] = loyaltyPoints
            row_data[wallet]['etherfi']['eigenlayerPoints'] = eigenlayerPoints
            badges = resp_json['badges']
            for badge in badges:
                if badge['name'] == 'daily-collector':
                    row_data[wallet]['etherfi']['dailyCollector'].update(badge)

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
        proxy = await get_proxy(wallet)
        process_etherfi_url = f'https://app.ether.fi/api/dailyStreak/updateStreak'
        payload = {'account': f'{wallet}'}
        async with session.post(process_etherfi_url, data=json.dumps(payload), headers = etherfi_headers, ssl=False, proxy=proxy, timeout=10) as resp:
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
        dailyStreak = row_data[wallet]['etherfi']['dailyCollector']['dailyStreak']
        dailyStreakPoints = row_data[wallet]['etherfi']['dailyCollector']['points']
        dailyStreakMaxPoints = row_data[wallet]['etherfi']['dailyCollector']['maxPoints']

        loyaltyPoints = row_data[wallet]['etherfi']['loyaltyPoints']
        eigenlayerPoints = row_data[wallet]['etherfi']['eigenlayerPoints']

        if cooldownActive == False:
            logger.success(f'{wallet} : Do collect')
            logger.success(f'LoyaltyPoints = {loyaltyPoints} : eigenlayerPoints = {eigenlayerPoints}')
            logger.success(f'DailyStreak = {dailyStreak} : DailyStreakPoints = {dailyStreakPoints} : MaxDailyStreakPoints = {dailyStreakMaxPoints} : Cooldown Active = {cooldownActive}')
            await process_daily_collector(session, wallet)
        else:
            logger.warning(f'{wallet} : Nothing to collect')
            logger.warning(f'LoyaltyPoints = {loyaltyPoints} : eigenlayerPoints = {eigenlayerPoints}')
            logger.warning(f'DailyStreak = {dailyStreak} : DailyStreakPoints = {dailyStreakPoints} : MaxDailyStreakPoints = {dailyStreakMaxPoints} : Cooldown Active = {cooldownActive}')

async def run():

    for wallet in WALLETS:

        row_data.update({wallet: {
        }})

        walletIndex = WALLETS.index(wallet)
        if len(PROXIES) >= walletIndex + 1:
            proxy = PROXIES[walletIndex]
            row_data[wallet].update({'proxy': proxy})

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

