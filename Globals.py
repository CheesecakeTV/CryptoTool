import os
from pathlib import Path

appdata = Path(os.getenv('LOCALAPPDATA')) / "CryptoTool"
appdata.mkdir(exist_ok=True)




