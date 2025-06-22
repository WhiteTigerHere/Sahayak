from flask import Flask, render_template,redirect,url_for,request,jsonify,session,flash,make_response
from chatbot import chat
from news import *
from db import *

app = Flask(__name__)

@app.route('/')
def home():
    session["user_id"]=None
    session["chat_id"]=1
    return render_template('firstpage.html')


@app.route('/process_audio', methods=['POST'])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file received"}), 400

    audio_file = request.files["audio"]

    try:
        # Convert OPUS to WAV using ffmpeg
        wav_buffer = io.BytesIO()
        # Use subprocess to call ffmpeg and convert the file
        process = subprocess.Popen(
            ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', 'pipe:1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        # Write the audio data to ffmpeg's stdin
        stdout, stderr = process.communicate(input=audio_file.read())

        if process.returncode != 0:
            return jsonify({"error": f"FFmpeg error: {stderr.decode()}"}), 500
        
        wav_buffer.write(stdout)
        wav_buffer.seek(0)

        # Recognize speech from the converted WAV file
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return jsonify({"text": text})
        except sr.UnknownValueError:
            return jsonify({"text": "Could not understand audio"})
        except sr.RequestError:
            return jsonify({"text": "Error with speech recognition service"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/get_today_events')
def get_today_events():
    user_id = session["user_id"]  # Get user_id from request
    events = get_user_events_today(user_id)  # Fetch today's events
    return jsonify(events)

@app.route('/chatbot')
def chatbot():
    if session["user_id"]!=None:
        response = make_response(render_template("chatbot.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    else:
        flash("You need to login or sign up first.", "error")
        return render_template('newfirstpage.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    return redirect(url_for("chatbot"))

# Events route
@app.route('/events')
def events():
    return render_template('events.html')

# News route
@app.route('/news')
def news():
    print("news lelo")
    return render_template('news2.html')

# Summary route
@app.route('/summary')
def summary():
    return render_template('summary.html')

# Settings route
@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        gender = request.form['gender']
        dob = request.form['dob']

        create_user(username,email,phone,password,dob,gender)

        session["user_id"]=get_user_id(username)

        flash("you registered successfully!", "success")

        return redirect(url_for("chatbot"))

@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if(check_user_password(username,password)):
                session["user_id"]=get_user_id(username)
                return redirect(url_for("chatbot"))
            else:
                flash("Invalid credentials. Please try again.", "error")
                return render_template('newfirstpage.html')
        
# Logout route
@app.route('/logout')
def logout():
    # Logic for logging out the user, for example, session clearing.
    session.clear()
    return redirect(url_for('home'))  # Redirect to home after logout.


@app.route('/get-user-info', methods=['GET'])
def get_user_info():
    """API endpoint to fetch user details."""
    user_id=session["user_id"]
    user_data = get_user(user_id)
    if user_data:
        print(user_data)
        return jsonify(user_data)
    return jsonify({"error": "User not found"}), 404

@app.route("/new_chat", methods=["POST"])
def new_chat():
    """
    Creates a new chat by generating a unique chat ID and updating the session.
    """
    user_id = session.get("user_id")  # Ensure the user is logged in

    if not user_id:
        return jsonify({"error": "User not logged in."}), 400

    # Generate a new unique chat ID
    new_chat_id = get_latest_free_chat_id(user_id)
    # Update the session with the new chat ID
    session["chat_id"] = new_chat_id

    return jsonify({"chat_id": new_chat_id, "message": "New chat started successfully."})


@app.route("/change_chat_id", methods=["POST"])
def change_chat_id():
    """
    Updates the session's chat ID.
    """
    try:
        data = request.json
        new_chat_id = data.get("chat_id")

        if not new_chat_id:
            return jsonify({"error": "Chat ID is required"}), 400

        session["chat_id"] = new_chat_id  # Store in session
        return jsonify({"success": True, "chat_id": new_chat_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_chat_ids", methods=["POST"])
def get_chat_ids():
    """
    Fetches all distinct chat IDs for a given user from the database.
    """
    user_id = session.get("user_id")  # Get user_id from the session
    
    if not user_id:
        return jsonify({"error": "User not logged in."}), 400

    # Fetch distinct chat IDs for the user
    chat_ids = get_distinct_chat_ids(user_id)

    if not chat_ids:
        return jsonify({"error": "No chats found for this user."}), 400

    # Return chat IDs as a list
    return jsonify({"chat_ids": chat_ids})


@app.route("/delete_chat", methods=["POST"])
def delete_chat():
    try:
        data = request.json
        chat_id = data.get("chat_id")
        user_id = session.get("user_id")  # Assuming user is logged in

        if not chat_id or not user_id:
            return jsonify({"error": "Missing chat_id or user_id"}), 400

        # Call the delete_chat_from_db function
        is_deleted = delete_chat_from_db(chat_id, user_id)

        if is_deleted:
            return jsonify({"success": True, "message": "Chat deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete chat"}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500


@app.route('/schedule_event', methods=['POST'])
def handle_schedule_event():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.get_json()
    event_name = data.get('event_name')
    event_date = data.get('event_date')  # Format: YYYY-MM-DD
    start_time = data.get('start_time')  # Format: HH:MM
    end_time = data.get('end_time')      # Format: HH:MM
    color = data.get('color')            # Event color (Hex code, optional)
    description = data.get('description')  # Event description (optional)
    every_year = data.get('everyYear', False)  # Boolean indicating if event is annual

    if not event_name or not event_date or not start_time or not end_time:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Combine date and time into a single timestamp
    try:
        timestamp = f"{event_date} {start_time}:00"
        start_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(f"{event_date} {end_time}:00", "%Y-%m-%d %H:%M:%S")
        duration = (end_datetime - start_datetime).seconds // 60  # Duration in minutes
    except ValueError as e:
        return jsonify({"status": "error", "message": "Invalid date or time format"}), 400

    # Schedule the event
    user_id = session['user_id']
    try:
        schedule_event(user_id, event_name, start_datetime, duration, color, description, every_year)
        return jsonify({"status": "success", "message": "Event scheduled successfully"}), 200
    except mysql.connector.Error as e:
        print(f"Error scheduling event: {e}")
        return jsonify({"status": "error", "message": "Database error occurred while scheduling event"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    # Read the PDF file from the request body
    pdf_bytes = request.data  # Get raw PDF data
    if not pdf_bytes:
        return jsonify({"error": "No PDF data received"}), 400

    text = read_pdf(pdf_bytes)  # Extract text from PDF
    if not text:
        return jsonify({"error": "No text found in PDF"}), 400

    summary = summarize_pdf_doc(text)  # Summarize extracted text
    return jsonify({"summary": summary})

@app.route("/translate_pdf", methods=["POST"])
def translate_pdf():
    # Read the PDF file from the request body
    pdf_bytes = request.data  # Get raw PDF data
    if not pdf_bytes:
        return jsonify({"error": "No PDF data received"}), 400

    text = read_pdf(pdf_bytes)  # Extract text from PDF
    if not text:
        return jsonify({"error": "No text found in PDF"}), 400

    summary=translate_text(text)  # Summarize extracted text
    return jsonify({"summary": summary})

# Notifications route
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

# Profile route
@app.route('/profile')
def profile():
    return render_template('profile.html')

# Assistant route (for your assistant input form)
@app.route('/assistant', methods=['GET','POST'])
async def assistant():
    data = request.get_json('query')
    query=data.get("query")

    # Process the query here (For now, just returning a mock response)
    # You can use your own assistant logic or model here
    response = chat(session['user_id'],session["chat_id"],query)
    
    # Return the response as JSON
    return jsonify({'response': response})

@app.route('/fetchnews', methods=['GET','POST'])
async def fetchnews():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Fetch personalized news using the provided function
    filtered_news = news_scrape()

    if not filtered_news:
        return jsonify({'newslist': [], 'message': 'No relevant news found.'})

    # Format the news items
    newslist = [
        {"title": news["title"], "link": news["link"], "image_url": news["image_link"]}
        for news in filtered_news
    ]

    #print(newslist)

