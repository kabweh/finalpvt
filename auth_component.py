"""
Streamlit component for authentication in the AI Tutor application.
Provides UI elements for login, registration, and subscription management.
"""
import streamlit as st
from typing import Dict, Any, Optional

# Use relative import within the package
from auth_manager import AuthManager

class AuthComponent:
    """
    Streamlit component for handling authentication in the AI Tutor application.
    """
    
    def __init__(self, auth_manager: AuthManager):
        """
        Initialize the authentication component.
        
        Args:
            auth_manager: Instance of AuthManager to handle authentication
        """
        self.auth_manager = auth_manager
    
    def render_auth_forms(self) -> None:
        """
        Render the authentication forms (login and registration).
        """
        # Create tabs for login and registration
        login_tab, register_tab = st.tabs(["Login", "Sign Up"])
        
        # Login form
        with login_tab:
            with st.form("login_form"):
                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                submitted = st.form_submit_button("Login")
                if submitted:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        # Attempt login
                        result = self.auth_manager.login_user(username, password)
                        
                        if result["success"]:
                            # Store user in session state
                            st.session_state.user = result["user"]
                            st.success("Login successful!")
                            st.experimental_rerun()
                        else:
                            st.error(result["message"])
        
        # Registration form
        with register_tab:
            with st.form("register_form"):
                st.subheader("Sign Up")
                st.info("Registration requires an invite code. Please contact an administrator if you don\\'t have one.")
                
                new_username = st.text_input("Username", key="reg_username")
                new_password = st.text_input("Password", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email (optional)")
                invite_token = st.text_input("Invite Code")
                
                submitted = st.form_submit_button("Sign Up")
                if submitted:
                    # Validate inputs
                    if not new_username or not new_password:
                        st.error("Please enter both username and password.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif not invite_token:
                        st.error("Invite code is required.")
                    else:
                        # Validate invite token
                        token_validation = self.auth_manager.validate_invite_token(invite_token)
                        
                        if not token_validation["success"]:
                            st.error(token_validation["message"])
                        else:
                            # Attempt registration
                            result = self.auth_manager.register_user(
                                new_username, 
                                new_password, 
                                email, 
                                invite_token
                            )
                            
                            if result["success"]:
                                st.success("Registration successful! You can now log in.")
                                # Consider automatically logging in or just prompting
                                # st.session_state.auth_tab = "login" # May not work reliably
                                st.experimental_rerun()
                            else:
                                st.error(result["message"])
    
    def render_auth_status(self) -> None:
        """
        Render the authentication status in the sidebar.
        """
        if st.session_state.get("user"):
            user = st.session_state.user
            
            st.write(f"Logged in as: **{user["username"]}**")
            
            # Subscription status
            if user.get("subscription_active", False):
                st.success("Subscription: Active")
                if user.get("subscription_expires"):
                    st.write(f"Expires: {user["subscription_expires"]}")
            else:
                st.warning("Subscription: Inactive")
                # Optionally add a link/button to subscribe
                # if st.button("Subscribe Now"):
                #     # Navigate to subscription page or show modal
                #     pass 
            
            # Logout button
            if st.button("Logout"):
                # Clear user-specific session state
                keys_to_clear = [k for k in st.session_state.keys() if k not in ["initialized", "current_page"]]
                for key in keys_to_clear:
                    del st.session_state[key]
                st.session_state.user = None # Ensure user is cleared
                st.experimental_rerun()
        else:
            st.info("Not logged in")
            # Optionally add login/signup buttons here if not using tabs elsewhere
            # if st.button("Login / Sign Up"):
            #     st.session_state.current_page = "Home" # Or a dedicated auth page
            #     st.experimental_rerun()

    
    def render_subscription_management(self) -> None:
        """
        Render the subscription management section (Placeholder).
        This would typically be on a separate Account or Billing page.
        """
        st.header("Subscription Management")
        
        # Check if user is logged in
        if not st.session_state.get("user"):
            st.warning("Please log in to manage your subscription.")
            return
        
        user = st.session_state.user
        
        # Display current subscription status
        if user.get("subscription_active", False):
            st.success("Your subscription is currently active.")
            if user.get("subscription_expires"):
                st.write(f"Your subscription expires on: {user["subscription_expires"]}")
            
            # Renewal/Management options (placeholder)
            st.subheader("Manage Subscription")
            st.write("Contact an administrator or visit the billing portal (link placeholder) to manage your subscription.")
            # Example: st.link_button("Go to Billing Portal", "https://your-billing-portal.com")
        else:
            st.warning("You don\'t have an active subscription.")
            
            # Subscription options (placeholder)
            st.subheader("Subscription Options")
            st.write("Contact an administrator or choose a plan below to activate your subscription.")
            
            # In a real application, this would integrate with Stripe Checkout or similar
            # For now, we\'ll just have a placeholder button
            if st.button("Subscribe (Test Mode)"):
                # Activate subscription (placeholder logic)
                result = self.auth_manager.activate_subscription(user["id"])
                
                if result["success"]:
                    # Update user in session state directly
                    st.session_state.user["subscription_active"] = True
                    st.session_state.user["subscription_expires"] = result["expires_at"]
                    
                    st.success("Subscription activated successfully!")
                    st.experimental_rerun()
                else:
                    st.error(result["message"])

