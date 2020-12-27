# Finance bot
Project for Programming course by Ivan Vasilyev, Maria Radionova and Ekaterina Tochilina.

We get information from https://www.moex.com/ and https://finnhub.io/

This bot can:

- Find company stock price (current or for custom period)
- Build plots of your investment portfolio for custom period to help analyze it.

## Configure

```bash
pip install -r requirements.txt
```

Copy "src/config_sample.py" into "src/config.py" and put real keys and telegram bot token.

Run:

```bash
python src/bot.py
```
