from siliconmetatrader5 import MetaTrader5
mt5 = MetaTrader5(host="localhost", port=8001)
mt5.initialize()

# Search for any symbol containing 'XAU' or 'GOLD'
symbols = mt5.symbols_get(group="*XAU*,*GOLD*")

for s in symbols:
    print(f"Name: {s.name} | Visible: {s.visible} | Path: {s.path}")

mt5.shutdown()