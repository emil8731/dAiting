from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
import uuid
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import application components
from src.app import DatingAppAIAssistant
from src.storage import DataStorage

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', str(uuid.uuid4()))

# Initialize Dating App AI Assistant
dating_app = DatingAppAIAssistant()

@app.route('/')
def index():
    """Render the home page."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    # Get user stats
    stats = dating_app.get_user_stats()
    
    # Get active conversations
    conversations = dating_app.get_active_conversations(limit=10)
    
    # Get message activity
    activity = dating_app.get_message_activity(days=30)
    
    return render_template('dashboard.html', 
                          stats=stats, 
                          conversations=conversations, 
                          activity=activity)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    """Handle authentication with dating platforms."""
    if request.method == 'POST':
        platform = request.form.get('platform')
        
        if platform == 'tinder':
            token = request.form.get('token')
            if not token:
                flash('Token is required for Tinder authentication', 'danger')
                return redirect(url_for('auth'))
            
            result = dating_app.authenticate('tinder', token=token)
            if result:
                session['authenticated'] = True
                session['platform'] = platform
                flash('Successfully authenticated with Tinder!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Failed to authenticate with Tinder', 'danger')
        
        elif platform == 'hinge':
            phone_number = request.form.get('phone_number')
            verification_code = request.form.get('verification_code')
            
            if not phone_number:
                flash('Phone number is required for Hinge authentication', 'danger')
                return redirect(url_for('auth'))
            
            if verification_code:
                # Complete authentication with verification code
                result = dating_app.authenticate('hinge', 
                                               phone_number=phone_number, 
                                               verification_code=verification_code)
                if result:
                    session['authenticated'] = True
                    session['platform'] = platform
                    flash('Successfully authenticated with Hinge!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Failed to authenticate with Hinge', 'danger')
            else:
                # Request verification code
                result = dating_app.authenticate('hinge', phone_number=phone_number)
                if result:
                    flash('Verification code sent to your phone. Please enter it below.', 'info')
                    session['phone_number'] = phone_number
                else:
                    flash('Failed to request verification code from Hinge', 'danger')
    
    return render_template('auth.html')

@app.route('/matches')
def matches():
    """Display matches from the dating platform."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    platform = session.get('platform', 'tinder')
    limit = request.args.get('limit', 20, type=int)
    
    matches = dating_app.get_matches(platform, limit=limit)
    
    return render_template('matches.html', matches=matches, platform=platform)

@app.route('/match/<match_id>')
def match_detail(match_id):
    """Display details for a specific match."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    match = dating_app.get_match(match_id)
    if not match:
        flash('Match not found', 'danger')
        return redirect(url_for('matches'))
    
    # Analyze match profile
    analysis = dating_app.analyze_match(match_id)
    
    # Get conversation if exists
    conversation = dating_app.get_conversation_for_match(match_id)
    
    return render_template('match_detail.html', 
                          match=match, 
                          analysis=analysis, 
                          conversation=conversation)

@app.route('/generate_message/<match_id>', methods=['GET', 'POST'])
def generate_message(match_id):
    """Generate a message for a match."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        message_content = request.form.get('message')
        platform = session.get('platform', 'tinder')
        
        if action == 'send':
            # Get the message from hidden field
            message_data = json.loads(request.form.get('message_data'))
            
            # Send the message
            result = dating_app.approve_and_send_message(platform, match_id, message_data)
            
            if result:
                flash('Message sent successfully!', 'success')
                # Get conversation ID
                conversation = dating_app.get_conversation_for_match(match_id)
                if conversation:
                    return redirect(url_for('conversation', conversation_id=conversation['id']))
                else:
                    return redirect(url_for('match_detail', match_id=match_id))
            else:
                flash('Failed to send message', 'danger')
        
        elif action == 'edit':
            # Get the message from hidden field
            message_data = json.loads(request.form.get('message_data'))
            edited_content = request.form.get('edited_content')
            
            # Edit and send the message
            result = dating_app.edit_and_send_message(platform, match_id, message_data, edited_content)
            
            if result:
                flash('Edited message sent successfully!', 'success')
                # Get conversation ID
                conversation = dating_app.get_conversation_for_match(match_id)
                if conversation:
                    return redirect(url_for('conversation', conversation_id=conversation['id']))
                else:
                    return redirect(url_for('match_detail', match_id=match_id))
            else:
                flash('Failed to send edited message', 'danger')
    
    # Generate a message
    message = dating_app.generate_initial_message(match_id)
    
    if not message:
        flash('Failed to generate message', 'danger')
        return redirect(url_for('match_detail', match_id=match_id))
    
    # Get match details for context
    match = dating_app.get_match(match_id)
    
    return render_template('generate_message.html', 
                          message=message, 
                          match=match, 
                          message_data=json.dumps(message))

@app.route('/conversations')
def conversations():
    """Display all conversations."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    platform = request.args.get('platform')
    limit = request.args.get('limit', 20, type=int)
    
    conversations = dating_app.get_active_conversations(platform, limit=limit)
    
    return render_template('conversations.html', conversations=conversations)

@app.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    """Display a specific conversation."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    # Get conversation details
    conversation = dating_app.get_conversation(conversation_id)
    if not conversation:
        flash('Conversation not found', 'danger')
        return redirect(url_for('conversations'))
    
    # Get messages
    messages = dating_app.get_conversation_history(conversation_id)
    
    # Get match details
    match = dating_app.get_match(conversation['match_id'])
    
    # Get conversation insights
    insights = dating_app.get_conversation_insights(conversation_id)
    
    return render_template('conversation.html', 
                          conversation=conversation, 
                          messages=messages, 
                          match=match, 
                          insights=insights)

