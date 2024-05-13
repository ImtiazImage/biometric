from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import pyotp #Python library for generating and verifying one-time passwords
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load the pre-trained model
model = load_model('my_model.h5')
 
def load_and_preprocess_image(image):
    """Load an image file and preprocess it for model prediction."""
    img = load_img(image, target_size=(80, 80))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img /= 255.0
    return img

def generate_otp():
    """Generate a One-Time Password using TOTP."""
    totp = pyotp.TOTP('base32secret3232', interval=30) #PyOTP is a Python library for generating and verifying one-time passwords
    return totp.now()

def generate_otp_email(email, otp):
    """Send OTP to the provided email address."""
    sender_email = 'your_email@gmail.com'  # Update with your email address
    sender_password = 'your_password'  # Update with your email password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = 'OTP for Fingerprint Verification'

    body = f'Your OTP for fingerprint verification is: {otp}'
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(message)

# Set up the Streamlit interface
st.title('Fingerprint Verification System')

with st.sidebar:
    st.header('What to do')
    st.sidebar.write("You can upload a clear fingerprint image")

uploaded_file = st.file_uploader("Choose a fingerprint image...", type=['jpg', 'png'])
if uploaded_file is not None:
    # Display the uploaded image with options
    st.image(uploaded_file, caption='Uploaded Fingerprint', use_column_width=True)
    img = load_and_preprocess_image(uploaded_file)

    # Button to initiate the verification process
    if st.button('Verify Fingerprint'):
        # Predict the fingerprint class
        prediction = model.predict(img)
        predicted_class = int(prediction[0][0] > 0.5)  # Assuming 1 is 'Spoof' and 0 is 'Real'

        if predicted_class == 0:
            otp = generate_otp()
            st.session_state['otp'] = otp # Store the OTP in session state
            st.success(f'Fingerprint verified. OTP generated: {otp}')
            # st.balloons()  # Adds a celebratory animation
            
            # send email option starts
            # email = "user@email.com"
            # if generate_otp_email(email, otp):
            #     st.success('OTP sent successfully. Check your email.')
            #send email option ends
        else:
            st.error('Fingerprint Spoofed. Operation terminated.')

    # Input field for OTP
    user_input = st.text_input('Enter OTP:')
    
    # Button to check OTP
    if st.button('Authenticate'):
        stored_otp = st.session_state.get('otp')  # Retrieve the stored OTP from session state
        if user_input == stored_otp:
            st.success('Authentication successful.')
            st.balloons()  # Adds a celebratory animation
        else:
            st.error('Incorrect OTP. Authentication failed.')

with st.expander("Learn More"):
    st.write("""
        fingerprint verification.
    """)
