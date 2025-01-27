from flask import Flask, render_template, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Configurações
app.config.update(
    PORT=int(os.environ.get('PORT', 10000)),
    HOST=os.environ.get('HOST', '0.0.0.0'),
    ENVIRONMENT=os.environ.get('ENVIRONMENT', 'production'),
    UPDATE_INTERVAL=int(os.environ.get('UPDATE_INTERVAL', 30)),
    CONFIDENCE_THRESHOLD=float(os.environ.get('CONFIDENCE_THRESHOLD', 75)),
    VALUE_THRESHOLD=float(os.environ.get('VALUE_THRESHOLD', 5))
)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat(),
        "message": "Odds Analysis System is running"
    })

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT']
    )
