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
- put your wallets (NOT PRIVATE KEYS) to data\wallets.txt
- rename data\proxies_EXAMPLE.txt -> data\proxies.txt
- put your proxies in format user:password@IP:PORT to data\proxies.txt


<h2>⚙️ Settings</h2>
The script is running indefinitely, it checks wallet by wallet, and if available collects "Daily Collector" bonuses on ether.fi then sleep a random time. You can set limits in setting.py CYCLE_SLEEP_FROM and CYCLE_SLEEP_TO variables.