# etherfidailycollector
Small python script that helps with processing Daily Collector on ether.fi

<h2>🚀 Installation</h2>

```
git clone https://github.com/Jcomper/etherfidailycollector.git

cd etherfidailycollector

pip install -r requirements.txt

python main.py
```

# Before you start:
- rename data\wallets_EXAMPLE.txt -> data\wallets.txt
- rename data\eth_api_EXAMPLE.txt -> data\eth_api.txt
- put your wallets (NOT PRIVATE KEYS) to data\wallets.txt
- put your etherscan.io API KEY to data\eth_api.txt if you want to avoid rate limits exception (or you can set a 30-60 seconds pause between wallets)

<h2>⚙️ Settings</h2>
The script is running indefinitely, it checks wallet by wallet, and if available collects "Daily Collector" bonuses on ether.fi then sleep a random time. You can set limits in setting.py CYCLE_SLEEP_FROM and CYCLE_SLEEP_TO variables.