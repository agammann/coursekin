"""Start Coursekin and open its local interface."""
import os
import threading
import webbrowser
from coursekin.server import main

if __name__ == '__main__':
    port = int(os.environ.get('COURSEKIN_PORT', '8767'))
    threading.Timer(1.0, lambda: webbrowser.open(f'http://127.0.0.1:{port}')).start()
    main()
