import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import logging
from flask import Flask
from flask_caching import Cache
from FoodCarbsAPI import create_app

app = create_app()

# Set up caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Set up logging
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Console handler for warning and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

# Add handlers to the app logger
app.logger.addHandler(console_handler)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
