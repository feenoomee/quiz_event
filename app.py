from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

@app.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')

@app.route('/media/<filename>')
def serve_media(filename):
    """Serve files from media folder"""
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'media'), filename)

@app.route('/api/register', methods=['POST'])
def register_team():
    """Handle team registration (placeholder)"""
    # This is where you'll handle the registration logic
    # For now, it's a placeholder
    return {'status': 'success', 'message': 'Registration received'}

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
