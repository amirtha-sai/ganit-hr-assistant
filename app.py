import streamlit as st
import requests
import json

# =====================================================
# CONFIG
# =====================================================

API_URL = "https://dtl1p82dzl.execute-api.us-east-1.amazonaws.com/dev/chat"

# =====================================================
# PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="💼",
    layout="wide"
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("💼 HR Assistant")

    employee_id = st.text_input(
        "Employee ID",
        value="EMP001"
    )

    st.markdown("---")

    st.markdown("""
    ### What you can ask

    • Leave policies  
    • Reimbursements  
    • Benefits & insurance  
    • Travel policy  
    • Workplace conduct  
    • HR guidelines  
    • Policy references  
    """)

    st.markdown("---")

    st.caption("Built with AWS Bedrock & OpenSearch")

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# HEADER
# =====================================================

st.title("HR Policy Assistant")

st.caption(
    "Get quick answers from company HR policies and guidelines."
)

# =====================================================
# CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================================
# USER INPUT
# =====================================================

question = st.chat_input(
    "Ask an HR-related question..."
)

# =====================================================
# HANDLE QUESTION
# =====================================================

if question:

    # -------------------------------------------------
    # USER MESSAGE
    # -------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # -------------------------------------------------
    # ASSISTANT RESPONSE
    # -------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Checking policies..."):

            try:

                payload = {
                    "question": question,
                    "employee_id": employee_id
                }

                response = requests.post(
                    API_URL,
                    json=payload
                )

                # -------------------------------------------------
                # PARSE RESPONSE
                # -------------------------------------------------

                result = response.json()

                # Lambda may return nested body
                if "body" in result:

                    if isinstance(result["body"], str):
                        result = json.loads(result["body"])
                    else:
                        result = result["body"]

                # -------------------------------------------------
                # EXTRACT RESPONSE
                # -------------------------------------------------

                answer = result.get(
                    "answer",
                    "No response received."
                )

                citations = result.get(
                    "citations",
                    []
                )

                # -------------------------------------------------
                # DISPLAY ANSWER
                # -------------------------------------------------

                st.markdown(answer)

                # -------------------------------------------------
                # POLICY REFERENCES
                # -------------------------------------------------

                if citations:

                    st.markdown("---")
                    st.markdown("### Referenced Policies")

                    for citation in citations:

                        chunk_number = citation.get(
                            "chunk_number",
                            "N/A"
                        )

                        policy_name = citation.get(
                            "policy_name",
                            "Unknown Policy"
                        )

                        page = citation.get(
                            "page",
                            "N/A"
                        )

                        section = citation.get(
                            "section",
                            "N/A"
                        )

                        score = citation.get(
                            "score",
                            0
                        )

                        text = citation.get(
                            "text",
                            ""
                        )

                        # -----------------------------------------
                        # SOURCE CARD
                        # -----------------------------------------

                        with st.expander(
                            f"{policy_name} • Chunk {chunk_number}"
                        ):

                            st.markdown(f"""
**Section:** {section}  
**Page:** {page}  
**Match Score:** {round(score, 3)}
""")

                            st.markdown("---")

                            st.write(text)

                else:

                    st.info(
                        "No policy references available."
                    )

                # -------------------------------------------------
                # SAVE CHAT
                # -------------------------------------------------

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                error_message = f"Something went wrong: {str(e)}"

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
