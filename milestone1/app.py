import streamlit as st
import time
import re
import db

if 'db_init' not in st.session_state:
    db.init_db()
    st.session_state['db_init'] = True
# --- Validation Utils ---
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    try:
        if re.match(pattern, email):
            return True
    except:
        return False
    return False

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not password.isalnum():
        return False
    return True

# --- Session State ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'user' not in st.session_state:
    st.session_state['user'] = None

# --- Styling ---
st.set_page_config(page_title="Infosys SpringBoard Intern", page_icon="", layout="wide")

st.markdown("""
<style>

/* ===== Background ===== */
.stApp {
    background: linear-gradient(135deg, #141E30, #243B55);
    font-family: 'Segoe UI', sans-serif;
}

/* ===== Titles ===== */
h1 {
    text-align: center;
    color: #ffffff;
    font-size: 2.5rem;
    font-weight: 700;
}

h3 {
    text-align: center;
    color: #dcdcdc;
}

/* ===== Buttons ===== */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 3em;
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    font-weight: bold;
    border: none;
    transition: all 0.3s ease-in-out;
}

.stButton>button:hover {
    transform: scale(1.05);
}

/* ===== Inputs ===== */
.stTextInput>div>div>input {
    border-radius: 10px;
    padding: 10px;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027, #203a43);
}

/* ===== Chat Messages ===== */
.user-msg {
    text-align: right;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    padding: 12px;
    border-radius: 15px 15px 0px 15px;
    margin: 8px;
    display: inline-block;
    max-width: 75%;
}

.bot-msg {
    text-align: left;
    background: linear-gradient(90deg, #ff9966, #ff5e62);
    color: white;
    padding: 12px;
    border-radius: 15px 15px 15px 0px;
    margin: 8px;
    display: inline-block;
    max-width: 75%;
}

</style>
""", unsafe_allow_html=True)

# --- Views ---

def login_page():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("Infosys SpringBoard Intern")
        st.markdown("<h3>Please sign in to continue</h3>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In")

            if submitted:
                # Placeholder (will replace with db.authenticate_user)
                is_locked,wait=db.is_locked(email)
                if is_locked:
                    st.error(f"Account locked. Try again in {wait} seconds.")
                elif db.authenticate_user(email,password):
                    st.session_state['user']=email
                    st.success("Login Successfull!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentialas.")
                

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Forgot Password?"):
                st.session_state['page'] = 'forgot'
                st.rerun()
        with c2:
            if st.button("Create an Account"):
                st.session_state['page'] = 'signup'
                st.rerun()

def signup_page():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("Create Account")

        with st.form("signup_form"):
            username = st.text_input("Username (Required)")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    # Placeholder (will replace with db.register_user)
                    if not is_valid_email(email):
                        st.error("Invalid email format")
                    elif not is_valid_password(password):
                        st.error("Password must be 8+ alphanumeric")
                    elif db.register_user(email,password):
                        st.success("Account created! Please login.")
                        time.sleep(1)
                        st.session_state['page']='login'
                        st.rerun()
                    else:
                        st.error("User already exists.")


        st.markdown("---")
        if st.button("Back to Login"):
            st.session_state['page'] = 'login'
            st.rerun()

def forgot_page():
    st.title("Reset Password")

    email = st.text_input("Enter your registered email")

    if st.button("Send OTP"):
        otp = db.generate_otp(email)
        st.session_state['reset_email'] = email
        st.success(f"OTP Generated: {otp}")  # For demo only
        st.session_state['page'] = 'verify_otp'
        st.rerun()

def dashboard_page():
    with st.sidebar:
        st.title("LLM")
        st.markdown("---")
        if st.button("New Chat", use_container_width=True):
            st.info("Started new chat!")

        st.markdown("### History")
        st.markdown("- Project analysis")
        st.markdown("- NLP")
        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            st.session_state['user'] = None
            st.session_state['page'] = 'login'
            st.rerun()

    st.title("Welcome!")
    st.markdown("### How can I help you today?")

    chat_placeholder = st.empty()

    with chat_placeholder.container():
        st.markdown('<div class="bot-msg">Hello! I am LLM. Ask me anything about LLM!</div>', unsafe_allow_html=True)

    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("Message LLM...", label_visibility="collapsed")
        with col2:
            submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            st.markdown(f'<div class="user-msg">{user_input}</div>', unsafe_allow_html=True)
            st.markdown('<div class="bot-msg">I am a demo bot. I received your message!</div>', unsafe_allow_html=True)

# --- Router ---
if st.session_state['user']:
    dashboard_page()
else:
    if st.session_state['page'] == 'signup':
        signup_page()
    elif st.session_state['page'] == 'forgot':
        forgot_page()
    elif st.session_state['page'] == 'verify_otp':
        verify_otp_page()
    elif st.session_state['page'] == 'new_password':
        new_password_page()
    else:
        login_page()



def verify_otp_page():
    st.title("Verify OTP")

    otp_input = st.text_input("Enter OTP")

    if st.button("Verify"):
        if db.verify_otp(st.session_state['reset_email'], otp_input):
            st.session_state['page'] = 'new_password'
            st.success("OTP Verified")
            st.rerun()
        else:
            st.error("Invalid or Expired OTP")

def new_password_page():
    st.title("Set New Password")

    new_pass = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        if is_valid_password(new_pass):
            db.update_password(st.session_state['reset_email'], new_pass)
            st.success("Password Updated Successfully")
            st.session_state['page'] = 'login'
            st.rerun()
        else:
            st.error("Password must be 8+ alphanumeric")
