from flask import Flask, render_template, request, session, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import base64

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Function to generate a CAPTCHA string based on a finite state machine (FSM)
def generate_captcha(length=5):
    # Define states and possible transitions for the FSM
    states = {
        "start": ["a", "b", "c", "d", "e"],  # States can have their own set of possible characters
        "vowel": ["a", "e", "i", "o", "u"],  # Transition to vowel-based characters
        "consonant": ["b", "c", "d", "f", "g"],  # Transition to consonant-based characters
        "end": ["x", "y", "z"],  # A different state that may finish the string
    }
    
    state = "start"  # Initial state
    captcha = []
    
    # FSM generation of CAPTCHA string
    for _ in range(length):
        # Select a character based on the current state
        char = random.choice(states[state])
        captcha.append(char)
        
        # Transition between states based on the character
        if state == "start":
            state = "vowel" if char in "aeiou" else "consonant"
        elif state == "vowel":
            state = "consonant"
        elif state == "consonant":
            state = "vowel"
        elif state == "end":
            state = "start"
    
    return ''.join(captcha)

# Function to generate a distorted CAPTCHA image
def generate_captcha_image(captcha_text):
    width, height = 200, 60
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Use a basic font or any TTF file you have
    font = ImageFont.load_default()
    
    # Draw the CAPTCHA text with random positioning, rotation, and color
    for i, char in enumerate(captcha_text):
        x = 40 * i + random.randint(-5, 5)
        y = random.randint(5, 15)
        angle = random.randint(-30, 30)
        draw.text((x, y), char, font=font, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    # Add random noise (dots or lines) to the background
    for _ in range(100):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    # Save image to a byte stream
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Convert to base64 string for embedding in HTML
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return img_base64

@app.route("/", methods=["GET", "POST"])
def home():
    if "captcha" not in session:
        session["captcha"] = generate_captcha()
    if "attempts" not in session:
        session["attempts"] = 0

    captcha = session["captcha"]
    captcha_image = generate_captcha_image(captcha)
    message = ""

    if request.method == "POST":
        user_input = request.form.get("user_input")
        
        if session["attempts"] < 3:
            if user_input == captcha:
                message = "Correct! The input is accepted by the automaton."
                session.pop("captcha")
                session["attempts"] = 0
            else:
                session["attempts"] += 1
                message = f"Incorrect! You have {3 - session['attempts']} attempt(s) remaining."
        else:
            message = "You have exceeded the maximum number of attempts. Click 'Try Again' to reset."

    if request.args.get('reset') == 'true':
        session["captcha"] = generate_captcha()
        session["attempts"] = 0
        return redirect(url_for('home'))

    return render_template("index.html", captcha_image=captcha_image, message=message)

if __name__ == "__main__":
    app.run(debug=True)