@app.route('/generate_response/<conversation_id>', methods=['GET', 'POST'])
def generate_response(conversation_id):
    """Generate a response for a conversation."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        platform = session.get('platform', 'tinder')
        
        if action == 'send':
            # Get the response from hidden field
            response_data = json.loads(request.form.get('response_data'))
            
            # Get match ID from conversation
            match_id = dating_app.get_match_id_from_conversation(conversation_id)
            if not match_id:
                flash('Failed to get match ID from conversation', 'danger')
                return redirect(url_for('conversation', conversation_id=conversation_id))
            
            # Send the response
            result = dating_app.approve_and_send_message(platform, match_id, response_data)
            
            if result:
                flash('Response sent successfully!', 'success')
                return redirect(url_for('conversation', conversation_id=conversation_id))
            else:
                flash('Failed to send response', 'danger')
        
        elif action == 'edit':
            # Get the response from hidden field
            response_data = json.loads(request.form.get('response_data'))
            edited_content = request.form.get('edited_content')
            
            # Get match ID from conversation
            match_id = dating_app.get_match_id_from_conversation(conversation_id)
            if not match_id:
                flash('Failed to get match ID from conversation', 'danger')
                return redirect(url_for('conversation', conversation_id=conversation_id))
            
            # Edit and send the response
            result = dating_app.edit_and_send_message(platform, match_id, response_data, edited_content)
            
            if result:
                flash('Edited response sent successfully!', 'success')
                return redirect(url_for('conversation', conversation_id=conversation_id))
            else:
                flash('Failed to send edited response', 'danger')
    
    # Generate a response
    response = dating_app.generate_response(conversation_id)
    
    if not response:
        flash('Failed to generate response', 'danger')
        return redirect(url_for('conversation', conversation_id=conversation_id))
    
    # Get conversation details for context
    conversation_data = dating_app.get_conversation(conversation_id)
    match = dating_app.get_match(conversation_data['match_id'])
    
    return render_template('generate_response.html', 
                          response=response, 
                          conversation=conversation_data, 
                          match=match, 
                          response_data=json.dumps(response))

@app.route('/monitor/<conversation_id>', methods=['POST'])
def monitor_conversation(conversation_id):
    """Start or stop monitoring a conversation."""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    action = request.form.get('action')
    platform = session.get('platform', 'tinder')
    
    if action == 'start':
        result = dating_app.start_conversation_monitoring(conversation_id, platform)
        if result:
            return jsonify({'success': True, 'message': 'Monitoring started'})
        else:
            return jsonify({'success': False, 'message': 'Failed to start monitoring'})
    
    elif action == 'stop':
        result = dating_app.stop_conversation_monitoring(conversation_id)
        if result:
            return jsonify({'success': True, 'message': 'Monitoring stopped'})
        else:
            return jsonify({'success': False, 'message': 'Failed to stop monitoring'})
    
    return jsonify({'success': False, 'message': 'Invalid action'})

@app.route('/stats')
def stats():
    """Display user statistics."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    # Get user stats
    user_stats = dating_app.get_user_stats()
    
    # Get message activity
    days = request.args.get('days', 30, type=int)
    activity = dating_app.get_message_activity(days=days)
    
    return render_template('stats.html', stats=user_stats, activity=activity, days=days)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Manage application settings."""
    if 'authenticated' not in session or not session['authenticated']:
        flash('Please authenticate first', 'warning')
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        # Update notification settings
        notification_enabled = request.form.get('notification_enabled') == 'on'
        new_message_notification = request.form.get('new_message_notification') == 'on'
        new_match_notification = request.form.get('new_match_notification') == 'on'
        conversation_inactive_notification = request.form.get('conversation_inactive_notification') == 'on'
        suggested_response_notification = request.form.get('suggested_response_notification') == 'on'
        
        # Update notification config
        dating_app.notification_system.config['enabled'] = notification_enabled
        dating_app.notification_system.config['notification_types']['new_message'] = new_message_notification
        dating_app.notification_system.config['notification_types']['new_match'] = new_match_notification
        dating_app.notification_system.config['notification_types']['conversation_inactive'] = conversation_inactive_notification
        dating_app.notification_system.config['notification_types']['suggested_response'] = suggested_response_notification
        
        # Save notification config
        result = dating_app.notification_system.save_config()
        
        if result:
            flash('Settings updated successfully!', 'success')
        else:
            flash('Failed to update settings', 'danger')
    
    # Get current settings
    notification_config = dating_app.notification_system.config
    
    return render_template('settings.html', notification_config=notification_config)

@app.route('/logout')
def logout():
    """Log out and clear session."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/api/check_messages/<conversation_id>')
def api_check_messages(conversation_id):
    """API endpoint to check for new messages in a conversation."""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    # Get the timestamp of the last message the client has
    last_timestamp = request.args.get('last_timestamp')
    
    # Get new messages
    messages = dating_app.get_new_messages(conversation_id, last_timestamp)
    
    return jsonify({
        'success': True,
        'messages': messages,
        'count': len(messages)
    })

@app.route('/api/notifications')
def api_notifications():
    """API endpoint to get notifications."""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    # Get notifications
    notifications = dating_app.notification_system.get_notification_history(10)
    
    return jsonify({
        'success': True,
        'notifications': notifications,
        'count': len(notifications)
    })

@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime string."""
    if not value:
        return ''
    
    if isinstance(value, str):
        try:
            dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime(format)
        except:
            return value
    
    return value

if __name__ == '__main__':
    # Create the database if it doesn't exist
    if not os.path.exists(dating_app.assistant.storage.db_path):
        dating_app.assistant.storage.create_tables()
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
