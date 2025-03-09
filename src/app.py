from flask import Flask, request, jsonify
from main import initialize_orchestrator
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize orchestrator
orchestrator = initialize_orchestrator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Service is running"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that processes user input and returns responses."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "Invalid request. Please provide a 'message' field."
            }), 400

        user_input = data['message']
        response = orchestrator.orchestrate_task(user_input)
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 