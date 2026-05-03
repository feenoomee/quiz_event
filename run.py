#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TLTQUIZ - Quiz Events Management Platform
Entry point for running the application
"""

import os
from app import app

if __name__ == '__main__':
    # Get environment
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(env == 'development')
    )
