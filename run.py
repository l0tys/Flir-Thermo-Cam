import sys
import os

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from src.main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting program")
    except Exception as e:
        print(f"Application error: {e}")