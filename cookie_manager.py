"""Browser cookie management for persistent authentication sessions."""

import re

import streamlit as st
import streamlit.components.v1 as components

from firebase_auth import get_user_profile


def set_auth_cookie(user_id: str):
    """Store user_id in a browser cookie with 7-day expiry."""
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", user_id)
    if not safe_id:
        return
    components.html(
        f"""<script>
        document.cookie = "vitamin_ai_auth={safe_id}; path=/; max-age=604800; SameSite=Lax";
        </script>""",
        height=0,
    )


def _delete_auth_cookie():
    """Remove the auth cookie from the browser."""
    components.html(
        """<script>
        document.cookie = "vitamin_ai_auth=; path=/; max-age=0; SameSite=Lax";
        </script>""",
        height=0,
    )


def try_restore_from_cookie():
    """Attempt to restore an authenticated session from a browser cookie.

    Call once at the top of main(), before the auth-gate check.
    On the very first page load it injects a tiny JS snippet that reads the
    cookie; if one exists the snippet redirects the page with a query-param
    that this function consumes on the resulting reload.
    """
    if st.session_state.get("is_authenticated"):
        return

    # Logout was requested on the previous run -- delete the cookie now.
    if st.session_state.get("_needs_cookie_delete"):
        _delete_auth_cookie()
        del st.session_state["_needs_cookie_delete"]
        return

    # Consume the restore redirect fired by the JS reader below.
    auth_user_id = st.query_params.get("_auth_restore")
    if auth_user_id is not None:
        st.query_params.clear()
        st.session_state._cookie_checked = True
        if auth_user_id:
            user_data = get_user_profile(auth_user_id)
            if user_data:
                st.session_state.is_authenticated = True
                st.session_state.user_data = user_data
                st.rerun()
        return

    # Already injected the reader this session -- nothing more to do.
    if st.session_state.get("_cookie_checked"):
        return

    # First load: inject a zero-height iframe that reads the cookie.
    # If a cookie is found the script navigates to ?_auth_restore=<uid>,
    # which is consumed on the next run above.
    st.session_state._cookie_checked = True
    components.html(
        """<script>
        (function() {
            var m = document.cookie.match(/(?:^|;\\s*)vitamin_ai_auth=([^;]+)/);
            if (m && m[1]) {
                var u = new URL(window.parent.location.href);
                u.searchParams.set('_auth_restore', m[1]);
                window.parent.location.href = u.toString();
            }
        })();
        </script>""",
        height=0,
    )
